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
import threading
import json
import queue
from pysolr import Solr

def search_helper(searched):
	services = Service.objects.none()
	services = []
	conn = Solr('http://localhost:8983/solr/new_core', always_commit = True)
	for word in searched.split(" "):
		results = conn.search(f'name:{word}',**{
    						  'qt':'spell',  
    						  'spellcheck':'true',  
    						  'spellcheck.collate':'true'  
							 })
		for result in results:
			services.append(result)
	return services
 

@api_view(['GET'])
def search(request):
    searched = request.GET.get('searched', '')
    q = queue.Queue()
    def wrapper():
        q.put(search_helper(searched))
    t = threading.Thread(target=wrapper)
    t.start()
    t.join()
    services = q.get()
    return JsonResponse(services, safe=False, status=200)
