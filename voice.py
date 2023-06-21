import requests
import io
import os
import time
import threading
from queue import Queue, Empty

# Audio
from pydub import AudioSegment
from pydub.playback import play

class Voice:
    def __init__(self, voice_id):
        self.voice_id = voice_id
        self.url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream?optimize_streaming_latency=0"
        
        self.model_id = "eleven_monolingual_v1"
        self.voice_settings = {"stability": 0.5, "similarity_boost": 0.7}
        self.XI_API_KEY = "3ef256f89ce19b0d0804caf3929d159a"
        
        self.text_queue = Queue()
        self.audio_queue = Queue()
        
        self.end_sentinel = object()
        
    def add_text(self, text):
        self.text_queue.put(text)
        
    def start(self):
        producer = threading.Thread(target=self.produce_audio, daemon=True)
        consumer = threading.Thread(target=self.consume_audio, daemon=True)
        
        producer.start()
        consumer.start()
        
        
    def produce_audio(self):
        while True:
            text = self.text_queue.get(block=True)
            if text is self.end_sentinel:
                break

            response = self.get_audio(text)

            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    self.audio_queue.put(chunk)
            self.audio_queue.put(None)
            self.text_queue.task_done()
            
    def consume_audio(self):
        while True:
            audio_buffer = io.BytesIO()

            while True:
                try:
                    chunk = self.audio_queue.get(timeout=1)
                except Empty:
                    if self.text_queue.unfinished_tasks == 0 and self.audio_queue.empty():
                        break
                    continue

                if chunk is None:
                    break
                audio_buffer.write(chunk)

            audio_buffer.seek(0)
            if audio_buffer.getbuffer().nbytes > 0:
                audio = AudioSegment.from_mp3(audio_buffer)
                play(audio)
                time.sleep(0.5)
        
    def get_audio(self, text):
        payload = {"text": text, "model_id": self.model_id, "voice_settings": self.voice_settings}
        headers = {"accept": "*/*", "xi-api-key": self.XI_API_KEY, "Content-Type": "application/json"}
        response = requests.post(self.url, json=payload, headers=headers, stream=True)
        
        return response

if __name__ == "__main__":
    voice = Voice("2A0V6HLMd0rFszt9RmmW")
    voice.start()
    
    voice.add_text("Hello, there! We are just doing a quick test of the voice class. Standby!")
    
    print("Done!")
