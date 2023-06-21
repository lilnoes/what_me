from datetime import datetime
import pyaudio
import asyncio
import aiohttp
import json
import os
import sys
import websockets
from dotenv import load_dotenv

load_dotenv()


startTime = datetime.now()

all_transcripts = ""

DEEPGRAM_API_KEY = os.environ["DEEPGRAM_API_KEY"]
DEEPGRAM_HOST = "wss://api.deepgram.com"
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 8000

audio_queue = asyncio.Queue()


# Used for microphone streaming only.
def mic_callback(input_data, frame_count, time_info, status_flag):
    audio_queue.put_nowait(input_data)
    return (input_data, pyaudio.paContinue)


async def run():
    deepgram_url = f'{DEEPGRAM_HOST}/v1/listen?punctuate=true'

    deepgram_url += f"&encoding=linear16&sample_rate={RATE}"

    # Connect to the real-time streaming endpoint, attaching our credentials.
    async with websockets.connect(deepgram_url, extra_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"}) as ws:
        async def sender(ws):
            try:
                while True:
                    mic_data = await audio_queue.get()
                    await ws.send(mic_data)
            except websockets.exceptions.ConnectionClosedOK:
                await ws.send(json.dumps({"type": "CloseStream"}))
            except Exception as e:
                print(f"Error while sending: {str(e)}")
                raise
            return

        async def receiver(ws):
            global all_transcripts
            """Print out the messages received from the server."""
            transcript = ""

            async for msg in ws:
                res = json.loads(msg)
                try:
                    if res.get("is_final"):
                        transcript = (
                            res.get("channel", {})
                            .get("alternatives", [{}])[0]
                            .get("transcript", "")
                        )
                        print(transcript)
                        all_transcripts += transcript

                except KeyError:
                    print(f"ERROR: Received unexpected API response! {msg}")

        # Set up microphone if streaming from mic
        async def microphone():
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=mic_callback,
            )

            stream.start_stream()

            global SAMPLE_SIZE
            SAMPLE_SIZE = audio.get_sample_size(FORMAT)

            while stream.is_active():
                await asyncio.sleep(0.1)

            stream.stop_stream()
            stream.close()

        functions = [
            asyncio.ensure_future(sender(ws)),
            asyncio.ensure_future(receiver(ws)),
            asyncio.ensure_future(microphone())
        ]

        await asyncio.gather(*functions)


def main():
    """Entrypoint for the example."""
    asyncio.run(run())


if __name__ == "__main__":
    sys.exit(main() or 0)
