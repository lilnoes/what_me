import numpy as np
import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")


def getEmbedding(text):
    res = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return res["data"][0]["embedding"]


def getSimilarity(text1, text2):
    try:
        vector1 = np.array(getEmbedding(text1))
        vector2 = np.array(getEmbedding(text2))

        similarity = np.dot(vector1, vector2) / \
            (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        return similarity
    except Exception as e:
        print(f"Error getting similarity {e}")
        return 0
