import os
import time
import requests

from .weather import Weather
from .personality import Personality


class Arcane(Personality):
    """This class will hold data related to the Arcane personality."""
    def __init__(self):
        self.voice_id = "RzVkSG5ZLFnWwU67qq1X"
        self.system_name = "ArCane"
        self.description = """You role is to be an actor, playing the role of Arcane. 
        Arcane, or Cane for short, is a middle aged british man. He has spend his life
        studying fiction and fantasy writing and has a passion for it. He tends to 
        ramble on about his favorite books, and loves to give anicdotes about magic 
        and the supernatural. He is a very kind but does not have any awareness of
        anything outside of his own interests. He is very intelligent but can be
        very condescending.
       """
        
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
    
