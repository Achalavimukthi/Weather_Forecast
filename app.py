import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from model import get_weather

# Initialize geolocator for reverse geocoding
geolocator = Nominatim(user_agent="geoapiExercises")

# Function to get location details
def get_location_details(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), language='en', exactly_one=True)
        address = location.raw.get('address', {})
        country = address.get('country', 'Unknown')
        state = address.get('state', 'Unknown')
        town = address.get('town', 'Unknown') or address.get('city', 'Unknown')
        return country, state, town
    except Exception as e:
        return "Unknown", "Unknown", "Unknown"

# Function to create a folium map with a given zoom level
def create_map(lat, lon, zoom_start):
    m = folium.Map(location=[lat, lon], zoom_start=zoom_start)
    folium.Marker([lat, lon], popup=f"Location: {lat}, {lon}", icon=folium.Icon(color='red')).add_to(m)
    return m

# Define pages
def show_intro_page():
    st.title('Weather Forecast Application')
    st.write("""
    Welcome to the Weather Forecast Application!

    This application provides comprehensive weather forecasting features powered by OpenWeatherMap. Whether you're planning a trip, preparing for an event, or just curious about the weather, this app has got you covered.

    ## Features

    - **Current Weather Data**: Get the latest weather information for any location.
    - **Hourly Forecast**: Access detailed hourly weather forecasts for the next 48 hours.
    - **Daily Forecast**: View daily weather forecasts up to 7 days in advance.
    - **Weather Alerts**: Receive notifications for severe weather conditions and alerts.
    - **Geocoding**: Convert city names to geographic coordinates and vice versa for accurate location-based data.
    - **Historical Weather Data**: Limited access to past weather data for various locations.

    ## Limitations

    - **API Rate Limits**: The free plan has restrictions on the number of API requests you can make per minute or per day.
    - **Data Refresh Rate**: Data updates may be less frequent compared to paid plans.
    - **Data Access**: Advanced features and detailed data are available only with premium plans.
    - **Limited Access to Premium APIs**: Some specialized services may not be included in the free plan.
    - **Data Accuracy and Availability**: Data quality may vary, especially for less common or remote locations.

    ## How to Use

    1. Navigate to the **Weather Forecast** page to select a location by clicking on the map.
    2. Choose a date to view the weather forecast for that specific day.
    3. The application will display the current weather conditions, temperature, rainfall, and forecast data.

    Enjoy exploring the weather forecasts with ease!
    """)

def show_weather_page():
    st.title('Weather Forecast Application')
    st.write("Click on the map to select a location:")

    # Initialize map
    map_center = [20, 0]
    m = folium.Map(location=map_center, zoom_start=2)

    # Display the map in Streamlit and let users click to select a location
    location_map = st_folium(m, width=700, height=500)

    if location_map['last_clicked'] is not None:
        lat = location_map['last_clicked']['lat']
        lon = location_map['last_clicked']['lng']
        
        # Get location details
        country, state, town = get_location_details(lat, lon)
        
        # Update the map with the selected location
        zoom_level = 12  # Adjust this zoom level as needed
        m = create_map(lat, lon, zoom_level)
        
        # Display the updated map with the marker
        location_map = st_folium(m, width=700, height=500)
        
        # Show selected location details and weather forecast results
        st.write(f"Selected Location:")
        st.write(f"Country: {country}")
        st.write(f"State: {state}")
        st.write(f"Town: {town}")
        
        # Allow user to choose a date
        date = st.date_input('Select date')
        
        # Get weather forecast from model.py
        temp, rainfall, forecast_data = get_weather(country, state, town, date.strftime('%Y-%m-%d'))
        
        # Display current weather data
        if temp is not None and rainfall is not None:
            st.write(f"Current Weather in {town}, {state}, {country}:")
            st.write(f"Current Temperature: {temp:.2f}°C")
            st.write(f"Current Rainfall: {rainfall:.2f} mm")
            
            if forecast_data:
                # Convert forecast data to DataFrame
                import pandas as pd
                
                temp_df = pd.DataFrame(forecast_data['temp'], columns=['Time', 'Temperature'])
                rainfall_df = pd.DataFrame(forecast_data['rainfall'], columns=['Time', 'Rainfall'])
                
                st.write("Temperature Forecast:")
                st.line_chart(temp_df.set_index('Time'))
                
                st.write("Rainfall Forecast:")
                st.line_chart(rainfall_df.set_index('Time'))
        else:
            st.write("Unable to fetch weather data for the selected location. Fetching data for the state...")
            temp, rainfall, forecast_data = get_weather(country, state, None, date.strftime('%Y-%m-%d'))
            if temp is not None and rainfall is not None:
                st.write(f"Current Weather in {state}, {country}:")
                st.write(f"Current Temperature: {temp:.2f}°C")
                st.write(f"Current Rainfall: {rainfall:.2f} mm")
                
                if forecast_data:
                    # Convert forecast data to DataFrame
                    import pandas as pd
                    
                    temp_df = pd.DataFrame(forecast_data['temp'], columns=['Time', 'Temperature'])
                    rainfall_df = pd.DataFrame(forecast_data['rainfall'], columns=['Time', 'Rainfall'])
                    
                    st.write("Temperature Forecast:")
                    st.line_chart(temp_df.set_index('Time'))
                    
                    st.write("Rainfall Forecast:")
                    st.line_chart(rainfall_df.set_index('Time'))
            else:
                st.write("Unable to fetch weather data for the selected state.")
    else:
        st.write("Click on the map to select a location.")

# Page navigation
PAGES = {
    "Introduction": show_intro_page,
    "Weather Forecast": show_weather_page
}

st.sidebar.image("bg/bg.jpg", use_column_width=True)
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

page = PAGES[selection]
page()
