from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
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
from cart.models import Cart

@csrf_exempt
@api_view(["POST"])
def login(request):
	if request.method == 'POST':
		data = json.loads(request.body)

		email = data['email']
		password = data['password']

		if not User.objects.filter(email=email).exists():
			return HttpResponse("Failed to log in!", status = 400)

		shadow_user = User.objects.get(email=email)
		user = authenticate(request, username=shadow_user.username, password=password)

		if user is not None:
			token = generate_jwt_token(user, email)
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
			return JsonResponse("Failed to log in!", safe = False, status = 400)
	return JsonResponse("Failed to log in!", safe = False)

@csrf_exempt
@api_view(["POST"])
def signup(request):
	response_data = {
		"username_exists": False,
		"email_exists": False,
	}

	if request.method == 'POST':
		data = json.loads(request.body)

		username = data['username']
		password = data['password']
		email = data['email']
  
		if User.objects.filter(email=email).exists():
			response_data['email_exists'] = True
			print("email exists")
			return JsonResponse(response_data, safe = False, status = 400)

		if User.objects.filter(username=username).exists():
			response_data['username_exists'] = True
			print("username exists")
			return JsonResponse(response_data, safe = False, status = 400)
  
		empty_cart = Cart.objects.create()
		user = User.objects.create_user(username=username, email=email, password=password,
                                  cart=empty_cart)
		
  
		user.is_staff = False
		user.is_active = True
		user.save()
		empty_cart.save()
  
		return JsonResponse("Successfully signed up!", safe = False, status = 200)
	else:
		return JsonResponse("Failed to sign up!", safe = False, status = 400)
	return JsonResponse("Failed to sign up!", safe = False, status = 400)

@api_view(["GET"])
def check_permissions(request):
	user = get_user_from_token_request(request)

	res = {
		"isAdmin": False
	}

	if user.is_staff:
		res['isAdmin'] = True

	return JsonResponse(res, status = 200)    
	