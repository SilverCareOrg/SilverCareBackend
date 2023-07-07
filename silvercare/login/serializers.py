from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import datetime

class JWTSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user, username):
        token = super().get_token(user)
        current_time = datetime.datetime.utcnow()
        expiration_time = datetime.datetime.utcnow() +\
                    datetime.timedelta(days=30)
        
        token['exp'] = expiration_time
        token['login_time'] = current_time.strftime('%Y-%m-%d %H:%M:%S')
        token['username'] = username
        token['user_id'] = user.id

        return token