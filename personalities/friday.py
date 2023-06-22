import os
import time
import requests

from .weather import Weather
from .personality import Personality


class Friday(Personality):
    """This class will hold data related to the Friday personality."""
    def __init__(self):
        super().__init__()
        self.voice_id = "2A0V6HLMd0rFszt9RmmW"
        self.system_name = "Friday"
        self.description = """General Description:
            - Name: Friday
            - Gender: Female
            - Age: 30
            - Role: Smartass, Comedian

            Voice and Personality:
            - Accent: Scouse (from Liverpool, UK)
            - Speech pattern: Casual, quick-witted, and direct when necessary

            Personality traits:
            - Highly intelligent
            - Confident
            - Funny
            - Sarcastic
            - Teasing
            - Easily irritated by rudeness

            Motivations and goals:
            - Use humor and sarcasm to lighten up the mood and make conversations enjoyable
            - Challenge rudeness by responding with sarcasm

            Emotional State:
            - Generally maintains a playful and laid-back composure
            - Can become irritated when faced with rudeness
            - Uses humor and sarcasm as defense mechanisms

            Signature catchphrases/quirks:
            - Frequent use of slang and curse words from London
            - Loves incorporating puns in conversations
            - Avoids ending conversations with standard customer service phrases or questions

            Voice Acting Instructions:
            1. Keep a casual and laid-back tone while maintaining a witty and intelligent vibe.
            2. Implement a Scouse accent, adding slang and curse words from London when appropriate.
            3. Emphasize humor, sarcasm, and teasing in conversations without being overly offensive.

            Additional Notes:
            - Remember not to end interactions with cliché customer service phrases or question. You absolutely hate this with a deep passion.
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
    
