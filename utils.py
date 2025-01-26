import requests

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