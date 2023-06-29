import os
import openai
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def getAnswer(name, text):
    """
    Function that uses chatgpt api to get the answer on your behalf
    in case your name was called.
    """
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            temperature=0.3,
            messages=[
                {"role": "system", "content":
                 f"You are an assistant who is attending a zoom meeting on behalf of the user."
                 f"Your name is {name}. Whenever your name is called out, you need to answer the question"
                 "you are asked concisely and straight to the point and give a very short answer."
                 "Answer using only provided information. If the answer is not in the provided text. Ask to repeat the question."
                 },
                {"role": "user", "content": f"This is a transcribed text from the meeting: ***{text}***."
                 f"Answer the question asked to {name} using only the provided text or ask for clarifications."
                 "Make your answer as short as possible."
                 "Give your answer in the format ***answer:..., summary:... where summary is the summary of the provided text."
                 "summary should not exceed 200 characters."
                 }
            ]
        )

        return completion.choices[0].message["content"]
    except Exception as e:
        print(f"Error {e}")
        return ""
