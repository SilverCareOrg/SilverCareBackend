from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import jwt
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
import datetime
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
import json
from .utils import generate_jwt_token, get_user_from_token_request

@csrf_exempt
@api_view(["POST"])
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        username = data['email']
        password = data['password']
        
        print(username)
        print(password)
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            token = generate_jwt_token(user, username)
            user.is_active = True
            user.save()
          
            response = JsonResponse(token, status = 200)
            expiration = datetime.datetime.utcnow() + datetime.timedelta(days=30)
            response.set_cookie('token', token, 
                                expires = expiration,
                                httponly = False,
                                samesite='None')
            response['Access-Control-Allow-Credentials'] = True

            return response
        else:
            return HttpResponse("Failed to log in!" + str(username) + " " + str(password), status = 400)
    return HttpResponse("Failed to log in!")

@api_view(["GET"])
def check_permissions(request):
    user = get_user_from_token_request(request)

    res = {
        "isAdmin": True
    }

    return JsonResponse(res, status = 200)    
    