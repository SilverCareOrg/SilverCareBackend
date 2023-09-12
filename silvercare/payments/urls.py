from django.urls import path
from .views import create_checkout_session,\
    stripe_webhook

urlpatterns = [
    path('create_checkout_session', create_checkout_session),
    path('stripe_webhook', stripe_webhook),
]