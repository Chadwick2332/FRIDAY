
from pydub import AudioSegment
from pydub.playback import play
import io
import requests

# the same setup as before
voice_id = "2A0V6HLMd0rFszt9RmmW"
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream?optimize_streaming_latency=0"
payload = {
    "text": "Hello, and welcome to the beach house!",
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

response = requests.post(url, json=payload, headers=headers)

# assuming the response content is an MP3 file
audio_data = response.content

# create a file-like object from the data
audio_file = io.BytesIO(audio_data)

# load audio to pydub
audio = AudioSegment.from_mp3(audio_file)

# play the audio
play(audio)