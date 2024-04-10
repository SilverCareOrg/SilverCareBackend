from django.urls import path
from .views import CreateServiceView, get_all_services,\
    get_homepage_random_services,\
    get_homepage_best_selling_products,\
    add_to_solr,\
    set_service_visibility,\
    CreateLinkServiceView,\
    set_link_service_visibility,\
    EditLinkServiceView

urlpatterns = [
    path('create_service/', CreateServiceView.as_view(), name='create_service'),
    path('create_link_service/', CreateLinkServiceView.as_view(), name='link_create_service'),
    path('edit_link_service/', EditLinkServiceView.as_view(), name='edit_link_service'),
    path('get_all_services', get_all_services),
    path('get_homepage_random_services', get_homepage_random_services),
    path('get_homepage_best_selling_products', get_homepage_best_selling_products),
    path('add_to_solr', add_to_solr),
    path('set_service_visibility', set_service_visibility),
    path('set_link_service_visibility', set_link_service_visibility),
]