from django.urls import path
from .views import login, check_permissions
from .serializers import JWTSerializer

urlpatterns = [
    path('login', login),
    path('check_permissions', check_permissions),
    path('jwt_serializer', JWTSerializer),
]