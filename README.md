# 🏡 Apartment Recommendation System

## 📌 Overview
This project was developed as part of annual Data Science Hackathon. The goal was to build an optimization-based apartment recommendation system for the Greater Seattle Area.

## 🏆 Problem Statement
Assume you work as an FTE at Amazon's Seattle Downtown office and you also attend classes at the University of Washington campus. Find an apartment within rent and commute budget, meeting user preferences and minimizing any constraints. Our solution leverages optimization techniques and collaborative filtering to suggest top-rated apartments based on factors like:
- Rent affordability
- Transit score
- Walk score
- Safety score
- Neighbourhood score
- Amenities and user preferences

## 📊 Data Source
- We sourced our apartment listing and pricing data from [Zillow's API](https://www.zillowgroup.com/developers/public-data/).
- Places data and insights from [Google Places API](https://developers.google.com/maps/documentation/places/web-service/op-overview) to analyze nearby amenities.
- Commute distance and time from [Google Distance Matrix API](https://developers.google.com/maps/documentation/distance-matrix/overview) to calculate commute cost and assess travel feasibility.
- Crime data from the [Seattle Police Department Crime Data](https://data.seattle.gov/Public-Safety/SPD-Crime-Data-2008-Present/tazs-3rd5/about_data) to evaluate neighborhood safety.

## 🔧 Technologies Used
- **Python** (Data Processing & Modeling)
- **Streamlit** (Dashboard UI)
- **Optimization Techniques and Collaborative Filtering** (for ranking best apartments)

## 🚀 Installation & Setup
Follow these steps to set up and run the project:
1. Install dependencies
   `pip install -r requirements.txt`
2. Run the Streamlit Dashboard
   `streamlit run dashboard.py`
3. Open the browser and navigate to `http://localhost:8501/` to interact with the dashboard.
