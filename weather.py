import os
import json
import requests

from dotenv import load_dotenv

# load the .env file
load_dotenv()


class Weather:
    """This class will implement calls to the Weather API to get the current weather in a given location. The API key will be stored in the .env file.
    It will also return have calls related to the weather, such as getting the forecast for the next 5 days, when the sun will rise and set, etc."""

    def __init__(self):
        """Initialize the class with the API key and the base URL for the API."""
        # http://api.weatherapi.com/v1/forecast.json?key=8cb9b608d5074260be0220343231706&q=London&days=1&aqi=no&alerts=no
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "http://api.weatherapi.com/v1/"

    def get_weather(self, location, days=1):
        """Get the current weather in a given location. The default number of days is 1.
        The response will be trimmed to only include the relevant information.
        """

        url = f"{self.base_url}forecast.json?key={self.api_key}&q={location}&days={days}&aqi=no&alerts=no"
        response = requests.get(url)

        # Assuming the original response is stored in the 'response' variable
        jsonRes = response.json()

        trimmedRes = {}

        # Modify the location object
        trimmedRes['location'] = {
            'name': jsonRes['location']['name'],
            'region': jsonRes['location']['region'],
            'country': jsonRes['location']['country'],
            'localtime': jsonRes['location']['localtime']
        }

        # Modify the current object
        trimmedRes['current'] = {
            'last_updated': jsonRes['current']['last_updated'],
            'temp_c': jsonRes['current']['temp_c'],
            'temp_f': jsonRes['current']['temp_f'],
            'condition': jsonRes['current']['condition'],
            'humidity': jsonRes['current']['humidity'],
            'cloud': jsonRes['current']['cloud'],
            'feelslike_c': jsonRes['current']['feelslike_c'],
            'feelslike_f': jsonRes['current']['feelslike_f']
        }

        # Modify the forecast object
        trimmedRes['forecast'] = [
            {
                'date': jsonRes['forecast']['forecastday'][0]['date'],
                'day': {
                    'maxtemp_c': jsonRes['forecast']['forecastday'][0]['day']['maxtemp_c'],
                    'maxtemp_f': jsonRes['forecast']['forecastday'][0]['day']['maxtemp_f'],
                    'mintemp_c': jsonRes['forecast']['forecastday'][0]['day']['mintemp_c'],
                    'mintemp_f': jsonRes['forecast']['forecastday'][0]['day']['mintemp_f'],
                    'avgtemp_c': jsonRes['forecast']['forecastday'][0]['day']['avgtemp_c'],
                    'avgtemp_f': jsonRes['forecast']['forecastday'][0]['day']['avgtemp_f'],
                    'maxwind_mph': jsonRes['forecast']['forecastday'][0]['day']['maxwind_mph'],
                    'maxwind_kph': jsonRes['forecast']['forecastday'][0]['day']['maxwind_kph'],
                    'totalprecip_mm': jsonRes['forecast']['forecastday'][0]['day']['totalprecip_mm'],
                    'totalprecip_in': jsonRes['forecast']['forecastday'][0]['day']['totalprecip_in'],
                    'totalsnow_cm': jsonRes['forecast']['forecastday'][0]['day']['totalsnow_cm'],
                    'avghumidity': jsonRes['forecast']['forecastday'][0]['day']['avghumidity'],
                    'daily_will_it_rain': jsonRes['forecast']['forecastday'][0]['day']['daily_will_it_rain'],
                    'daily_chance_of_rain': jsonRes['forecast']['forecastday'][0]['day']['daily_chance_of_rain'],
                    'daily_will_it_snow': jsonRes['forecast']['forecastday'][0]['day']['daily_will_it_snow'],
                    'daily_chance_of_snow': jsonRes['forecast']['forecastday'][0]['day']['daily_chance_of_snow'],
                    'condition': jsonRes['forecast']['forecastday'][0]['day']['condition']
                },
                'astro': {
                    'sunrise': jsonRes['forecast']['forecastday'][0]['astro']['sunrise'],
                    'sunset': jsonRes['forecast']['forecastday'][0]['astro']['sunset'],
                    'moon_phase': jsonRes['forecast']['forecastday'][0]['astro']['moon_phase'],
                },

            }
        ]

        return json.dumps(trimmedRes)


if __name__ == "__main__":
    weather = Weather()

    print(weather.get_weather("Boston"))
