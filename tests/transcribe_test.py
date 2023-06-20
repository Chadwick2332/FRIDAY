from Transcriber import Transcriber
from time import sleep

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