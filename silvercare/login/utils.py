import jwt
from django.contrib.auth.models import User
import datetime
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import JWTSerializer
from rest_framework.exceptions import AuthenticationFailed

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = JWTSerializer

def get_user_from_token_request(request):
    token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
    if not token:
        raise AuthenticationFailed('Unauthenticated')

    id = jwt.decode(token, key = 'SECRET_KEY', algorithms = ['HS256'])['user_id']

    try:
        user = User.objects.get(id = id)

        if not user.is_active:
            user.is_active = True
    except User.DoesNotExist:
        raise AuthenticationFailed('User not found')
    
    return user

def generate_jwt_token(user, username):
    refresh = JWTSerializer.get_token(user, username)

    token = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

    return token

def generate_JWT(employee):
    # set expiring time
    expiration_time = datetime.datetime.utcnow() +\
        datetime.timedelta(days=30)
    current_time = datetime.datetime.utcnow()
    
    manager_first_name = employee.manager.first_name if employee.manager != None else None
    manager_last_name = employee.manager.last_name if employee.manager != None else None

    payload = {
        "id": employee.user.id,
        "first_name" : employee.first_name,
        "last_name" : employee.last_name,
        "manager" : employee.manager.first_name +
                    employee.manager.last_name,
        "role" : employee.role,
        "exp": expiration_time,
        "login_time": current_time.strftime('%Y-%m-%d %H:%M:%S')
    }

    token = jwt.encode(payload, 'SECRET_KEY', algorithm='HS256')

    return {"token" : token}