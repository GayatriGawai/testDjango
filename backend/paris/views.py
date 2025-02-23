import requests
from django.http import JsonResponse
from math import radians, cos, sin, sqrt, atan2
import urllib.parse

def get_properties(request):
    """
    Fetch property data from the Open Data Paris API and return it as JSON.
    """
    # Open Data Paris API URL
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/records?limit=20"
    
    try:
        # Make the API request
        response = requests.get(url)
        data = response.json()  # Convert response to JSON

        # Return the data as a JSON response
        return JsonResponse(data, safe=False)

    except requests.exceptions.RequestException as e:
        # Handle any errors during the API request
        return JsonResponse({"error": str(e)}, status=500)

def get_places_by_postal_code(request, postal_code):
    """
    Fetch all places (streets, landmarks, neighborhoods) for a given postal code
    using api-adresse.data.gouv.fr.
    """
    url = f"https://api-adresse.data.gouv.fr/search/?limit=100&q={postal_code}"

    try:
        response = requests.get(url)
        data = response.json()
        return JsonResponse(data, safe=False)

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

STREET_HISTORY_API = "https://api-adresse.data.gouv.fr/search/?type=street&q="
ADDRESS_API = "https://api-adresse.data.gouv.fr/search/?type=housenumber&q="

def get_street_history_and_addresses(request, postal_code, street_name):
    """Fetch history and list of addresses for a given street in a Paris arrondissement."""
    try:
        # Convert street name to lowercase and replace spaces with hyphens
        formatted_street = street_name.lower().replace(" ", "-")

        # Fetch street history
        history_url = f"{STREET_HISTORY_API}{formatted_street}"
        history_response = requests.get(history_url)
        history_response.raise_for_status()
        history_data = history_response.json()

        # Extract street history (if exists)
        street_history = history_data.get("features", [{}])[0].get("properties", {}).get("label", "No history available")

        # Fetch addresses on the street
        address_url = f"{ADDRESS_API}{formatted_street}"
        address_response = requests.get(address_url)
        address_response.raise_for_status()
        address_data = address_response.json()

        # Extract list of addresses
        addresses = [
            f"{record['properties']['housenumber']} {record['properties']['name']}"
            for record in address_data.get("features", [])
        ]

        return JsonResponse({
            "street": street_name,
            "postal_code": postal_code,
            "history": street_history,
            "addresses": addresses
        })

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

ARRONDISSEMENT_API = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/records?limit=20"
ADDRESSES_API = "https://documentation-resources.opendatasoft.com/api/explore/v2.1/catalog/datasets/les-arbres-remarquables-de-paris/records?limit=50"

def haversine(lon1, lat1, lon2, lat2):
    """Calculate distance between two points using the Haversine formula (in km)."""
    R = 6371  # Earth radius in km
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c  # Distance in km

def get_nearest_addresses(request, number):
    """Fetch the nearest addresses for an arrondissement based on coordinates."""
    try:
        # Step 1: Fetch Arrondissement Data
        arr_response = requests.get(ARRONDISSEMENT_API)
        arr_response.raise_for_status()
        arr_data = arr_response.json()

        # Find matching arrondissement
        arrondissement = next(
            (record for record in arr_data.get("results", []) if record["c_ar"] == number),
            None
        )

        if not arrondissement:
            return JsonResponse({"error": "Arrondissement not found"}, status=404)

        arr_lon, arr_lat = arrondissement["geom_x_y"]["lon"], arrondissement["geom_x_y"]["lat"]

        # Step 2: Fetch Address Data
        addr_response = requests.get(ADDRESSES_API)
        addr_response.raise_for_status()
        addr_data = addr_response.json()

        # Step 3: Find the closest addresses
        nearest_addresses = []
        for record in addr_data.get("results", []):
            if "geo_point" in record:
                addr_lon, addr_lat = record["geo_point"]["lon"], record["geo_point"]["lat"]
                distance = haversine(arr_lon, arr_lat, addr_lon, addr_lat)

                # Keep addresses within 1 km radius
                if distance < 1:
                    address = record.get("adresse", "Unknown Address")
                    nearest_addresses.append(address)

        if not nearest_addresses:
            return JsonResponse({"error": "No addresses found nearby."})

        return JsonResponse({"arrondissement": number, "nearest_addresses": nearest_addresses})

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)