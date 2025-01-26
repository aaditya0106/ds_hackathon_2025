import folium
from optimisation import get_optimised_model
import pandas as pd

def _get_marker(ip):
    popup_html = (
            f"<b>Building:</b> {ip['buildingName']}<br>"
            f"<b>Address:</b> {ip['address']}<br>"
            f"<b>Price:</b> {ip['price']}<br>"
            f"<b>Primary Location:</b> {ip['primary_dist']} miles ({ip['distance_time_source_transit']} min)<br>"
            f"<b>Secondary Location:</b> {ip['sec_dist']} miles ({ip['distance_time_second_transit']} min)<br>"
        )
    marker = folium.Marker(
            location=(ip['latitude'], ip['longitude']),
            popup=folium.Popup(popup_html, max_width=None),
            icon=folium.Icon(color="red", icon="home"),
        )
    return marker

def get_markers(suggestions):
    m = folium.Map(location=[47.6097, -122.3331], zoom_start=13)
    for row in suggestions:
         _get_marker(row).add_to(m)
    m.save("properties_map.html")
    #folium.Marker([47.6097, -122.3331], popup="Seattle Center").add_to(m)
    return m

def get_apartments(price_range, living_area, bedrooms, bathrooms, primary_location, secondary_location, 
                   primary_visit_days, secondary_visit_days, commute_time, walking_dist, commute_type, commute_budget):
    base_data = pd.read_csv("base_data.csv")
    print(price_range)
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
    print(apts[0]['buildingName'])
    return apts