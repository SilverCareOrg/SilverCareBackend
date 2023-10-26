from django.urls import path
from .views import get_users, get_users_by_email, set_staff, unset_staff

urlpatterns = [
    path('get_users/', get_users, name = 'get_users'),
    path('get_users_by_email/', get_users_by_email, name = 'get_users_by_email'),
    path('set_staff', set_staff, name = 'set_staff'),
    path('unset_staff', unset_staff, name = 'unset_staff')
]