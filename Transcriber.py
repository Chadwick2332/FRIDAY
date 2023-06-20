import os
import io
import torch
import whisper
import speech_recognition as sr
from datetime import datetime, timedelta
from queue import Queue
from tempfile import NamedTemporaryFile
from time import sleep

class Transcriber:
    def __init__(self, model="medium", non_english=False, energy_threshold=1000,
        record_timeout=2, phrase_timeout=3):
        self.model = model
        if model != "large" and not non_english:
            self.model = model + ".en"

        self.audio_model = whisper.load_model(self.model)

        self.energy_threshold = energy_threshold
        self.record_timeout = record_timeout
        self.phrase_timeout = phrase_timeout

        self.temp_file = NamedTemporaryFile().name
        self.transcription = ['']

        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = self.energy_threshold
        self.recorder.dynamic_energy_threshold = False

        self.last_sample = bytes()
        self.data_queue = Queue()
        self.phrase_time = None

        self.is_running = False

    def _record_callback(self, _, audio:sr.AudioData) -> None:
        data = audio.get_raw_data()
        self.data_queue.put(data)

    def _update_transcriptions(self):
        now = datetime.utcnow()

        if not self.data_queue.empty():
            phrase_complete = False
            if self.phrase_time and now - self.phrase_time > timedelta(seconds=self.phrase_timeout):
                self.last_sample = bytes()
                phrase_complete = True

            self.phrase_time = now

            while not self.data_queue.empty():
                data = self.data_queue.get()
                self.last_sample += data

            audio_data = sr.AudioData(self.last_sample, sr.Microphone().sample_rate, sr.Microphone().sample_width)
            wav_data = io.BytesIO(audio_data.get_wav_data())

            with open(self.temp_file, 'w+b') as f:
                f.write(wav_data.read())

            result = self.audio_model.transcribe(self.temp_file, fp16=torch.cuda.is_available())
            text = result['text'].strip()

            if phrase_complete:
                self.transcription.append(text)
            else:
                self.transcription[-1] = text

    def start(self):
        source = sr.Microphone(sample_rate=16000)

        with source:
            self.recorder.adjust_for_ambient_noise(source)

        self.recorder.listen_in_background(source, self._record_callback, phrase_time_limit=self.record_timeout)
        self.is_running = True

    def pause(self):
        self.is_running = False

    def stop(self):
        self.is_running = False
        self.recorder.stop()
        self._update_transcriptions()

    def get_transcriptions(self):
        return self.transcription

    def clear_transcriptions(self):
        self.transcription = ['']

def main():
    transcriber = Transcriber()

    transcriber.start()
    sleep(10)

    transcriber.pause()
    sleep(5)

    transcriber.start()
    sleep(10)

    transcriber.stop()

    transcriptions = transcriber.get_transcriptions()
    print(transcriptions)

if __name__ == "__main__":
    main()