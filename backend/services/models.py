from django.db import models
from s3.s3_client import S3Client
from django.http import JsonResponse
from django.contrib.auth.models import User
from enum import Enum
import environ
import json
import uuid

# Environment variables
env = environ.Env()
environ.Env.read_env()

MAX_DESCRIPTION_LENGTH = 15000

# Featuring
class DetailType(Enum):
    pass

class ServiceImage(models.Model):
    id = models.CharField(max_length=37, primary_key=True)
    position = models.IntegerField()
    service = models.ForeignKey("Service", on_delete=models.SET_NULL, null=True)

class MapLocation(models.Model):
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)

    # Returns a json object with the latitude and longitude
    def serialize(self):
        return [self.latitude, self.longitude]

class ServiceOption(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField(default=0)
    duration = models.CharField(max_length=20, null = True)
    
    # Store day, month, year, hour, minute
    date = models.DateTimeField(null = True)
    location = models.CharField(default="",max_length=100, null = True)
    map_location = models.OneToOneField(MapLocation, on_delete=models.SET_NULL, null=True)
    rating = models.FloatField(default=0)
    number_ratings = models.IntegerField(default=0)
    details = models.TextField(null = True)
    city = models.CharField(default="",max_length=100, null = True)
    county = models.CharField(default="",max_length=100, null = True)

    service = models.ForeignKey('Service', on_delete=models.SET_NULL, null=True)

class Service(models.Model):
    # Base information about the service
    description = models.TextField()
    image = models.CharField(max_length=100, null=True)
    image_type = models.CharField(max_length=10, null=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, null = True)
    
    # service_raw_name is the name without diacritics
    raw_name = models.CharField(max_length = 100, null = True)

    organiser = models.CharField(max_length=100)
    has_more_options = models.BooleanField(default=False)
    options_common_city = models.BooleanField(default=False)
    common_location = models.BooleanField(default=False)
    location = models.CharField(default="", max_length=100, null = True)
    map_location = models.OneToOneField(MapLocation, on_delete=models.SET_NULL, null=True)
    semantic_field = models.CharField(max_length=100, null=True)
    city = models.CharField(default="", max_length=100, null = True)
    county = models.CharField(default="", max_length=100, null = True)
    
    # payment information
    iban = models.CharField(max_length=100, null = True)

    # Custom details about the service - dumped json
    extra_details = models.CharField(max_length=3000, null = True)    
    
    # hidden or not
    hidden = models.BooleanField(default=False)
    
    # stripe account id
    stripe_account_id = models.CharField(max_length=100, null = True)

    def add_image(self, position, image_data):
        if image_data is None:
            raise Exception("No image data provided")
        
        # If there is already an image for this id, delete it
        if ServiceImage.objects.filter(service=self).exists():
            ServiceImage.objects.get(service=self).delete()
        
        image = ServiceImage(id=str(uuid.uuid4()), position=position, service=self)
        image.save()

        # Save image with the id
        S3Client.get_instance()
        S3Client.upload_image_encode_base64(env('SILVERCARE_AWS_S3_SERVICES_SUBDIR'), image.id, image_data)
        
class PurchasedService(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null = True)
    base_service = models.ForeignKey(Service, on_delete=models.SET_NULL, null = True)
    option = models.ForeignKey(ServiceOption, on_delete=models.SET_NULL, null = True)

    participants_names = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    payment = models.ForeignKey('payments.Payment', on_delete = models.SET_NULL, null = True)

    command_number = models.CharField(max_length=50)

class CartService(models.Model):
    cart = models.ForeignKey('cart.Cart', on_delete=models.SET_NULL, null = True)
    base_service = models.ForeignKey(Service, on_delete=models.SET_NULL, null = True)
    option = models.ForeignKey(ServiceOption, on_delete=models.SET_NULL, null = True)
    number_of_participants = models.IntegerField(default=1)
    price = models.FloatField(default=0)
