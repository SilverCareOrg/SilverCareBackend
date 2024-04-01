from django.core.mail import send_mail
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse
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
import json
from services.models import Service

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

def send_db_user_email_message(cart_services, user, user_email, metadata):
    introduction = ""
    SC_introduction = f"<h2>Email client: {user.email}<h2>"
    with open('./emailApp/components/introduction.txt', 'r', encoding='utf-8') as f:
        introduction = f.read()
        introduction = introduction.replace("[Nume Client]", user.username)
        introduction = introduction.replace("[Număr Comandă]", metadata["cmd"])
        introduction = introduction.replace("[Data Comenzii]", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        
        SC_introduction += "<h3>Detalii comandă" + introduction.split("Detalii comandă")[1]
        
    footer = ""
    with open('./emailApp/components/footer.txt', 'r', encoding='utf-8') as f:
        footer = f.read()
    
    service_template = ""
    with open('./emailApp/components/service.txt', 'r', encoding='utf-8') as f:
        service_template = f.read()
    
    activities = []
    total_price = 0
    for service in cart_services:
        base_service = service.base_service
        option = service.option

        price = "Gratis" if option.price == '0' or option.price == "free" else option.price

        html_service = service_template.replace("[Nume Serviciu]", base_service.name)
        html_service = html_service.replace("[Preț Serviciu]", str(price))
        html_service = html_service.replace("[Organizator]", base_service.organiser)
        html_service = html_service.replace("[Număr participanți]", str(service.number_of_participants))

        total_price += float(option.price) * service.number_of_participants if option.price != 'free' else 0
        activities.append(html_service)
    
    introduction = introduction.replace("[Total Comandă]", str(total_price))
    
    alternative_plain_message = ""
    
    # Send email to client
    subject = 'Confirmarea comenzii tale'
    message = "<html><body>" +\
                introduction +\
                "<ul>" +\
                "".join(activities) +\
                "</ul>" +\
                footer +\
                "</body></html>"
    
    recipient_list = [user_email]
    send_mail(subject, alternative_plain_message, settings.DEFAULT_FROM_EMAIL, recipient_list, html_message=message)
    
    # Send email to SilverCare
    subject = "Comandă nouă"
    message = "<html><body>" +\
                SC_introduction +\
                "<ul>" +\
                "".join(activities) +\
                "</ul>"
    recipient_list = ["hello@thesilvercare.com"]
    # send_mail(subject, alternative_plain_message, settings.DEFAULT_FROM_EMAIL, recipient_list, html_message=message)

def checkout_send_email(user, user_email, metadata):
    # user = get_user_from_token_request(request)
    cart = user.cart
    cart_services = cart.cartservice_set.all()
    
    if len(cart_services) == 0:
        return JsonResponse({"message":"Nu exista servicii in cos!"}, status = 200)

    send_db_user_email_message(cart_services, user, user_email, metadata)

    # transfer_cart_to_purchase(cart_services, user)

def send_guest_user_email_message(command_email, cart_services):
    introduction = ""
    SC_introduction = f"<h2>Email client: {command_email}<h2>"
    with open('./emailApp/components/introduction.txt', 'r', encoding='utf-8') as f:
        introduction = f.read()
        introduction = introduction.replace("[Nume Client]", "cumpărător")
        introduction = introduction.replace("[Număr Comandă]",generate_command_number())
        introduction = introduction.replace("[Data Comenzii]", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        
        SC_introduction += "<h3>Detalii comandă" + introduction.split("Detalii comandă")[1]
        
    footer = ""
    with open('./emailApp/components/footer.txt', 'r', encoding='utf-8') as f:
        footer = f.read()
    
    service_template = ""
    with open('./emailApp/components/service.txt', 'r', encoding='utf-8') as f:
        service_template = f.read()
    
    activities = []
    total_price = 0
    for service in cart_services:
        base_service = Service.objects.get(id=service["service_id"])
        price = "Gratis" if base_service.price == 'free' else base_service.price

        html_service = service_template.replace("[Nume Serviciu]", base_service.name)
        html_service = html_service.replace("[Preț Serviciu]", price)
        html_service = html_service.replace("[Organizator]", base_service.organiser)
        html_service = html_service.replace("[Nume Senior]", service["senior_name"])
        html_service = html_service.replace("[Nume Adult]", service["adult_name"])
        html_service = html_service.replace("[Însoțitor]", service["companion"])
        html_service = html_service.replace("[Număr de telefon]", service["phone_number"])
        
        total_price += float(base_service.price) if base_service.price != 'free' else 0
        activities.append(html_service)
    
    introduction = introduction.replace("[Total Comandă]", str(total_price))
    
    alternative_plain_message = ""
    
    # Send email to client
    subject = 'Confirmarea comenzii tale'
    message = "<html><body>" +\
                introduction +\
                "<ul>" +\
                "".join(activities) +\
                "</ul>" +\
                footer +\
                "</body></html>"
    
    recipient_list = [command_email]
    send_mail(subject, alternative_plain_message, settings.DEFAULT_FROM_EMAIL, recipient_list, html_message=message)
    
    # Send email to SilverCare
    subject = "Comandă nouă"
    message = "<html><body>" +\
                SC_introduction +\
                "<ul>" +\
                "".join(activities) +\
                "</ul>"
    recipient_list = ["hello@thesilvercare.com"]
    # send_mail(subject, alternative_plain_message, settings.DEFAULT_FROM_EMAIL, recipient_list, html_message=message)


# @api_view(['POST'])
def guest_checkout_send_email(services, email):
    # data = json.loads(request.body)["checkout_data"]

    # email = data["email"]
    # services = data["services"]

    send_guest_user_email_message(email, services)
    
    return JsonResponse('Email sent', safe = False, status = 200)

