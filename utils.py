import requests
import math

api_key = 'AIzaSyAvesyp1z_BijIwRNIftwyWU7S0ToBCI6s'

def get_autocomplete_suggestions(input_text):
    if not input_text:
        return []
    url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json?input={input_text}&key={api_key}&types=address"
    response = requests.get(url)
    #print(response.json())
    if response.status_code == 200:
        predictions = response.json().get("predictions", [])
        predictions = [prediction["description"] for prediction in predictions]
        return predictions
    else:
        return []

def get_coordinates_from_place_id(place_id):
    base_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "key": api_key,
        "place_id": place_id,
        "fields": "geometry"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        location = data['result']['geometry']['location']
        return location.get("lat"), location.get("lng")
    else:
        return None, None

def get_approx_dist(lat1, lng1, placeid):
    lat2, lng2 = get_coordinates_from_place_id(placeid)
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat, dlng = lat2 - lat1, lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    dist = 3958.8 * c
    return dist

def get_nearest_place(lat, lng, place_type):
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": api_key,
        "location": f"{lat},{lng}",
        "rankby": "distance",
        "type": place_type
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        if results:
            nearest = results[0]
            name = nearest.get("name")
            address = nearest.get("vicinity")
            place_id = nearest.get("place_id")
            dist = get_approx_dist(lat, lng, place_id)
            return {
                "name": name,
                "address": address,
                "place_id": place_id,
                "dist": dist
            }
        else:
            return None
    else:
        raise Exception(f"Request failed with status code {response.status_code}.")
