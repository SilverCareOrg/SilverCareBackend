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
from .models import Payment, Checkout
from django.contrib.auth.models import User
import time

env = environ.Env()
environ.Env.read_env()

stripe.api_key = env('STRIPE_SECRET_KEY')
BASE_URL=env('BASE_URL')

@api_view(['POST'])
def create_checkout_session(request):
    data = json.loads(request.body)

    if data["isGuest"] == True:
        services = data["services"]      
        metadata = {'user_id': 'guest'}
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
    else:
        user = User.objects.get(id=metadata["user_id"])

        if user is None:
            return JsonResponse({'status': 'Internal error at payment_intent.succeeded'}, status=500)

        payment_obj.user = user

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

        checkout_obj = Checkout.objects.create(payment_intent_id=payment_intent_id, metadata=json.dumps(payment_intent_data.get('metadata')))

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
