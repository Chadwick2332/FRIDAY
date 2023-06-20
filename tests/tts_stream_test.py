import requests

voice_id = "2A0V6HLMd0rFszt9RmmW"
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream?optimize_streaming_latency=0"
payload = {
    "text": """A king ruled the state in the early days.
            The ship was torn apart on the sharp reef.
            Sickness kept him home the third week.
            The wide road shimmered in the hot sun.
            The lazy cow lay in the cool grass.
            Lift the square stone over the fence.
            The rope will bind the seven books at once.
            Hop over the fence and plunge in.
            The friendly gang left the drug store.
            Mesh wire keeps chicks inside.""",
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