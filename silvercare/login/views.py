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
from django.utils import timezone
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime

def handle_bad_login_request(request):
	login_attempts = request.session.get('login_attempts', 0)
	cooldown = request.session.get('cooldown', None)
	print(login_attempts, cooldown, timezone.now())

	request.session['login_attempts'] = login_attempts + 1

	if login_attempts >= 3:
		if cooldown is not None:
			cooldown = parse_datetime(cooldown)
	 
			if cooldown < timezone.now():
				request.session['login_attempts'] = 0
				request.session['cooldown'] = None
		else:
			request.session['cooldown'] = (timezone.now() + timezone.timedelta(minutes=2)).isoformat()
	 
		return JsonResponse({'error': 'Too many login attempts. Please try again in 2 minutes.'}, status=429, safe = False)
	else:
		attempts_left = 3 - login_attempts
		return JsonResponse({'error': f'Incorrect credentials. {attempts_left} attempts left.'}, status=401, safe = False)

@csrf_exempt
@api_view(["POST"])
def login(request):
	if request.method == 'POST':
		data = json.loads(request.body)

		email = data['email']
		password = data['password']

		if not User.objects.filter(email=email).exists():
			return handle_bad_login_request(request)

		shadow_user = User.objects.get(email=email)
		user = authenticate(request, username=shadow_user.username, password=password)
		token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
		
		if user is not None or not token:
			user = shadow_user if user is None else user
      
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
			return handle_bad_login_request(request)

	return JsonResponse("Failed to log in!", safe = False, status = 400)

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

@api_view(["GET"])
def get_user_role(request):
	user = get_user_from_token_request(request)

	if user.is_staff:
		return JsonResponse({"role":"staff"}, status = 200, safe = False)

	if user.is_superuser:
		return JsonResponse({"role":"admin"}, status = 200, safe = False)
 
	return JsonResponse({"role":"user"}, status = 200, safe = False)
	
# @api_view(["POST"])
# def httponly_get_test(request):
# 	email = "stefan@stefan.com"
# 	password = "stefan"
# 	shadow_user = User.objects.get(email=email)
# 	user = authenticate(request, username=shadow_user.username, password=password)
# 	token = generate_jwt_token(user, email)

# 	response = JsonResponse(token, status = 200, safe = False)
# 	expiration = datetime.datetime.utcnow() + datetime.timedelta(days=30)
# 	response.set_cookie('token', token, 
# 						expires = expiration,
# 						httponly = True,
# 						samesite='None')
# 	response['Access-Control-Allow-Credentials'] = True

# 	return response

# @api_view(["POST"])
# def httponly_post_test(request):
#     jwt_token = request.COOKIES.get('token')
#     print(jwt_token)
#     print(request.COOKIES)
	
#     return JsonResponse("Success", status = 200, safe = False)