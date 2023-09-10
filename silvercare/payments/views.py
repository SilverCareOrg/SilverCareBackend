from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from django.shortcuts import redirect
import stripe
import json
import environ
from rest_framework.decorators import api_view
from login.utils import get_user_from_token_request
from services.models import Service, CartService

env = environ.Env()
environ.Env.read_env()

stripe.api_key = env('STRIPE_SECRET_KEY')
BASE_URL=env('BASE_URL')

@api_view(['POST'])
def create_checkout_session(request):
    data = json.loads(request.body)
    
    if data["isGuest"] == True:
        services = data["services"]      
    else:
        user = get_user_from_token_request(request)
        cart = user.cart
        services = cart.cartservice_set.all()
        
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
            locale="ro"
        )
    except Exception as e:
        return HttpResponse("Error creating checkout session: " + str(e), status = 500)

    return JsonResponse({"id":checkout_session.id}, status=200)