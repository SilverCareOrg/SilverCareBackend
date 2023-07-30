from django.urls import path
from .views import login, check_permissions, signup,\
    get_user_role#,\
    # httponly_get_test,\
    # httponly_post_test
from .serializers import JWTSerializer

urlpatterns = [
    path('login', login),
    path('signup', signup),
    path('check_permissions', check_permissions),
    path('get_user_role', get_user_role),
    # path('httponly_get_test', httponly_get_test),
    # path('httponly_post_test', httponly_post_test),
    path('jwt_serializer', JWTSerializer),
]