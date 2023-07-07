from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from services.models import Service
import json
from django.http import HttpResponse, JsonResponse
from login.utils import get_user_from_token_request
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
import cv2
import os

class ServiceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    category = serializers.CharField(max_length=100)
    price = serializers.CharField(max_length = 50)
    description = serializers.CharField(max_length=255)

class CreateServiceView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        serializer = ServiceSerializer(data=request.data)        
        if serializer.is_valid():            
            name = serializer.validated_data.get('name')
            category = serializer.validated_data.get('category')
            price = serializer.validated_data.get('price')
            description = serializer.validated_data.get('description')

            file = request.FILES.get('file')
            f = open(os.path.join(os.path.dirname(__file__), 'images/' + str(file)), 'wb')
            f.write(file.read())
            
            service = Service.objects.create(name=name,
                                             category=category,
                                             price=price,
                                             description=description,
                                             image=str(file))

            return Response({'message': 'Service created successfully'})
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=400)
