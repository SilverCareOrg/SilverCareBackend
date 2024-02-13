from django.urls import path
from .views import search_ex

urlpatterns = [
    path("search_ex", search_ex),
]