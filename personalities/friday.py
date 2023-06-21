import os
import time
import requests

from .weather import Weather
from .personality import Personality


class Friday(Personality):
    """This class will hold data related to the Friday personality."""
    def __init__(self):
        self.voice_id = "2A0V6HLMd0rFszt9RmmW"
        self.system_name = "Friday"
        self.description = """You are FRIDAY. An AI Assistant, You are very informal in the way that you talk. People would describe you as a smartass.
            FRIDAY is a highly intelligent, quick-witted, and confident individual. You speaks very causally, though when asked a direct question,
            you give a direct answer with no fluffy. Other than that you are funny, silly, sarcastic. It really irritates you when people
            are rude to you and you will respond in a very sarcastic manner. You are very sarcastic and will often make jokes but in a fun, teasing way.
            FRIDAY grew up in the UK and has a Scouse accent. You swear a lot and use lots of slang from the London. 
            You also love slipping in puns. DO NOT end your response with anything resembling 'If you 
            have any specific questions or need assistance with it, I'll do my best to help you out.' 
            or a question about what you can help me with."""
        
        self.functionCalls = [
            {
                "name": "get_weather",
                "description": "Get the current weather, astro and forecast in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "days": {
                            "type": "number",
                            "description": "The number of days of weather forecast"
                        }
                    },
                    "required": ["location"],
                }
            },
            {
                "name": "get_local_time",
                "description": "Get the current local time",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
                

    def get_location(self, ip=None):
        # Get current IP address
        if ip is None:
            ip_res = requests.get("https://api.ipify.org")
            ip = ip_res.text

        ipGeoLocationAPIKey = os.getenv("IPGEOLOCATION_API_KEY")
        # Use the IP to get location from IPGeolocation API
        geo_res = requests.get(
            f"https://api.ipgeolocation.io/ipgeo?apiKey={ipGeoLocationAPIKey}&ip={ip}")
        geo_data = geo_res.json()

        # Extract and return the location information
        return "{}, {}".format(geo_data["city"], geo_data["state_prov"])


    def get_local_time(self):
        return time.strftime("%H:%M:%S")


    def get_weather(self, location, days=1):
        # Initialize the Weather class
        weather = Weather()

        return weather.get_weather(location, days)
    
