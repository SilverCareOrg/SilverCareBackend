from django.shortcuts import render

# Create your views here.
from services.models import Service, ServiceOption, LinkService
from django.http import JsonResponse
from rest_framework.response import Response
from login.utils import get_user_from_token_request
from rest_framework.decorators import api_view
from services.views import get_services_helper
from search.views import search_helper
from services.utils import delete_service_solr, add_service_solr
from enum import Enum
from s3.s3_client import S3Client

class ServicesQueryType(Enum):
    NORMAL = 1
    EDIT_TABLE = 2

def location_filter(services, location):
    services = []
    
    for svc in services:
        if isinstance(svc, LinkService):
            if location in svc.city:
                services.append(svc)
            continue

        if location in (("" if svc.location is None else svc.location) +\
            ("" if svc.city is None else svc.city)\
            + ("" if svc.county is None else svc.county)):
            services.append(svc)
        else:
            for option in ServiceOption.objects.filter(service = svc):
                if location in (("" if option.location is None else option.location) +\
                    ("" if option.city is None else option.city)\
                    + ("" if option.county is None else option.county)):
                    services.append(svc)
                    break
    
    # return [service for service in services\
    #     if location in (("" if service.location is None else service.location) +\
    #         ("" if service.city is None else service.city)\
    #         + ("" if service.county is None else service.county)) or\
    #     len([option for option in ServiceOption.objects.filter(service = service)\
    #         if location in (("" if option.location is None else option.location) +\
    #         ("" if option.city is None else option.city)\
    #         + ("" if option.county is None else option.county))]) > 0]

def sort_filter(services, type):
    sort_key_function = lambda x: min([option.price for option in ServiceOption.objects.filter(service = x)] if isinstance(x, Service) else [x.price])

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
    services = list(Service.objects.all())# if searched == '' else search_helper(searched)
    services.extend(list(LinkService.objects.all()))
    
    # Filter by location - main service or options
    if location is not None and location != '':
        services = location_filter(services, location)
    
    # Filter by category
    if category is not None and category != '':
        services = list(filter(lambda x: category in x.category, services))

    if sort is not None and sort == 'ascending':
        services = sort_filter(services, 'ascending')
    if sort is not None and sort == 'descending':
        services = sort_filter(services, 'descending')

    # instantiate s3
    S3Client.get_instance()

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
            "hidden": service["hidden"]
        } for service in services]

    try:
        user = get_user_from_token_request(request)
        if not user.is_staff:
            services = [service for service in services if not service["hidden"]]
    except:
        services = [service for service in services if not service["hidden"]]

    return JsonResponse({"services":services, "total":total}, safe = False, status=200)
 
@api_view(['GET'])
def get_link_services(request):
    services = LinkService.objects.all()
    total = len(services)

    type_of_query = request.GET.get('type_of_query', ServicesQueryType.NORMAL.value)
    S3Client.get_instance()

    try:
        type_of_query = int(type_of_query)
    except:
        type_of_query = ServicesQueryType.NORMAL.value

    if type_of_query == ServicesQueryType.EDIT_TABLE.value:
        services = [{
            "name": service.name,
            "id": service.id,
            "category": service.category,
            "organiser": service.organiser,
            "hidden": service.hidden
        } for service in services]

    try:
        user = get_user_from_token_request(request)
        if not user.is_staff:
            services = [service for service in services if not service["hidden"]]
    except:
        services = [service for service in services if not service["hidden"]]

    return JsonResponse({"services":services, "total":total}, safe = False, status=200)
 
@api_view(['GET'])
def get_service_by_id(request):
    S3Client.get_instance()
    id = request.GET.get('id', "")
    service = Service.objects.filter(id = id)
    service = get_services_helper(service)
    return JsonResponse({'service': service}, safe = False, status = 200)

@api_view(['GET'])
def get_link_service_by_id(request):
    S3Client.get_instance()
    id = request.GET.get('id', "")
    service = LinkService.objects.filter(id = id)
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



