from django.core.mail import send_mail
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from services.models import PurchasedService
from login.utils import get_user_from_token_request
import environ
import time
from datetime import datetime
import string
import random as rd
import socket

# Environment variables
env = environ.Env()
environ.Env.read_env()

"""
    MAIN WORKFLOW

    subject = 'Hello'
    message = 'This is a test email.'
    recipient_list = ['some@mail.com']

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
    return HttpResponse('Email sent', status = 200)
"""

def generate_command_number():
    timestamp = int(time.time())
    random_part = ''.join(rd.choices(string.ascii_uppercase + string.digits, k=6))
    command_number = f'CMD{timestamp}{random_part}'
    return command_number

def transfer_cart_to_purchase(cart_services, user):
    for service in cart_services:
        purchased_service = PurchasedService.objects.create(
            base_service=service.base_service,
            user=user,
            senior_name=service.senior_name,
            adult_name=service.adult_name,
            companion=service.companion,
            phone_number=service.phone_number,
            email=service.email,
        )
        
    cart_services.delete()
    user.save()

@api_view(['POST'])
def checkout_send_email(request):
    res = socket.getaddrinfo('smtp.gmail.com', 587, socket.AF_INET, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
    print(res)
    
    user = get_user_from_token_request(request)
    cart = user.cart

    introduction = ""
    with open('./emailApp/components/introduction.txt', 'r', encoding='utf-8') as f:
        introduction = f.read()
        introduction = introduction.replace("[Nume Client]", user.username)
        introduction = introduction.replace("[Număr Comandă]",generate_command_number())
        introduction = introduction.replace("[Data Comenzii]", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        
    footer = ""
    with open('./emailApp/components/footer.txt', 'r', encoding='utf-8') as f:
        footer = f.read()
    
    service_template = ""
    with open('./emailApp/components/service.txt', 'r', encoding='utf-8') as f:
        service_template = f.read()
    
    activities = []
    total_price = 0
    for service in cart.cartservice_set.all():
        base_service = service.base_service
        price = "Gratis" if base_service.price == 'free' else base_service.price

        html_service = service_template.replace("[Nume Serviciu]", base_service.name)
        html_service = html_service.replace("[Preț Serviciu]", price)
        html_service = html_service.replace("[Organizator]", base_service.organiser)
        html_service = html_service.replace("[Nume Senior]", service.senior_name)
        html_service = html_service.replace("[Nume Adult]", service.adult_name)
        html_service = html_service.replace("[Însoțitor]", service.companion)
        
        total_price += float(base_service.price) if base_service.price != 'free' else 0
        activities.append(html_service)
    
    introduction = introduction.replace("[Total Comandă]", str(total_price))
    
    subject = 'Confirmarea comenzii tale'
    message = "<html><body>" +\
                introduction +\
                "<ul>" +\
                "".join(activities) +\
                "</ul>" +\
                footer +\
                "</body></html>"

    alternative_plain_message = ""
    recipient_list = [user.email]
    send_mail(subject, alternative_plain_message, settings.DEFAULT_FROM_EMAIL, recipient_list, html_message=message)
    transfer_cart_to_purchase(cart.cartservice_set.all(), user)
    return HttpResponse('Email sent', status = 200)

