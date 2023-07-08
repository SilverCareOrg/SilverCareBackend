from django.urls import path
from .views import CreateServiceView, get_all_services,\
    get_homepage_random_services,\
    get_homepage_best_selling_products

urlpatterns = [
    path('create_service/', CreateServiceView.as_view(), name='create_service'),
    path('get_all_services', get_all_services),
    path('get_homepage_random_services', get_homepage_random_services),
    path('get_homepage_best_selling_products', get_homepage_best_selling_products),
]