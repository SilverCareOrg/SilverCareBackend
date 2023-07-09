from django.urls import path
from .views import add_to_cart,\
    get_cart,\
    checkout_cart,\
    remove_from_cart

urlpatterns = [
    path('add_to_cart', add_to_cart),
    path('get_cart', get_cart),
    path('checkout_cart', checkout_cart),
    path('remove_from_cart', remove_from_cart),
]