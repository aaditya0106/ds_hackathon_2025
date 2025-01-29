import streamlit as st
from streamlit_folium import st_folium
from PIL import Image
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO
from utils import get_nearest_place
from get_apt_suggestions import get_markers, get_apartments
from css import *

st.set_page_config(layout="wide")

######################## user filters ########################

st.sidebar.header("Filters")

price_range = st.sidebar.slider("Price Range ($):", min_value=500, max_value=1800, value=(500, 1500), step=50)
living_area = st.sidebar.slider("Living Area (sq ft):", min_value=100, max_value=2500, value=(100, 2500), step=50)
bedrooms = st.sidebar.multiselect("Number of Bedrooms:", options=[1, 2, 3, 4], default=[1, 2, 3])
bathrooms = st.sidebar.multiselect("Number of Bathrooms:", options=[1, 2, 3, 4], default=[1, 2, 3])
commute_budget = st.sidebar.slider("Commute Budget ($):", min_value=0, max_value=800, value=500, step=50)
primary_location = st.sidebar.text_input("Primary Location Address:", "440 Terry Ave N, Seattle, WA 98109")
primary_visit_days = st.sidebar.multiselect(
    "Primary Location Visit Days:", options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
)
secondary_location = st.sidebar.text_input("Secondary Location Address:", "45th Street Plaza")
secondary_visit_days = st.sidebar.multiselect(
    "Secondary Location Visit Days:", options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    default=["Wednesday", "Thursday"]
)
commute_time = st.sidebar.slider("Commute Time (minutes)(home to primary location):", min_value=0, max_value=120, value=30, step=1)
walking_dist = st.sidebar.slider("Walking DIstance (miles)(home to primary location):", min_value=0.0, max_value=3.0, value=1.0, step=0.1)
transport_mode = st.sidebar.radio("Mode of transportation:", ("Transit", "Vehicle"), index = 1)

######################## apt suggestions and details ########################

st.title("RentWise - Smarter and optimized rental decisions")

st.markdown(card_css, unsafe_allow_html=True)
st.markdown(wide_dialog_css, unsafe_allow_html=True)

######################## apt details ########################

def _show_apt_img(apt):
    if apt.get("imgSrc"):
        img = Image.open(BytesIO(requests.get(apt["imgSrc"]).content))
        img = img.resize((810, 400))
        st.image(img)

def _show_apt_name(apt):
    name = apt.get("buildingName") or "Apartment"
    url = apt.get("url") or "#"
    st.markdown(
        f"""
            <h1><a href="https://zillow.com{url}" target="_blank" 
                style="text-decoration: none; color: black;"> {name} 🔗
            </a></h1>
        """,
        unsafe_allow_html=True,
    )

def _show_price(apt):
    price = int(apt["price"])
    st.write(f"**Price:** ${price}")

def _show_address(apt):
    address = apt.get("streetAddress") or apt.get("address") or "N/A"
    st.write(f"**Address:** {address}")

def _show_living_area(apt):
    liv_area = apt.get("livingArea")
    st.write(f"**Living Area:** {liv_area} sq ft")

def _show_bed_bath(apt):
    beds = int(apt.get("bedrooms", 1))
    baths = int(apt.get("bathrooms", 1))
    st.write(f"**Bedrooms/Bathrooms:** {beds} / {baths}")

def _show_prop_type(apt):
    prop_type = apt.get("propertyTypeDimension") or "N/A"
    st.write(f"**Property Type:** {prop_type}")

def _show_transit_dist(apt):
    distance_transit = apt.get("distance_time_source_transit", "N/A")
    distance_transit = eval(distance_transit)
    if isinstance(distance_transit, dict):
        distance_transit = f'{distance_transit['distance']} miles ({distance_transit['duration']} mins)'
    st.write(f"**Est. Commute (Transit):** {distance_transit}")

def _show_vehicle_dist(apt):
    distance_vehicle = apt.get("distance_time_source_vehicle", "N/A")
    distance_vehicle = eval(distance_vehicle)
    if isinstance(distance_vehicle, dict):
        distance_vehicle = f'{distance_vehicle['distance']} miles ({distance_vehicle['duration']} mins)'
    st.write(f"**Est. Commute (Vehicle):** {distance_vehicle}")

def _show_monthly_commute_cost(apt):
    monthly_commute_transit = apt.get("total_commute_cost_tranist", "N/A")
    st.write(f"**Monthly Commute Cost (Transit):** ${round(monthly_commute_transit)}")

def _show_monthly_vehicle_cost(apt):
    monthly_commute_vehicle = apt.get("total_commute_cost_vehicle", "N/A")
    st.write(f"**Monthly Commute Cost (Vehicle):** ${round(monthly_commute_vehicle)}")

def _show_parking_details(apt):
    parking = apt.get("parkingFeatures", "Unknown")
    if not parking or parking == "{}":
        parking = "Unknown"
    if parking != 'Unknown':
        parking = ', '.join(eval(parking))
    st.write(f"**Parking:** {parking}")

def _show_security_details(apt):
    security = apt.get("securityFeatures", "Unknown")
    if pd.isna(security):
        security = "Unknown"
    if security != 'Unknown':
        security = ', '.join(eval(security))
    st.write(f"**Security Features:** {security}")

def _show_furnishing(apt):
    furnished = apt.get("furnished", "False")
    st.write(f"**Furnished:** {furnished}")

