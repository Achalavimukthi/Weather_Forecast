import requests
from datetime import datetime

# Replace with your OpenWeatherMap API key
API_KEY = 'fdba23023838ed11e7e071d54b888856'

def get_weather_forecast(city_name, date):
    # URL for fetching weather forecast data from OpenWeatherMap
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric'  # Temperature in Celsius
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        # Convert the date to the format used in the API
        target_date = datetime.strptime(date, '%Y-%m-%d')
        forecast_data = {
            'temp': [],
            'rainfall': []
        }
        for item in data['list']:
            dt = datetime.utcfromtimestamp(item['dt'])
            if dt.date() == target_date.date():
                temp = item['main']['temp']
                rainfall = item.get('rain', {}).get('3h', 0)  # Rainfall in the last 3 hours
                forecast_data['temp'].append((dt, temp))
                forecast_data['rainfall'].append((dt, rainfall))
        return forecast_data
    else:
        return {'temp': [], 'rainfall': []}

def get_weather(country, state, town=None, date=None):
    # URL for fetching weather data from OpenWeatherMap
    base_url = "http://api.openweathermap.org/data/2.5/weather"

    # Function to fetch weather data from OpenWeatherMap
    def fetch_weather(city_name):
        params = {
            'q': city_name,
            'appid': API_KEY,
            'units': 'metric'  # Temperature in Celsius
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            rainfall = data.get('rain', {}).get('1h', 0)  # Rainfall in the last hour
            return temp, rainfall
        else:
            return None, None

    # Try fetching weather data for the town first
    if town:
        city_name = f"{town},{state},{country}"
        temp, rainfall = fetch_weather(city_name)
        if temp is not None and rainfall is not None:
            if date:
                forecast_data = get_weather_forecast(city_name, date)
                return temp, rainfall, forecast_data
            else:
                return temp, rainfall, None
    
    # If town data is not available, fallback to state-level data
    city_name = f"{state},{country}"
    temp, rainfall = fetch_weather(city_name)
    if date:
        forecast_data = get_weather_forecast(city_name, date)
        return temp, rainfall, forecast_data
    else:
        return temp, rainfall, None
