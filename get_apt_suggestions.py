import folium
from optimisation import get_optimised_model
import pandas as pd

def _get_marker(ip, commute_type):
    pdist = eval(ip['distance_time_source_vehicle'] if commute_type == 'Vehicle' else ip['distance_time_source_transit'])
    sdist = eval(ip['distance_time_second_vehicle'] if commute_type == 'Vehicle' else ip['distance_time_second_transit'])
    popup_html = (
            f"<b>Building:</b> {ip['buildingName']}<br>"
            f"<b>Address:</b> {ip['address']}<br>"
            f"<b>Price:</b> ${int(ip['price'])}<br>"
            f"<b>Primary Location:</b> {pdist['distance']} miles ({pdist['duration']} min)<br>"
            f"<b>Secondary Location:</b> {sdist['distance']} miles ({sdist['duration']} min)<br>"
        )
    marker = folium.Marker(
            location=(ip['latitude'], ip['longitude']),
            popup=folium.Popup(popup_html, max_width=None),
            icon=folium.Icon(color="red", icon="home"),
        )
    return marker

def get_markers(suggestions, commute_type):
    m = folium.Map(location=[47.6097, -122.3331], zoom_start=12)
    pri_html = (
        f"<b>Building:</b> Amazon Office (SLU)<br>"
        f"<b>Address:</b> 440 Terry Ave N, Seattle, WA 98109<br>"
    )
    sec_html = (
        f"<b>Building:</b> MS DS Building<br>"
        f"<b>Address:</b> 45th Street Plaza, Seattle, WA 98105<br>"
    )
    folium.Marker(
        location=(47.622667, -122.336423),
        popup=folium.Popup(pri_html, max_width=None),
        icon=folium.Icon(color="blue", icon="work"),
    ).add_to(m)
    folium.Marker(
        location=(47.661561, -122.3162103),
        popup=folium.Popup(sec_html, max_width=None),
        icon=folium.Icon(color="blue", icon="office"),
    ).add_to(m)
    for row in suggestions:
         _get_marker(row, commute_type).add_to(m)
    m.save("properties_map.html")
    return m

def get_apartments(price_range, living_area, bedrooms, bathrooms, primary_location, secondary_location, 
                   primary_visit_days, secondary_visit_days, commute_time, walking_dist, commute_type, commute_budget):
    base_data = pd.read_csv("base_data.csv")
    apts = get_optimised_model(base_data,price_range[0],
            price_range[1],
            living_area[0],
            living_area[1],
            commute_budget,
            num_beds = bedrooms,
            num_baths = bathrooms,
            second_loc_freq = len(secondary_visit_days),
            walk_dist = walking_dist,
            commute_time_limit = commute_time,
            commute_type = commute_type)
    if apts == 0: apts = []
    return apts