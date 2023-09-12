from django.urls import path
from .views import create_checkout_session,\
    stripe_webhook,\
    check_payment_status

urlpatterns = [
    path('create_checkout_session', create_checkout_session),
    path('stripe_webhook', stripe_webhook),
    path('check_payment_status/<str:checkout_session_id>', check_payment_status),
]