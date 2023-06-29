import pyaudio
import asyncio
import json
import os
import websockets
import re
from dotenv import load_dotenv

load_dotenv()

all_transcripts = ""

DEEPGRAM_API_KEY = os.environ["DEEPGRAM_API_KEY"]
DEEPGRAM_HOST = "wss://api.deepgram.com"
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 8000

audio_queue = asyncio.Queue()


def mic_callback(input_data, frame_count, time_info, status_flag):
    """
    callback called for each stream of data from the mic. It appends the stream to the queue.
    """
    audio_queue.put_nowait(input_data)
    return (input_data, pyaudio.paContinue)


async def run(transcript_queue):
    """
    Function that streams from the microphone and sends the data to Deepgram's Nova for speech-to-text.
    """
    deepgram_url = f'{DEEPGRAM_HOST}/v1/listen?punctuate=true'

    deepgram_url += f"&encoding=linear16&sample_rate={RATE}"

    # Connect to the real-time streaming endpoint, attaching our credentials.
    async with websockets.connect(deepgram_url, extra_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"}) as ws:
        async def sender(ws):
            """
            Function that sends microphone data to the Deepgram Nova server.
            """
            try:
                while True:
                    mic_data = await audio_queue.get()
                    await ws.send(mic_data)
            except websockets.exceptions.ConnectionClosedOK:
                await ws.send(json.dumps({"type": "CloseStream"}))
            except Exception as e:
                print(f"🔴 Error while sending: {str(e)}")
                raise
            return

        async def receiver(ws):
            """
            Function that receives speech-to-text transcriptions from the Deepgram Nova server.
            """
            global all_transcripts
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
                        # trim all whitespaces
                        transcript = re.sub(r"\s+", " ", transcript)
                        # print(transcript)
                        all_transcripts += transcript
                        transcript_queue.put_nowait(
                            (all_transcripts, transcript))

                except KeyError:
                    print(f"🔴 ERROR: Received unexpected API response! {msg}")

        # Set up microphone if streaming from mic
        async def microphone():
            """
            Function that sets up the microphone for streaming.
            """
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
            print("🟢 Started streaming")

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


# def main():
#     """Entrypoint for the example."""
#     asyncio.run(run())
