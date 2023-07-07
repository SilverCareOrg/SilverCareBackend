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
import os
import base64

BASE_IMG_PATH = "./services/images/"
PATH_TO_FIMG = "../../SilverCareFrontend/src/images/"

class ServiceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    category = serializers.CharField(max_length=100)
    price = serializers.CharField(max_length = 50)
    description = serializers.CharField(max_length=1500)
    organiser = serializers.CharField(max_length=100)

class CreateServiceView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        serializer = ServiceSerializer(data=request.data)        
        if serializer.is_valid():            
            name = serializer.validated_data.get('name')
            category = serializer.validated_data.get('category').lower()
            price = serializer.validated_data.get('price')
            description = serializer.validated_data.get('description')
            organiser = serializer.validated_data.get('organiser')

            file = request.FILES.get('file')
            image_type = str(file).split('.')[-1]

            f = open(os.path.join(os.path.dirname(__file__), 'images/' + str(file)), 'wb')
            f.write(file.read())
            
            service = Service.objects.create(name=name,
                                             category=category,
                                             price=price,
                                             description=description,
                                             image=str(file),
                                             organiser=organiser,
                                             image_type=image_type)
            service.save()

            return Response({'message': 'Service created successfully'})
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=400)

@api_view(["GET"])
def get_all_services(request):
    services = Service.objects.all()
    res = []
    bef = []
    
    for service in services:
        serialized_service = {
            "name": service.name,
            "category": service.category.capitalize(),
            "price": service.price,
            "description": service.description,
            "rating": str(service.rating),
            "img_path": service.image,
            "img_type": service.image_type,
            "organiser": service.organiser
        }

        res.append(serialized_service)
        bef.append(service.image)
        
    fef = os.listdir(PATH_TO_FIMG)
    img_to_add = list(set(bef).difference(set(fef)))
    for img in img_to_add:
        content_to_write = ""
        print(img)
        with open(BASE_IMG_PATH + img, "rb") as image_file:
            content_to_write = image_file.read()
        
        with open(PATH_TO_FIMG + img, "wb") as f:
            print("Saving ... " + img)
            f.write(content_to_write)
    
    return JsonResponse(res, safe = False)