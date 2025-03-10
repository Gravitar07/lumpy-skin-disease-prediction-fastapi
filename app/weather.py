import requests
from typing import Optional, Tuple
from .config import WEATHER_API_KEY

# Use the API key from config
API_KEY = WEATHER_API_KEY

def get_temperature_by_coords(lat: float, lon: float) -> Optional[float]:
    """Get current temperature for given coordinates"""
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return data["main"]["temp"]
        return None
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def get_city_by_coords(lat: float, lon: float) -> Optional[str]:
    """Get city name for given coordinates"""
    url = f"https://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data:
            return data[0]["name"]
        return None
    except Exception as e:
        print(f"Error fetching location data: {e}")
        return None 