from django.db import models
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from enum import Enum

# Featuring
class DetailType(Enum):
    pass

class MapLocation(models.Model):
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)

    # Returns a json object with the latitude and longitude
    def serialize(self):
        return [self.latitude, self.longitude]

class ServiceOption(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField(default=0)
    duration = models.DurationField(null = True)
    
    # Store day, month, year, hour, minute
    date = models.DateTimeField(null = True)
    location = models.CharField(max_length=100, null = True)
    map_location = models.OneToOneField(MapLocation, on_delete=models.SET_NULL, null=True)
    rating = models.FloatField(default=0)
    number_ratings = models.IntegerField(default=0)
    details = models.CharField(max_length=3000, null = True)
    city = models.CharField(max_length=100, null = True)
    county = models.CharField(max_length=100, null = True)

    service = models.ForeignKey('Service', on_delete=models.SET_NULL, null=True)

class Service(models.Model):
    # Base information about the service
    description = models.CharField(max_length=1500)
    image = models.CharField(max_length=100)
    image_type = models.CharField(max_length=10)    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, null = True)
    
    # service_raw_name is the name without diacritics
    raw_name = models.CharField(max_length = 100, null = True)

    organiser = models.CharField(max_length=100)
    has_more_options = models.BooleanField(default=False)
    options_common_city = models.BooleanField(default=False)
    common_location = models.BooleanField(default=False)
    location = models.CharField(max_length=100, null = True)
    map_location = models.OneToOneField(MapLocation, on_delete=models.SET_NULL, null=True)
    semantic_field = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null = True)
    county = models.CharField(max_length=100, null = True)
    
    # payment information
    iban = models.CharField(max_length=100, null = True)

    # Custom details about the service - dumped json
    extra_details = models.CharField(max_length=3000, null = True)    


class PurchasedService(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null = True)
    base_service = models.ForeignKey(Service, on_delete=models.SET_NULL, null = True)

    senior_name = models.CharField(max_length=100)
    adult_name = models.CharField(max_length=100, null = True)
    phone_number = models.CharField(max_length=100)
    companion = models.CharField(max_length=100, null = True)
    email = models.CharField(max_length=100)
    payment = models.ForeignKey('payments.Payment', on_delete = models.SET_NULL, null = True)

class CartService(models.Model):
    cart = models.ForeignKey('cart.Cart', on_delete=models.SET_NULL, null = True)
    base_service = models.ForeignKey(Service, on_delete=models.SET_NULL, null = True)
    option = models.ForeignKey(ServiceOption, on_delete=models.SET_NULL, null = True)
    number_of_participants = models.IntegerField(default=1)
    price = models.FloatField(default=0)
