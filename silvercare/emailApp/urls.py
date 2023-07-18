from django.urls import path
from .views import checkout_send_email

urlpatterns = [
    path('checkout_send_email', checkout_send_email),
]