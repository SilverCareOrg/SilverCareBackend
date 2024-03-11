from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from services.models import Service, ServiceOption, MapLocation
import json
from django.utils.dateparse import parse_duration
from django.utils.timezone import timedelta
from django.http import HttpResponse, JsonResponse
from login.utils import get_user_from_token_request
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
import os
import base64
import random as rd
import environ
from unidecode import unidecode
import uuid
from datetime import datetime
from django.utils import timezone
import re
from services.utils import delete_service_solr, add_service_solr, add_everything_solr

duration_pattern = re.compile(r'(?:(?P<days>\d+)d\s*)?(?:(?P<hours>\d+)h\s*)?(?:(?P<minutes>\d+)m)?')

env = environ.Env()
environ.Env.read_env()

BASE_IMG_PATH = "./services/images/"
PATH_TO_FIMG = env("SILVERCARE_PATH_TO_FIMG")

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
        user = get_user_from_token_request(request)
        
        if not user.is_staff:
            return Response({'message': 'You are not authorized to add services'}, status=400)
        
        data = request.data
        service_name = data.get('name')
        service_raw_name = unidecode(service_name)
        service_description = data.get('description')
        service_options_common_city = True if data.get('options_common_city') == "true" else False
        service_common_location = True if data.get('common_location') == "true" else False
        service_category = data.get('category')
        service_iban = data.get('iban')
        service_organiser = data.get('organiser')
        
        options = data.get("options")
        options = json.loads(options)
        
        if len(options) == 0:
            return Response({'message': 'You need to add at least one option'}, status=400)
        
        sections = data.get("sections")
        sections = json.dumps(json.loads(sections)["sections"])
        
        file = request.FILES.get('image')
        image_type = str(file).split('.')[-1]

        # generate_file_name
        file_name = str(uuid.uuid4())

        if "/var/www" in PATH_TO_FIMG:
            f = open(PATH_TO_FIMG + file_name + "." + image_type, 'wb')
        else:
            f = open(os.path.join(os.path.dirname(__file__), 'images/' + file_name + "." + image_type), 'wb')

        f.write(file.read())
        f.close()
        
        service_obj = Service.objects.create(name = service_name,
                                            organiser = service_organiser,
                                            raw_name = service_raw_name,
                                            description = service_description,
                                            options_common_city = service_options_common_city,
                                            common_location = service_common_location,
                                            category = service_category,
                                            iban = service_iban,
                                            image = file_name,
                                            image_type = image_type)
        
        if service_options_common_city:
            service_city = data.get('city')
            service_obj.city = service_city
            
            service_county = data.get('county')
            service_obj.county = service_county
            
        if service_common_location:
            service_location = data.get('location')
            service_obj.location = service_location
            
            service_map_location = data.get('map_location')
            if service_map_location != "":
                service_map_location = service_map_location.split(",")
                latitude = float(service_map_location[0])
                longitude = float(service_map_location[1][1:])
                map_location_obj = MapLocation.objects.create(latitude = latitude,
                                                                longitude = longitude)
                service_obj.map_location = map_location_obj
        
        for option in options:
            option_name = option.get("name")
            option_price = option.get("price")
            option_duration = option.get("duration")
            option_location = option.get("location")
            option_map_location = option.get("map_location")
            option_details = option.get("details")
            option_city = option.get("city")
            option_county = option.get("county")
            
            
            option_obj = ServiceOption.objects.create(name = option_name,
                                                      price = option_price,
                                                      duration = option_duration,
                                                      location = option_location,
                                                      details = option_details,
                                                      city = option_city,
                                                      county = option_county,
                                                      service = service_obj)
            
            try:
                option_date = option.get("date_time")
                
                if option_date != "":
                    option_date = datetime.strptime(option.get("date_time"), "%Y-%m-%dT%H:%M")
                    option_obj.date = option_date
            except:
                pass
            
            if option_map_location != "":
                option_map_location = option_map_location.split(",")
                latitude = float(option_map_location[0])
                longitude = float(option_map_location[1][1:])
                map_location_obj = MapLocation.objects.create(latitude = latitude,
                                                                longitude = longitude)
                option_obj.map_location = map_location_obj
            
            option_obj.save()
            
        service_obj.extra_details = sections
        service_obj.save()
        
        return Response({'message': 'Service created successfully'})

