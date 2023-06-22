import stream
import argparse
import asyncio
import similarity
import sys
from dotenv import load_dotenv
load_dotenv()

# parser = argparse.ArgumentParser()

transcript_queue = asyncio.Queue()


async def topicCallback(topic, max_words=10, time=30):
    while True:
        await asyncio.sleep(time)
        (all_transcripts, transcript) = await transcript_queue.get()
        sim = similarity.getSimilarity(topic, all_transcripts[-max_words * 5:])
        return sim


async def triggerCallback(trigger, time=1):
    while True:
        await asyncio.sleep(time)
        (all_transcripts, transcript) = await transcript_queue.get()
        if trigger.lower() not in transcript.lower():
            continue


async def test1(time, text):
    while True:
        transcript_queue.put_nowait((1, 10))
        await asyncio.sleep(time)
        (_, d) = await transcript_queue.get()
        print(f"got {d}")


async def run(method, trigger, topic):
    functions = [asyncio.ensure_future(stream.run(transcript_queue))]
    if method == "trigger":
        functions.append(triggerCallback(trigger))
    else:
        functions.append(topicCallback(topic))
    await asyncio.gather(*functions)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--word", default=None, help="Trigger word")
    parser.add_argument("--topic", default=None, help="Topic to look for")
    args = parser.parse_args()
    method = "trigger" if args.word != None else "topic"
    asyncio.run(run(method, args.word, args.topic))


if __name__ == "__main__":
    sys.exit(main() or 0)
