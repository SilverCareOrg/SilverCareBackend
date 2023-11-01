from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.db import connection
from . import views
from django.urls import path, reverse
from services.models import Service
from django.template import loader  
from django.shortcuts import render
from django.views import generic
from django.utils import timezone
import Levenshtein
from search.semantic_fields import fields
from search.correct_words import correct_words, seplist
import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from services.views import get_services_helper

@api_view(['POST'])
def search_ex(request):
	data = json.loads(request.body)
	print(data)
	if 'searched' in data.keys():
		services = Service.objects.none()
		searched = str(data["searched"])
		for word in searched.split(" "):
			if word not in seplist:
				wordd = word[:] 
				newword = min(correct_words, key=lambda x: Levenshtein.distance(word, x))
				wordlower = newword[0].lower() + newword[1:]
				wordupper = newword[0].upper() + newword[1:]
				services1 = Service.objects.filter(name__contains = wordlower)
				services2 = Service.objects.filter(name__contains = wordupper)
				services |= services1 
				services |= services2
				for x in fields:
					if wordlower in fields[x]:
						services3 = Service.objects.filter(semantic_field__contains = x)
						services |= services3 
				wordlower = wordd[0].lower() + wordd[1:]
				wordupper = wordd[0].upper() + wordd[1:]
				services1 = Service.objects.filter(name__contains = wordlower)
				services2 = Service.objects.filter(name__contains = wordupper)
				services |= services1 
				services |= services2
				for x in fields:
					if wordlower in fields[x]:
						services3 = Service.objects.filter(semantic_field__contains = x)
						services |= services3 

		res, _ = get_services_helper(services)
		return JsonResponse(res, safe=False, status = 200)
   
	else:
	   return JsonResponse({
			'error': "No input given"
	   }, status = 400)
	    

