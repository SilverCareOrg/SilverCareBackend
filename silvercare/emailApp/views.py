from django.core.mail import send_mail
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def send_email(request):
    subject = 'Hello'
    message = 'This is a test email.'
    recipient_list = ['avramcristianstefan@gmail.com']

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
    return HttpResponse('Email sent', status = 200)

def test_func(request):
    pass