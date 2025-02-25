
from django.urls import path
from . import views # Importing the views module from the current package

urlpatterns = [
    path('', views.get_districts_list, name='districts-data'), # URL pattern for the Districts view
    path('<int:district_code>/', views.get_streets_by_district_code, name='streets-data'), # URL pattern for the Streets view
    # path('<int:district_code>/<str:street_name>', views.get_street_history, name='streets-history'), # URL pattern for the Street-History view
    # path('<int:district_code>/<str:street_name>/', views.get_addresses_by_street, name='streets-details'), # URL pattern for the Addresses view
    path('<str:q>/', views.get_address_search, name='address-search'), # URL pattern for the Address-Search view
    path('q/<str:q>/', views.get_numbered_address, name='named-address-search') # URL pattern for the Address-Search view
]
