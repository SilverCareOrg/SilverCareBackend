from django.urls import path
from .views import CreateServiceView, get_all_services

urlpatterns = [
    path('create_service/', CreateServiceView.as_view(), name='create_service'),
    path('get_all_services', get_all_services),
]