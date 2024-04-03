from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from services.models import Service, ServiceImage
import json
from django.http import HttpResponse, JsonResponse
from login.utils import get_user_from_token_request
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
import os
from .models import Cart
import environ
from services.models import CartService, Service, PurchasedService, ServiceOption
from s3.s3_client import S3Client

env = environ.Env()
environ.Env.read_env()

@api_view(["POST"])
def add_to_cart(request):
    user = get_user_from_token_request(request)

    # Check if user cart has been created in the database
    if user.cart is None:
        cart = Cart.objects.create(user=user)
        cart.save()

    data = json.loads(request.body)

    # Get the service to be added to cart
    base_service = Service.objects.get(id=data['service_id'])

    # Get the option to be added to cart
    option = ServiceOption.objects.get(id=data['option_id'])

    # Get the number of participants
    number_of_participants = data['number_of_participants']

    cart_service = CartService.objects.create(cart=user.cart,
                                              base_service=base_service,
                                              option=option,
                                              number_of_participants=number_of_participants)

    user.cart.save()
    base_service.save()
    cart_service.save()
    option.save()
    user.save()
    return JsonResponse("Added to cart successfully!", safe = False, status = 200)

def serialize_cart_services(cart_services):
    cart_services_json = []
    
    for cart_service in cart_services:
        service_images = ServiceImage.objects.filter(service = cart_service.base_service)
        
        cart_services_json.append({
            "base_service_id": cart_service.base_service.id,
            "service_id": cart_service.id,
            "service_name": cart_service.base_service.name,
            "option_name": cart_service.option.name,
            "option_details": {
                    "price": cart_service.option.price,
                    "duration": cart_service.option.duration,
                    "date": cart_service.option.date,
                    "location": cart_service.option.location,
                    "map_location": cart_service.option.map_location.serialize() if cart_service.option.map_location else None,
                    "rating": cart_service.option.rating,
                    "number_ratings": cart_service.option.number_ratings,
                    "details": cart_service.option.details,
                    "city": cart_service.option.city,
                    "county": cart_service.option.county,
                    "id": cart_service.option.id
                },
            "price": cart_service.option.price * cart_service.number_of_participants,
            "number_of_participants": cart_service.number_of_participants,
            "service_image_path": [S3Client.download_image(env('SILVERCARE_AWS_S3_SERVICES_SUBDIR'), svc_img.id) for svc_img in service_images],
        })
        
    return cart_services_json

@api_view(["DELETE"])
def remove_from_cart(request):
    user = get_user_from_token_request(request)
    data = json.loads(request.body)
    cart_service = CartService.objects.get(id=data['id'])
    cart_service.delete()
    user.cart.save()
    
    cart_services = user.cart.cartservice_set.all()
    cart_services_json = serialize_cart_services(cart_services)
    
    return JsonResponse(cart_services_json, safe = False, status = 200)    
    
    
@api_view(["GET"])
def get_cart(request):
    user = get_user_from_token_request(request)
    cart = user.cart
    cart_services = cart.cartservice_set.all()
    cart_services_json = serialize_cart_services(cart_services)
    
    return JsonResponse(cart_services_json, safe = False, status = 200)