def _show_garage(apt):
    has_garage = apt.get("hasGarage", "False")
    st.write(f"**Has Garage:** {has_garage}")

def _show_laundry(apt):
    laundry = apt.get("laundryFeatures", [])
    if pd.isna(laundry):
        laundry = []
    laundry = ', '.join(eval(laundry)) if laundry else "Unknown"
    st.write(f"**Laundry Features:** {laundry}")

def _show_safety_score(apt):
    safety_score = apt.get("safety_score", "N/A")
    if isinstance(safety_score, float):
        safety_score = round(safety_score) * 100
    else:
        safety_score = eval(safety_score)
    st.write(f"**Safety Score:** {safety_score}%")

def _show_transit_score(apt):
    walkscore = eval(apt.get("walk_score", "N/A"))
    transit_score = str(walkscore['transitScore']['transit_score'])+"%" #if isinstance(walk_score, dict) else "N/A"
    st.write(f"**Transit Score:** {transit_score}")

def _show_walk_score(apt):
    walkscore = eval(apt.get("walk_score", "N/A"))
    walk_score = str(walkscore['walkScore']['walkscore']) + "%"  # if isinstance(walk_score, dict) else "N/A"
    st.write(f"**Walk Score:** {walk_score}")

def _show_apt_desc(apt):
    description = apt.get("description")
    if description:
        with st.expander("Description"):
            st.write(description)

def _show_amenities(apt):
    amenities = apt.get("associationAmenities", "Unknown")
    if pd.isna(amenities):
        amenities = "Unknown"
    exterior = apt.get("exteriorFeatures", "Unknown")
    if not exterior or exterior == '{}':
        exterior = 'Unknown'
    if not amenities != 'Unknown' and exterior != 'Unknown':
        with st.expander("Amenities & Exterior Features"):
            st.write(f"**Amenities:** {amenities}")
            exterior = ', '.join(eval(exterior))
            st.write(f"**Exterior Features:** {exterior}")

def _show_nearby_places(apt):
    schools = apt.get("schools")
    schools = eval(schools) if schools else schools
    bus_station = get_nearest_place(apt['latitude'], apt['longitude'], 'bus_station')
    train_station = get_nearest_place(apt['latitude'], apt['longitude'], 'train_station')
    restaurant = get_nearest_place(apt['latitude'], apt['longitude'], 'restaurant')
    pharmacy = get_nearest_place(apt['latitude'], apt['longitude'], 'pharmacy')
    with st.expander("Nearby Places"):
        if bus_station:
            st.markdown(f"🚍 **{bus_station['name']}** {bus_station['address']} ({bus_station['dist']:.2f} miles)")
        if train_station:
            st.markdown(f"🚊 **{train_station['name']}** {train_station['address']} ({train_station['dist']:.2f} miles)")
        if restaurant:
            st.markdown(f"🥣 **{restaurant['name']}** {restaurant['address']} ({restaurant['dist']:.2f} miles)")
        if pharmacy:
            st.markdown(f"💊 **{pharmacy['name']}** {pharmacy['address']} ({pharmacy['dist']:.2f} miles)")
        if schools:
            st.markdown(f"🏫 [**{schools['name']}**]({schools['link']}) ({schools['distance']:.2f} miles)")

def _show_price_history(apt):
    price_history = apt.get("priceHistory", None)
    if price_history:
        price_history = pd.DataFrame(eval(price_history))
        price_history['date'] = pd.to_datetime(price_history['date'])
        with st.expander("Price History"):
            fig = px.line(price_history, x='date', y='price', title='Price Change History')
            st.plotly_chart(fig)

@st.dialog("Apartment Details")
def show_apartment_details(apt):
    _show_apt_img(apt)
    _show_apt_name(apt)
    _show_address(apt)

    c1,c2 = st.columns(2)
    with c1:
        _show_price(apt)
        _show_living_area(apt)
        _show_transit_dist(apt)
        _show_monthly_commute_cost(apt)
        _show_parking_details(apt)
        _show_furnishing(apt)
        _show_laundry(apt)
        _show_walk_score(apt)
        
    with c2:
        _show_bed_bath(apt)
        _show_prop_type(apt)
        _show_vehicle_dist(apt)
        _show_monthly_vehicle_cost(apt)
        _show_security_details(apt)
        _show_garage(apt)
        _show_safety_score(apt)
        _show_transit_score(apt)

    _show_apt_desc(apt)
    _show_amenities(apt)
    _show_nearby_places(apt)
    _show_price_history(apt)
    st.html("<span class='big-dialog'></span>")


######################## apt suggestions ########################

apartments = get_apartments(price_range, living_area, bedrooms, bathrooms, primary_location, secondary_location, 
                   primary_visit_days, secondary_visit_days, commute_time, walking_dist, transport_mode, commute_budget)

col1, col2 = st.columns([1, 1], gap="medium")
with col1:
    with st.container():
        folium_obj = get_markers(apartments, transport_mode)
        st_folium(folium_obj, width=500, height=700)

with col2:
    if not apartments:
        st.write('No listings found. Try again with different filters.')
    else:
        for i, apt in enumerate(apartments):
            with st.container():
                st.html(apt_css(apt))
                if st.button("Details", key=f"details_{i}"):
                    show_apartment_details(apt)



