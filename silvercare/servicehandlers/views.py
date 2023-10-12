from django.shortcuts import render

# Create your views here.
from services.models import Service
from django.http import JsonResponse
from rest_framework.response import Response
from login.utils import get_user_from_token_request
from rest_framework.decorators import api_view

@api_view(['GET'])
def get_services(request):
    inf_lim = request.GET.get('inf_lim', 0) #default inf_lim = 0
    sup_lim = request.GET.get('sup_lim', 20) #default sup_lim = 20
    if inf_lim > sup_lim:
         inf_lim, sup_lim = sup_lim, inf_lim
    services = Service.objects.filter(pk__gte=inf_lim, pk__lte=sup_lim)
    data = list(services.values())
    return JsonResponse(data, safe = False)


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
        service.delete()
        return JsonResponse({'message': 'Service deleted successfully'}, safe = False)
    except Service.DoesNotExist:
        return JsonResponse({'message' : 'Service not found'}, safe = False)



