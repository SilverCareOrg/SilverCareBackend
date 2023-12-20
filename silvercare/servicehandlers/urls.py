from django.urls import path
from .views import get_services, get_services_by_organiser, delete_service, get_service_by_id

urlpatterns = [
    path('get_services', get_services),
    path('get_services_by_organiser', get_services_by_organiser, name = 'get_services_by_organiser'),
    path('delete_service', delete_service, name = 'delete_service'),
    path('get_service_by_id', get_service_by_id, name = 'get_service_by_id'),
]