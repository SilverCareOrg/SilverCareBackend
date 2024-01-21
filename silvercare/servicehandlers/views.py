from django.shortcuts import render

# Create your views here.
from services.models import Service, ServiceOption
from django.http import JsonResponse
from rest_framework.response import Response
from login.utils import get_user_from_token_request
from rest_framework.decorators import api_view
from services.views import get_services_helper
from search.views import search_helper
from services.utils import delete_service_solr, add_service_solr
from enum import Enum

class ServicesQueryType(Enum):
    NORMAL = 1
    EDIT_TABLE = 2

def location_filter(services, location):
    return [service for service in services\
        if location in (("" if service.location is None else service.location) +\
            ("" if service.city is None else service.city)\
            + ("" if service.county is None else service.county)) or\
        len([option for option in ServiceOption.objects.filter(service = service)\
            if location in (("" if option.location is None else option.location) +\
            ("" if option.city is None else option.city)\
            + ("" if option.county is None else option.county))]) > 0]

def sort_filter(services, type):
    sort_key_function = lambda x: min([option.price for option in ServiceOption.objects.filter(service = x)])
    
    if type == 'ascending':
        return sorted(services, key=sort_key_function)
    if type == 'descending':
        return sorted(services, key=sort_key_function, reverse=True)
    return services

@api_view(['GET'])
def get_services(request):
    searched = request.GET.get('searched', '') # default searched = ''
    inf_lim = int(request.GET.get('inf_limit', 0)) # default inf_lim = 0
    sup_lim = int(request.GET.get('sup_limit', 20)) # default sup_lim = 20
    category = request.GET.get('category', '') # default category = ''
    location = request.GET.get('location', '') # default location = ''
    sort = request.GET.get('sort', '') # default sort = ''; you can sort by 'views', 'ascending', 'descending'

    if inf_lim > sup_lim:
        inf_lim, sup_lim = sup_lim, inf_lim

    # Get all services
    services = Service.objects.all() if searched == '' else search_helper(searched)

    # Filter by category
    if category is not None and category != '':
        services = services.filter(category__contains = category)
    
    # Filter by location - main service or options
    if location is not None and location != '':
        services = location_filter(services, location)
    
    if sort is not None and sort == 'ascending':
        services = sort_filter(services, 'ascending')
    if sort is not None and sort == 'descending':
        services = sort_filter(services, 'descending')

    total = len(services)
    services, _ = get_services_helper(services[inf_lim:sup_lim])
    
    type_of_query = request.GET.get('type_of_query', ServicesQueryType.NORMAL.value)
    
    try:
        type_of_query = int(type_of_query)
    except:
        type_of_query = ServicesQueryType.NORMAL.value
    
    if type_of_query == ServicesQueryType.EDIT_TABLE.value:
        services = [{
            "name": service["name"],
            "id": service["id"],
            "category": service["category"],
            "organiser": service["organiser"],
        } for service in services]

    return JsonResponse({"services":services, "total":total}, safe = False, status=200)
 
@api_view(['GET'])
def get_service_by_id(request):
    id = request.GET.get('id', "")
    service = Service.objects.filter(id = id)
    service = get_services_helper(service)
    return JsonResponse({'service': service}, safe = False, status = 200)

@api_view(['GET'])
def get_services_by_organiser(request):
    organiser = request.GET.get('organiser', 'Null') #default organiser = 'Null'
    services = Service.objects.filter(organiser__contains = organiser)
    data = list(services.values())
    return JsonResponse(data, safe = False)

@api_view(["GET"])
def delete_service(request):
    
    user = get_user_from_token_request(request)
    if not user.is_staff:
            return Response({'message': 'You are not authorized to add services'}, status=403)
    
    service_id = request.GET.get('service_id', 0)
    try:
        service = Service.objects.get(id=service_id)
        delete_service_solr(service_id)
        service.delete()
        return JsonResponse({'message': 'Service deleted successfully'}, safe = False)
    except Service.DoesNotExist:
        return JsonResponse({'message' : 'Service not found'}, safe = False)


@api_view(["POST"])
def modify_service(request):

    user = get_user_from_token_request(request)
    if not user.is_staff:
            return Response({'message': 'You are not authorized to add services'}, status=403)
    try:
        service_id = request.GET.get('id', 0)
        service = Service.objects.get(id = service_id)
        if service:
            service.description = request.GET.get('description', 0)
            service.price = request.GET.get('price', 0)
            service.image = request.GET.get('image', 0)
            service.image_type = request.GET.get('image_type', 0)
            service.name = request.GET.get('name', 0)
            service.rating = request.GET.get('rating', 0)
            service.category = request.GET.get('category', 0)
            service.organiser = request.GET.get('organiser', 0)
            service.raw_name = request.GET.get('raw_name', 0)
            service.location = request.GET.get('location', 0)
            service.options_common_city = request.GET.get('options_common_city', 0)
            service.common_location = request.GET.get('common_location', 0)
            service.map_location = request.GET.get('map_location', 0)
            service.semantic_field = request.GET.get('semantic_field', 0)
            service.city = request.GET.get('city', 0)
            service.county = request.GET.get('county', 0)
            service.iban = request.GET.get('iban', 0)
            service.extra_details = request.GET.get('extra_details', 0)
            
            service.save()
            return JsonResponse({'message': 'Service updated successfully!'}, status=200)
    except:
            return JsonResponse({'message': 'Error while modifying the service.'}, status=404)





