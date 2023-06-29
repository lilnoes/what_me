import stream
import argparse
import asyncio
import similarity
import notification
import answer
import sys
from dotenv import load_dotenv
load_dotenv()

# parser = argparse.ArgumentParser()

# queue to store all transcribed texts as tuple(all_transcripts, transcript)
transcript_queue = asyncio.Queue()


async def topicCallback(topic, max_words=10, time=10):
    while True:
        # after every {seconds} check if the topic was mentioned
        await asyncio.sleep(time)
        (all_transcripts, transcript) = await transcript_queue.get()
        sim = similarity.getSimilarity(topic, all_transcripts[-max_words * 5:])
        if sim < 0.8:
            continue
        body = f"Your topic {topic} is being discussed.\nRecent conversation is: {transcript}"
        print(f"🟢 {body}")
        notification.sendMessage(body)


async def nameCallback(name, time=1):
    while True:
        # after each {time} seconds, check if your name was called.
        await asyncio.sleep(time)
        (all_transcripts, transcript) = await transcript_queue.get()
        if name.lower() not in transcript.lower():
            continue
        reply = answer.getAnswer(name, all_transcripts[-100 * 5:])
        print(f"🟢 Your name {name} is called.")
        print(f"🟢 Last transcribed text: {transcript}")
        notification.sendMessage(reply)


async def run(method, name, topic):
    functions = [asyncio.ensure_future(stream.run(transcript_queue))]
    if method == "name":
        functions.append(nameCallback(name))
    else:
        functions.append(topicCallback(topic))
    await asyncio.gather(*functions)


def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--name", default=None,
                            help="Your name to listen for.")
        parser.add_argument("--topic", default=None, help="Topic to look for.")
        args = parser.parse_args()
        method = "name" if args.name != None else "topic"

        if method == "name":
            print(f"🟢 Started streaming and listening for name {args.name}")
        else:
            print(f"🟢 Started streaming and listening for topic {args.topic}")

        asyncio.run(run(method, args.name, args.topic))
    except KeyboardInterrupt:
        print("🔴 Canceled")


if __name__ == "__main__":
    sys.exit(main() or 0)