def get_services_helper(services):
    res = []
    bef = []

    for service in services:
        serialized_service = {
            "hidden": service.hidden,
            "name": service.name,
            "id": service.id,
            "category": service.category.capitalize(),
            "description": service.description,
            "img_path": service.image + "." + service.image_type,
            "img_type": service.image_type,
            "organiser": service.organiser,
            "service_id": service.id,
            "options_common_city": service.options_common_city,
            "common_location": service.common_location,
            "city": service.city,
            "county": service.county,
            "location": service.location,
            "map_location": service.map_location.serialize() if service.map_location else None,
            "options": [
                {
                    "name": option.name,
                    "price": option.price,
                    "duration": option.duration,
                    "date": option.date,
                    "location": option.location,
                    "map_location": option.map_location.serialize() if option.map_location else None,
                    "rating": option.rating,
                    "number_ratings": option.number_ratings,
                    "details": option.details,
                    "city": option.city,
                    "county": option.county,
                    "id": option.id
                }
                for option in ServiceOption.objects.filter(service = service)],
            "sections": json.loads(service.extra_details),
        }

        res.append(serialized_service)
        bef.append(service.image + "." + service.image_type)

    return res, bef

@api_view(["GET"])
def get_all_services(request):
    services = Service.objects.all()
    res, bef = get_services_helper(services)
    fef = os.listdir(PATH_TO_FIMG)

    if not "/var/www" in PATH_TO_FIMG:
        img_to_add = list(set(bef).difference(set(fef)))
        for img in img_to_add:
            content_to_write = ""

            with open(BASE_IMG_PATH + img, "rb") as image_file:
                content_to_write = image_file.read()
            
            with open(PATH_TO_FIMG + img, "wb") as f:
                print("Saving ... " + img)
                f.write(content_to_write)
    
    return JsonResponse(res, safe = False)

@api_view(["GET"])
def get_homepage_random_services(request):
    services = set(rd.choices(Service.objects.all(), k=6)) # k represents the number of services to be extracted
    res, _ = get_services_helper(services)
    return JsonResponse(res, safe = False)

@api_view(["GET"])
def get_homepage_best_selling_products(request):
    services = set(Service.objects.all()) 
    res, _ = get_services_helper(services)
    res = sorted(res, key=lambda x: float(x["rating"]), reverse=True)
    
    # We need 6 products, implement more complex logic later
    
    tmp = rd.sample(res, k = 6 if len(res) > 6 else len(res)) # k represents the number of services to be extracted
    res.clear()
    tmp = [res.append(x) for x in tmp if x not in res]

    return JsonResponse(res, safe = False)

# @api_view(["DELETE"])
# def delete_service(request):
#     id = request.GET.get('id','')
#     delete_service_solr(id)
    # We need to implement the delete_service for database

@api_view(["POST"])
def add_to_solr(request):
    add_everything_solr()
    return JsonResponse("Database loaded", safe = False)

@api_view(['POST'])
def set_service_visibility(request):
    user = get_user_from_token_request(request)
    if not user.is_staff:
        return JsonResponse({'message': 'You are not authorized to hide services'}, status=403)

    data = json.loads(request.body)
    
    if "hidden" not in data or "id" not in data:
        return JsonResponse("Missing parameters", safe=False, status=400)
    
    svc = Service.objects.get(id=data["id"])

    if svc is None:
        return JsonResponse("Service not found", safe=False, status=400)
    
    svc.hidden = data["hidden"]
    svc.save()
    return JsonResponse("Service hidden status updated successfully!", safe=False, status=200)
