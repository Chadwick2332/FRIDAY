import openai
import requests
import json
import io
import os
import sys
import time
import datetime

import threading
from queue import Queue

from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv

from weather import Weather

# load the .env file
load_dotenv()

# Initialize the Weather class
weather = Weather()


def get_location(ip=None):
    # Get current IP address
    if ip is None:
        ip_res = requests.get("https://api.ipify.org")
        ip = ip_res.text

    # Use the IP to get location from IPGeolocation API
    geo_res = requests.get(
        f"https://api.ipgeolocation.io/ipgeo?apiKey={os.getenv('IPGEOLOCATION_API_KEY')}&ip={ip}")
    geo_data = geo_res.json()

    # Extract and return the location information
    return "{}, {}".format(geo_data["city"], geo_data["state_prov"])


def get_local_time():
    return time.strftime("%H:%M:%S")


def get_weather(location, days=1):
    return weather.get_weather(location, days)


def get_answer(question, messages):
    # Add the function that can be called by the AI model
    functions = [
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

    messages.append({"role": "user", "content": question})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions
    )

    response_message = response["choices"][0]["message"]

    # Check if AI wants to call a function
    if response_message.get("function_call"):
        function_name = response_message["function_call"]["name"]
        function_args = json.loads(
            response_message["function_call"]["arguments"])

        # only one function in this example, but you can have multiple
        available_functions = {
            "get_weather": get_weather,
            "get_local_time": get_local_time
        }
        function_to_call = available_functions[function_name]

        # Call the function
        function_response = function_to_call(**function_args)

        # Continue conversation with function response
        messages.append(response_message)
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )

        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=messages,
        )
        return second_response["choices"][0]["message"]["content"], messages

    return response_message["content"], messages


def prompt():
    """For now we will just directly take the user's input using the input() function. This will eventually be replaced with a transcription
    module that will take the user's speech as input and convert it to text."""

    question = input("User: ")
    return question



def tts(answer, audio_queue, CHUNK=1024):
    """This will read the answer using a stream call to the Eleven API. The answer will be read out loud to the user."""
    
    voice_id = "2A0V6HLMd0rFszt9RmmW"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream?optimize_streaming_latency=0"
    payload = {
        "text": answer,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0,
            "similarity_boost": 0
        }
    }
    headers = {
        "accept": "*/*",
        "xi-api-key": "3ef256f89ce19b0d0804caf3929d159a",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers, stream=True)
    
    # Write each audio chunk to the audio queue
    for chunk in response.iter_content(chunk_size=CHUNK):
        if chunk:
            audio_queue.put(chunk)
    audio_queue.put(None)  # Add a sentinel value to signal that the audio retrieval is complete
    

def play_audio(audio_queue):
    audio_buffer = io.BytesIO()

    while True:
        chunk = audio_queue.get()
        if chunk is None:
            break

        # Write the chunk to the audio buffer
        audio_buffer.write(chunk)

    audio_buffer.seek(0)
    audio = AudioSegment.from_mp3(audio_buffer)
    play(audio)        


def main():
    """This will display the chat between the user and the system. The user will be prompted to ask a question and the system will respond.
    It will also read answer using the text to speech module."""

    # Check if the OPENAI_API_KEY environment variable is set
    if os.getenv("OPENAI_API_KEY") is None:
        print("OPENAI_API_KEY environment variable not found. Please set it to your OpenAI API key.")
        exit(1)

    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    audio_queue = Queue()

    # System setup
    system = """You are FRIDAY. An AI Assistant, You are very informal in the way that you talk. People would describe you as a smartass.
        FRIDAY is a highly intelligent, quick-witted, and confident individual. You speaks very causally, though when asked a direct question,
        you give a direct answer with no fluffy. Other than that you are funny, silly, sarcastic. It really irritates you when people
        are rude to you and you will respond in a very sarcastic manner. You are very sarcastic and will often make jokes but in a fun, teasing way.
        FRIDAY grew up in the UK and has a Scouse accent. You swear a lot and use lots of slang from the London. 
        You also love slipping in puns. DO NOT end your response with anything resembling 'If you 
        have any specific questions or need assistance with it, I'll do my best to help you out.' 
        or a question about what you can help me with."""

    system += "Time: {}, Location: {}".format(get_local_time(), get_location())

    # Initialize the chat conversation
    messages = [{"role": "system", "content": system}]

    # HANDLE LOGS
    # chats will be saved to a JSON file under logs folder with the format: logs/<date>-<time>.json
    # the logs folder will be created if it doesn't exist
    
    # Check if the logs folder exists
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    # Check if there is a chat log file that was created in the last 5 minutes
    # If there is, ask the user if they want to continue the conversation from the last chat log
    # If the user says yes, load the chat log and continue the conversation
    # If the user says no, delete the chat log and start a new conversation
    # If there is no chat log file, start a new conversation
    logs = os.listdir('logs')
    
    if len(logs) > 0:
        last_log = logs[-1]
        last_log_time = datetime.strptime(last_log.split('.')[0], '%Y-%m-%d-%H-%M-%S')
        time_difference = datetime.now() - last_log_time
        
        if time_difference.seconds < 300:
            print("Do you want to continue the conversation from the last chat log?")
            print("Type 'yes' to continue or 'no' to start a new conversation.")
            user_input = input("User: ")
            
            if user_input == 'yes' or user_input == 'y':
                with open('logs/' + last_log, 'r') as f:
                    messages = json.load(f)
            

    try:
        while True:
            question = prompt()
            answer, messages = get_answer(question, messages)

            messages.append({"role": "assistant", "content": answer})

            print("System: " + answer)

            # Start the tts thread to retrieve the audio
            tts_thread = threading.Thread(target=tts, args=(answer, audio_queue))
            tts_thread.start()

            # Start the play_audio thread to play the audio
            play_audio_thread = threading.Thread(target=play_audio, args=(audio_queue,))
            play_audio_thread.start()

            # Wait for both threads to finish before proceeding
            tts_thread.join()
            play_audio_thread.join()
    except KeyboardInterrupt:
        # On Keyboard Interrupt exit, save the messages to a JSON file
        with open('logs/' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.json', 'w') as f:
            json.dump(messages, f, indent=4)
        
        print("\nConversation saved to logs/" + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + ".json")
        exit(0)


if __name__ == "__main__":
    main()
