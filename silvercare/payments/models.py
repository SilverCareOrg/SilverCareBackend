from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Payment(models.Model):
    payment_intent_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=0)
    currency = models.CharField(max_length=3)
    idempotency_request_id = models.CharField(max_length=255, null=True)
    idempotency_key = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
class Checkout(models.Model):
    payment_intent_id = models.CharField(max_length=255)
    metadata = models.CharField(max_length=1000)


