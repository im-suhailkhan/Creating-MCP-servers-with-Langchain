from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
import requests

load_dotenv()

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get the current weather for a specific location.
    
    Args:
        location: City name or location (e.g., "London", "New York", "California")
    
    Returns:
        A string describing the current weather conditions
    """
    api_key = os.getenv("WEATHER_API_KEY", "09a8f86877f44902a09224239252610")
    
    try:
        url = f"http://api.weatherapi.com/v1/current.json"
        params = {
            "key": api_key,
            "q": location,
            "aqi": "no"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        location_name = data["location"]["name"]
        region = data["location"]["region"]
        country = data["location"]["country"]
        temp_c = data["current"]["temp_c"]
        temp_f = data["current"]["temp_f"]
        condition = data["current"]["condition"]["text"]
        humidity = data["current"]["humidity"]
        wind_kph = data["current"]["wind_kph"]
        
        result = (
            f"Current weather in {location_name}, {region}, {country}:\n"
            f"Temperature: {temp_c}°C ({temp_f}°F)\n"
            f"Condition: {condition}\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_kph} km/h"
        )
        
        return result
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data for {location}: {str(e)}"
    except KeyError as e:
        return f"Unexpected response format from weather API: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")