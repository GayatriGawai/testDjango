from django.urls import path
from . import views  

urlpatterns = [
    path('', views.get_properties,),
    path('<str:postal_code>/', views.get_places_by_postal_code),
    path("<int:number>/nearest-addresses/", views.get_nearest_addresses), 
    path("<str:postal_code>/<str:street_name>",views.get_street_history_and_addresses)
]