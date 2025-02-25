
# standard library imports
import os
import requests
import re
from urllib.parse import quote_plus

from django.http import JsonResponse  # Importing JsonResponse to send JSON responses

# django imports
from rest_framework.decorators import api_view  # Importing api_view decorator from Django REST framework
from rest_framework.response import Response  # Importing Response to send HTTP responses
from rest_framework.request import Request  # Importing Request to send HTTP responses
from rest_framework import status

@api_view(['GET'])
def get_districts_list(request: Request) -> Response:
    """
    Handles GET requests to fetch the list of districts from an external API.
    
    Args:
        request (Request): The HTTP request object.
    
    Returns:
        Response: A Response object containing the data or an error message.
    """
    BASE_URL: str = os.getenv("DISTRICTS_DATA_URL")  # Getting the base URL from environment variables

    try:
        response = requests.get(BASE_URL)  # Making a GET request to the external API
        response.raise_for_status()  # Raises an error for bad responses (4xx, 5xx)
        return Response(response.json(), status=status.HTTP_200_OK)  # Returning the data with a 200 OK status

    except requests.exceptions.RequestException as e:
        # Handling any request exceptions and returning a 500 Internal Server Error status
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_streets_by_district_code(request: Request, district_code: int) -> Response:
    """
    Fetches the list of streets based on district code.

    Args:
        request (Request): The HTTP request object.
        district_code (int): The district code to filter streets.

    Returns:
        Response: A Response object containing the data or an error message.
    """
    BASE_URL: str = os.getenv("STREETS_DATA_URL")  # Getting the base URL from environment variables
    formatted_district = f"{district_code:02d}e"  # Ensure it's zero-padded (e.g., 1 -> 01e, 2 -> 02e)
    query_params = {"refine.arrdt": formatted_district}  # Formatting district code properly

    try:
        response = requests.get(BASE_URL, params=query_params)
        response.raise_for_status()  # Raises an error for bad responses (4xx, 5xx)
        return Response(response.json(), status=status.HTTP_200_OK)

    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# def fetch_street_history(district_code: int, street_name: str) -> dict:
#     """
#     Fetches the history of a street in a given district.

#     Args:
#         district_code (int): The arrondissement number.
#         street_name (str): The name of the street.

#     Returns:
#         dict: A dictionary containing the street history or an error message.
#     """
#     data_url = os.getenv("STREETS_HISTORY")  # Getting the base URL from environment variables
#     if not data_url:
#         return {"error": "STREETS_HISTORY environment variable not set"}

#     # Encode the full query properly for URL
#     encoded_query = quote_plus(f'typo_min="{street_name}"')
#     api_url = f"{data_url}&where={encoded_query}"

#     response = requests.get(api_url)
#     response.raise_for_status()  # Raise an error for non-200 responses
#     records = response.json().get('results', [])

#     if not records:
#         return {"message": "No history found for this street"}

#     # Extract relevant history information
#     history = []
#     for record in records:
#         historical_reference = record.get('historique')
#         opening_reference = record.get('ouverture')
#         sanitation_reference = record.get('assainissement')

#         if historical_reference:
#             history_label = "historical_reference"
#             history_value = historical_reference
#         elif opening_reference:
#             history_label = "opening_reference"
#             history_value = opening_reference
#         elif sanitation_reference:
#             history_label = "sanitation_reference"
#             history_value = sanitation_reference
#         else:
#             history_label = "No History Available"
#             history_value = "No history available"

#         history.append({
#             'district': f"{district_code}e",
#             'street_name': record.get('typo_min', 'Unknown'),
#             history_label: history_value,
#             'original_reference': record.get('orig', 'Unknown')
#         })

#     return {"street_history": history}

# data_url_authorizations = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/autorisations-durbanisme-h/records"
# @api_view(['GET'])
# def get_addresses_by_street(request: Request, district_code: int, street_name: str) -> Response:
#     """
#     Fetches the list of addresses for a given street and its history.

#     Args:
#         request (Request): The HTTP request object.

#     Returns:
#         Response: A Response object containing the addresses and history or an error message.
#     """
#     # Fetch street history
#     history = fetch_street_history(district_code, street_name)
    
#     if not street_name:
#         return Response({'error': 'Street name is required'}, status=400)
    
#     # Extract district code from the postal code (assuming the first part of the street name is the district code)
    
#     # Encode street name query
#     query = f"adresse_du_terrain=\"{street_name}\""
#     encoded_query = quote_plus(query)
#     api_url = f"{data_url_authorizations}?select=adresse_du_terrain&select=numero_voirie_du_terrain&limit=100&where={encoded_query}"
    
#     try:
#         response = requests.get(api_url)
#         response.raise_for_status()  # Raises an error for bad responses (4xx, 5xx)
#         data = response.json()
#         records = data.get('results', [])
        
#         if not records:
#             return Response({'message': 'No addresses found for this street'}, status=404)
        
#         # Extract relevant address information
#         addresses = [
#             f"{record.get('numero_voirie_du_terrain', 'Unknown')} {record.get('adresse_du_terrain', 'Unknown')}"
#             for record in records
#         ]
        
#         return Response({'addresses': addresses, 'history': history}, status=status.HTTP_200_OK)

#     except requests.exceptions.RequestException as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_address_search(request: Request, q:str) -> Response:
    """
    Handles GET requests to fetch the list of districts from an external API.
    
    Args:
        q (str): The name of the street.
    
    Returns:
        Response: A Response object containing the data or an error message.
    """
    BASE_URL: str = os.getenv("ADDRESS_OPENDATA")  # Getting the base URL from environment variables
    api_url = f"{BASE_URL}?&q={q}"
    try:
        response = requests.get(api_url)  # Making a GET request to the external API
        response.raise_for_status()  # Raises an error for bad responses (4xx, 5xx)
        return Response(response.json(), status=status.HTTP_200_OK)  # Returning the data with a 200 OK status

    except requests.exceptions.RequestException as e:
        # Handling any request exceptions and returning a 500 Internal Server Error status
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_numbered_address(request: Request, q:str) -> Response:
    """
    Handles GET requests to fetch the list of districts from an external API.
    
    Args:
        request (Request): The HTTP request object.
        q (str): Can be a street name or a street number followed by a street name.
    
    Returns:
        Response: A Response object containing the data or an error message.
    """
    BASE_URL: str = os.getenv("STREETS_ADDRESSES")  # Getting the base URL from environment variables
    # Split the query into words
    parts = q.strip().split()

    # Extract the first number (street number) if it exists
    street_number = parts[0] if parts[0].isdigit() else None

    # Extract the remaining words as the street name
    street_name_start_idx = 1 if street_number else 0
    street_name = " ".join(parts[street_name_start_idx:])  # Everything after the number

    # Construct the API URL dynamically
    api_url = f"{BASE_URL}&q={requests.utils.quote(street_name)}"

    if street_number:
        api_url += f"&refine.numero_voirie_du_terrain={street_number}"

    try:
        response = requests.get(api_url)  # Making a GET request to the external API
        response.raise_for_status()  # Raises an error for bad responses (4xx, 5xx)
        return Response(response.json(), status=status.HTTP_200_OK)  # Returning the data with a 200 OK status

    except requests.exceptions.RequestException as e:
        # Handling any request exceptions and returning a 500 Internal Server Error status
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
