from django.shortcuts import render

from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.response import Response
from login.utils import get_user_from_token_request
from rest_framework.decorators import api_view

@api_view(['GET'])
def get_users(request):
    try:
        user = get_user_from_token_request(request)
        if not user.is_staff:
            return Response({'message': 'You are not authorized to get users'}, status=403)
        inf_lim = request.GET.get('inf_lim', 0)
        sup_lim = request.GET.get('sup_lim', 20)
        if inf_lim > sup_lim:
            inf_lim, sup_lim = sup_lim, inf_lim
        users = User.objects.filter(pk__gte = inf_lim, pk__lte = sup_lim)
        data = list(users.values())
        return JsonResponse(data, safe = False)
    except Exception as e:
        return Response({'message': 'An error occurred.'}, status=500)



@api_view(['GET'])
def get_users_by_email(request):
    try:
        user = get_user_from_token_request(request) 
        if not user.is_staff:
            return Response({'message': 'You are not authorized to get users'}, status=403)

        search_email = request.GET.get('search_email', '') 
        users = User.objects.filter(email__contains=search_email)
        
        data = list(users.values())

        return JsonResponse(data, safe=False)
    except Exception as e:
        return Response({'message': 'An error occurred.'}, status=500)
    

@api_view(['POST'])
def set_staff(request):
    try:
        user = get_user_from_token_request(request) 
        if not user.is_staff: 
            return Response({'message': 'You are not authorized to set staff'}, status=403)
        staff_email = request.GET.get('staff_email', '')
        users = User.objects.filter(email__contains = staff_email).first()
        users.is_staff= True
        users.save()
        return Response({'message':'Staff set successfully'})
    except Exception as e:
        return Response({'message': 'An error occurred.'}, status=500)
    

@api_view(['POST'])
def unset_staff(request):
    try:
        user = get_user_from_token_request(request) 
        if not user.is_staff: 
            return Response({'message': 'You are not authorized to set staff'}, status=403)
        staff_email = request.GET.get('staff_email', '')
        users = User.objects.filter(email__contains = staff_email).first()
        users.is_staff = False
        users.save()
        return Response({'message':'Staff unset successfully'})
    except Exception as e:
        return Response({'message': 'An error occurred.'}, status=500)
    



    # @api_view(['GET'])
# def get_users_by_email(request):
#     user = get_user_from_token_request(request)
#     if not user.is_staff:
#         return Response({'message': 'You are not authorized to add services'}, status=403)
#     search_email = request.GET.get('search_email', 0)
#     users = User.objects.filter(email__contains = search_email)
#     data = list(users.values())
#     return JsonResponse(data, safe = False)
