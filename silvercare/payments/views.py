from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
import stripe
from stripe import Webhook
import json
import environ
from rest_framework.decorators import api_view
from login.utils import get_user_from_token_request
from services.models import Service, CartService
from .models import Payment, Checkout, TemporaryGuestMetadata
from django.contrib.auth.models import User
import time
from emailApp.views import checkout_send_email, guest_checkout_send_email
from services.models import PurchasedService

env = environ.Env()
environ.Env.read_env()

stripe.api_key = env('STRIPE_SECRET_KEY')
BASE_URL=env('BASE_URL')

def checkout_cart(user, payment_obj):
    cart = user.cart
    cart_services = cart.cart_services.all()
    
    for cart_service in cart_services:
        purchased_service = PurchasedService.objects.create(user=user,
                                                            base_service=cart_service.base_service,
                                                            senior_name=cart_service.senior_name,
                                                            adult_name=cart_service.adult_name,
                                                            phone_number=cart_service.phone_number,
                                                            companion=cart_service.companion,
                                                            email=cart_service.email,
                                                            payment = payment_obj )
        purchased_service.save()
    
    cart.cart_services.all().delete()
    

@api_view(['POST'])
def create_checkout_session(request):
    data = json.loads(request.body)

    if data["isGuest"] == True:
        services = data["services"]   
        tmp_obj = TemporaryGuestMetadata.objects.create(metadata=json.dumps(services))
           
        metadata = {'user_id': 'guest',
                    'temporary_guest_metadata': tmp_obj.id}
    else:
        user = get_user_from_token_request(request)
        cart = user.cart
        services = cart.cartservice_set.all()

        metadata = {'user_id': user.id}

        if len(services) == 0:
            return HttpResponse({"message":"Nu exista servicii in cos!"}, status = 200)

    line_items = []    
    for service in services:
        if isinstance(service, CartService):
            base_service = service.base_service
        else:
            base_service = Service.objects.get(id=service["service_id"])
        price = 0 if base_service.price == 'free' else base_service.price

        line_items.append({
            "price_data": {
                    "currency": "ron",
                    "unit_amount": int(round(float(price), 2) * 100),
                    "product_data": {
                        "name": base_service.name,
                    },
                },
            "quantity": 1,
        })
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=BASE_URL + '/checkout-success',
            cancel_url=BASE_URL + '/checkout-fail',
            automatic_tax={'enabled': True},
            locale="ro",
            metadata=metadata
        )
    except Exception as e:
        return HttpResponse("Error creating checkout session: " + str(e), status = 500)
    
    return JsonResponse({"id":checkout_session.id}, status=200)

def match_checkout_payment(payment_obj, checkout_obj):
    metadata = json.loads(checkout_obj.metadata)
    if metadata["user_id"] == "guest":
        payment_obj.user = None
        tmp_obj = TemporaryGuestMetadata.objects.get(id=metadata["temporary_guest_metadata"])
        
        guest_checkout_send_email(json.loads(tmp_obj.metadata), checkout_obj.checkout_email)
    else:
        user = User.objects.get(id=metadata["user_id"])

        if user is None:
            return JsonResponse({'status': 'Internal error at payment_intent.succeeded'}, status=500)

        payment_obj.user = user
        
        checkout_send_email(user, checkout_obj.checkout_email)
        checkout_cart(user, payment_obj)

    payment_obj.save()

@csrf_exempt
def stripe_webhook(request):
    payload = json.loads(request.body.decode('utf-8'))

    secret_key = env('STRIPE_WEBHOOK_KEY')

    try:
        event = stripe.Event.construct_from(
            payload, stripe.api_key
        )
    except ValueError as e:
        return JsonResponse(status=400)

    if event.type == 'payment_intent.succeeded':
        payment_intent_data = event.data.get('object', {})
        payment_intent_id = payment_intent_data.get('id')
        
        if not payment_intent_id:
            return JsonResponse({'status': 'Payment intent data not found'}, status=400)

        payment_obj = Payment.objects.create(
            payment_intent_id=payment_intent_id,
            amount=payment_intent_data.get('amount'),
            currency=payment_intent_data.get('currency'),
            idempotency_request_id=event.get('request', {}).get('id'),
            idempotency_key=event.get('request', {}).get('idempotency_key'),
        )

        try:
            checkout_obj = Checkout.objects.get(payment_intent_id=payment_intent_id)
            match_checkout_payment(payment_obj, checkout_obj)
        except Checkout.DoesNotExist:
            checkout_obj = None
    elif event.type == 'checkout.session.completed':
        payment_intent_data = event.data.get('object', {})
        payment_intent_id = payment_intent_data.get('payment_intent')

        checkout_obj = Checkout.objects.create(payment_intent_id=payment_intent_id,
                                               metadata=json.dumps(payment_intent_data.get('metadata')),
                                               checkout_email = payment_intent_data.get('customer_details', {}).get('email'))

        if checkout_obj is None:
            return JsonResponse({'status': 'Internal error at checkout.session.completed'}, status=500)

        try:
            payment_obj = Payment.objects.get(payment_intent_id=payment_intent_id)
            match_checkout_payment(payment_obj, checkout_obj)
        except Payment.DoesNotExist:
            payment_obj = None

    elif event.type == 'payment_intent.payment_failed':
        pass
    else:
        pass

    return JsonResponse({'status': 'Webhook received successfully'}, status=200)

@api_view(['GET'])
def check_payment_status(request, checkout_session_id):
    try:
        checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)

        if checkout_session.payment_status == "paid":
            return JsonResponse({"status": "completed"}, status=200)

        return JsonResponse({"status": "pending"}, status=200)

    except stripe.error.StripeError as e:
        return JsonResponse({"error": str(e)}, status=500)