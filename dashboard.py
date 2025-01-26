import streamlit as st
from streamlit_searchbox import st_searchbox
from streamlit_folium import st_folium
from PIL import Image
import requests
from io import BytesIO
from utils import get_autocomplete_suggestions
from get_apt_suggestions import get_markers, get_apartments
st.set_page_config(layout="wide")
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

transport_mode = st.sidebar.radio(
    "Mode of transportation:",
    ("Transit", "Vehicle"), index = 1
)

######################## apt suggestions ########################
st.title("Suggested Apartments")
col1, col2 = st.columns(2)

card_css = """
<style>
.card {
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 10px;
    box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.1);
    background-color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: transform 0.1s ease-in-out, box-shadow 0.1s ease-in-out;
}
.card:hover {
    transform: scale(1.02);
    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2);
}
.card img {
    width: 80px;
    height: auto;
    border-radius: 5px;
}
.card-content {
    flex: 3;
    text-align: left;
}
.card-image {
    flex: 1;
    text-align: right;
}
.details-button {
    margin-top: 10px;
    background-color: #007bff;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 5px;
    font-size: 14px;
    cursor: pointer;
}
.details-button:hover {
    background-color: #0056b3;
}
</style>
"""
st.markdown(card_css, unsafe_allow_html=True)
st.markdown(
    """
    <style>
        div[data-testid="stDialog"] div[role="dialog"]:has(.big-dialog) {
            width: 50vw;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.dialog("Apartment Details")
def show_apartment_details(apt):
    # Load and resize image (imgSrc -> your image URL field)
    if apt.get("imgSrc"):
        img = Image.open(BytesIO(requests.get(apt["imgSrc"]).content))
        img = img.resize((660, 400))
        st.image(img)

    # Title / hyperlink to listing
    # buildingName or some custom name field
    apt_name = apt.get("buildingName") or "Apartment"
    listing_url = apt.get("url") or "#"
    st.markdown(
        f"""
            <a href="https://zillow.com{listing_url}" target="_blank" class="dialog-link">{apt_name} 🔗</a>
        """,
        unsafe_allow_html=True,
    )

    # Basic details
    address = apt.get("streetAddress") or apt.get("address") or "N/A"
    price = apt.get("price") or "N/A"
    st.write(f"**Address:** {address}")
    st.write(f"**Price:** {price}")

    # Beds / Baths
    beds = apt.get("bedrooms") or apt.get("beds") or "N/A"
    baths = apt.get("bathrooms") or "N/A"
    st.write(f"**Bedrooms/Bathrooms:** {beds} / {baths}")

    # Additional property details
    #year_built = apt.get("yearBuilt") or "N/A"
    living_area = apt.get("livingArea") or "N/A"
    prop_type = apt.get("propertyTypeDimension") or "N/A"
    #st.write(f"**Year Built:** {year_built}")
    st.write(f"**Living Area:** {living_area} sq ft")
    st.write(f"**Property Type:** {prop_type}")

    # Commute or distance info (if applicable)
    distance_transit = apt.get("distance_time_source_transit", "N/A")
    distance_vehicle = apt.get("distance_time_source_vehicle", "N/A")
    st.write(f"**Est. Commute (Transit):** {distance_transit}")
    st.write(f"**Est. Commute (Vehicle):** {distance_vehicle}")

    # Monthly commute cost (if available)
    monthly_commute_vehicle = apt.get("total_commute_cost_vehicle", "N/A")
    monthly_commute_transit = apt.get("total_commute_cost_tranist", "N/A")
    st.write(f"**Monthly Commute Cost (Vehicle):** {monthly_commute_vehicle}")
    st.write(f"**Monthly Commute Cost (Transit):** {monthly_commute_transit}")

    # Scores
    walk_score = apt.get("walk_score", "N/A")
    walk_score = walk_score['walkScore']['walkscore'] if isinstance(walk_score, dict) else "N/A"
    transit_score = apt.get("walk_score", "N/A")
    transit_score = transit_score['transitScore']['transit_score'] if isinstance(transit_score, dict) else "N/A"
    safety_score = apt.get("safety_score", "N/A")
    if isinstance(safety_score, float):
        safety_score = round(safety_score, 2)*100

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Walk Score:** {walk_score}")
    with col2:
        st.write(f"**Transit Score:** {transit_score}")
    with col3:
        st.write(f"**Safety Score:** {safety_score}%")

    # Amenities (includes associationAmenities, external features, etc.)
    amenities = apt.get("associationAmenities", "")
    exterior = apt.get("exteriorFeatures", "")
    with st.expander("Amenities & Exterior Features"):
        if amenities:
            st.write(f"**Amenities:** {amenities}")
        if exterior:
            st.write(f"**Exterior Features:** {exterior}")

    # Parking and security info
    parking = apt.get("parkingFeatures", "N/A")
    security = apt.get("securityFeatures", "N/A")
    st.write(f"**Parking:** {parking}")
    st.write(f"**Security Features:** {security}")

    # Other details
    furnished = apt.get("furnished")
    has_garage = apt.get("hasGarage")
    laundry = apt.get("laundryFeatures")
    st.write(f"**Furnished:** {furnished}")
    st.write(f"**Has Garage:** {has_garage}")
    st.write(f"**Laundry Features:** {laundry}")

    # Price history (if any)
    price_history = apt.get("priceHistory", None)
    if price_history:
        with st.expander("Price History"):
            st.write(price_history)

    # Description
    description = apt.get("description")
    if description:
        with st.expander("Description"):
            st.write(description)

    # Schools
    schools = apt.get("schools")
    if schools:
        with st.expander("Nearby Schools"):
            st.write(schools)

    # Mark end of the big dialog
    st.html("<span class='big-dialog'></span>")


with col1:
    with st.container():
        folium_obj = get_markers([])
        st_folium(folium_obj, width=500, height=700)

with col2:
    st.markdown(card_css, unsafe_allow_html=True)
    apartments = get_apartments(price_range, living_area, bedrooms, bathrooms, primary_location, secondary_location, 
                   primary_visit_days, secondary_visit_days, commute_time, walking_dist, transport_mode, commute_budget)
    print(apartments[0]['buildingName'])
    for i, apt in enumerate(apartments):
        with st.container():
            st.html(
                f"""
                <div class="card">
                    <div class="card-content">
                        <strong>{apt['buildingName']}</strong><br>
                        {apt['address']}<br>
                        <strong>Price:</strong> ${int(apt['price'])}/bed
                    </div>
                    <div class="card-image">
                        <img src="{apt['imgSrc']}" alt="Apartment Image">
                    </div>
                </div>
                """
            )
            
            if st.button("Details", key=f"details_{i}"):
                show_apartment_details(apt)



