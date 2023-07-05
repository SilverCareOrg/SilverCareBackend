from django.db import models
from django.http import JsonResponse
import json

class Service(models.Model):
    description = models.CharField(max_length=100)
    price = models.CharField(max_length = 50)

    # This is just the path (name of the photo) to where the image is stored
    image = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    rating = models.FloatField(default=0.0)
    category = models.CharField(max_length=100)

    def __str__(self):
        serialized_obj = {
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "image": self.image,
            "rating": self.rating,
            "category": self.category            
        }
        
        return JsonResponse(serialized_obj, safe = False)
        