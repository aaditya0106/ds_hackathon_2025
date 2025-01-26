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
    img = Image.open(BytesIO(requests.get(apt["imgSrc"]).content))
    img = img.resize((660, 400))
    st.image(img)
    #st.header(f"{apt['name']} :link:")
    st.markdown(
        f"""
        <a href="{apt['url']}" target="_blank" class="dialog-link">{apt['buildingName']} 🔗</a>
        """,
        unsafe_allow_html=True,
    )
    st.write(f"**Address:** {apt['address']}")
    st.write(f"**Price:** ${int(apt['price'])}/bed")
    st.write(f"**Living Area:** {apt['livingArea']} sqft.")
    st.write(f"**Bedrooms:** {apt['bedrooms']}")
    st.write(f"**Bathrooms:** {apt['bathrooms']}")
    #st.write(f"**Amenities:** {apt['amenities']}")
    #st.write(f"**Nearest Bus Stop:** {apt['nearest_bus_stop']}")
    #st.write(f"**Nearest Train Station:** {apt['nearest_train_station']}")
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



