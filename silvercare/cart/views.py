from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from services.models import Service
import json
from django.http import HttpResponse, JsonResponse
from login.utils import get_user_from_token_request
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
import os
from .models import Cart
from services.models import CartService, Service, PurchasedService

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
    
    if user.cart.cartservice_set.all().filter(base_service=base_service).exists():
        return JsonResponse("Object already added to cart!", safe = False, status = 200)

    cart_service = CartService.objects.create(cart=user.cart,
                                              base_service=base_service,
                                              senior_name=data['senior_name'],
                                              adult_name=data['adult_name'],
                                              phone_number=data['phone_number'],
                                              companion=data['companion'],
                                              email=data['email'])

    user.cart.save()
    base_service.save()
    cart_service.save()
    user.save()
    print(cart_service)
    return JsonResponse("Added to cart successfully!", safe = False, status = 200)

def serialize_cart_services(cart_services):
    cart_services_json = []
    
    for cart_service in cart_services:
        cart_services_json.append({
            "service_id": cart_service.id,
            "service_name": cart_service.base_service.name,
            "service_price": cart_service.base_service.price,
            "service_image_path": cart_service.base_service.image,
            "senior_name": cart_service.senior_name,
            "adult_name": cart_service.adult_name,
            "phone_number": cart_service.phone_number,
            "companion": cart_service.companion,
            "email": cart_service.email
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


