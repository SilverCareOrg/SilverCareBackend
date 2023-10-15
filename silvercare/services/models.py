from django.db import models
from django.http import JsonResponse
from django.contrib.auth.models import User
import json

class Service(models.Model):
    description = models.CharField(max_length=1500)
    price = models.CharField(max_length = 50)

    # This is just the path (name of the photo) to where the image is stored
    image = models.CharField(max_length=100)
    image_type = models.CharField(max_length=10)    

    name = models.CharField(max_length=100)
    rating = models.FloatField(default=0.0)
    category = models.CharField(max_length=100)
    organiser = models.CharField(max_length=100)
    # cutom_data ={ 'options' : [
    #                              {
    #                                 'location' : 
    #                                 'duration' : 
    #                                 'price'    :
    #                                 'nr_available_spots' : 
    #                                 'rating' :

    #                             }
    # ],

    
    # }
    
    semantic_field = models.CharField(max_length=100, null=True)


    def __str__(self):
        serialized_obj = {
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "image": self.image,
            "rating": self.rating,
            "category": self.category,
            "organiser": self.organiser    
               
        }
        
        return JsonResponse(serialized_obj, safe = False)    

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

    senior_name = models.CharField(max_length=100)
    adult_name = models.CharField(max_length=100, null = True)
    phone_number = models.CharField(max_length=100)
    companion = models.CharField(max_length=100, null = True)
    email = models.CharField(max_length=100)
        