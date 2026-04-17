"""
P2 DocTalk — embed_intro.py
Concepts: embeddings, cosine similarity, OpenAI embeddings API
"""
import os
import math
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_embedding(client: OpenAI, text: str) -> list[float]:
    # Call client.embeddings.create()
    # model: "text-embedding-3-small"
    # Return: response.data[0].embedding
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding

def cosine_similarity(a: list[float], b: list[float]) -> float:
    # dot product / (magnitude_a * magnitude_b)
    # use math.sqrt and a loop — no numpy
    # dot product of a and b in a loop
    if len(a) != len(b):
        raise ValueError("Lists must have the same length")
    dot = 0   
    mag_a = 0
    mag_b = 0

    for i in range(len(a)):
         dot += a[i] * b[i]
         mag_a += a[i] ** 2
         mag_b += b[i] ** 2

    mag_a = math.sqrt(mag_a)
    mag_b = math.sqrt(mag_b)

    if mag_a == 0 or mag_b == 0:
       raise ValueError("Magnitude of one vector is zero")

    return dot / (mag_a * mag_b)


def main():
    client = OpenAI()
    sentences = [
        "The cat sat on the mat.",
        "A feline rested on a rug.",
        "The stock market crashed today.",
        "Machine learning uses neural networks.",
    ]
    print("Embedding 4 sentences with text-embedding-3-small...\n")
    embeddings = [get_embedding(client, s) for s in sentences]
    print(f"Embedding dimension: {len(embeddings[0])}\n")
    print("Cosine Similarity Matrix:")
    print(f"{'':>45}", end="")
    for i in range(len(sentences)):
        print(f"  [{i}]", end="")
    print()
    for i, (s1, e1) in enumerate(zip(sentences, embeddings)):
        print(f"[{i}] {s1[:40]:40}", end="")
        for j, e2 in enumerate(embeddings):
            sim = cosine_similarity(e1, e2)
            print(f"  {sim:.2f}", end="")
        print()

if __name__ == "__main__":
    main()
    