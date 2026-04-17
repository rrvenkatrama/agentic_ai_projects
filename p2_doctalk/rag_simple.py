"""
  P2 DocTalk — rag_simple.py
  Concepts: chunking, embedding, retrieval (no LangChain)
"""

from openai import OpenAI
from dotenv import load_dotenv
from embed_intro import get_embedding, cosine_similarity  # reuse your work

load_dotenv()

DOCUMENT = """
Python is a high-level programming language known for its simplicity.
It was created by Guido van Rossum and released in 1991.
Python supports multiple programming paradigms including procedural and
object-oriented.
The language emphasizes code readability with significant indentation.
Python has a large standard library often described as batteries included.
Machine learning frameworks like TensorFlow and PyTorch are written in Python.
Python is widely used in data science, web development, and automation.
Django and Flask are popular Python web frameworks.
The Python Package Index (PyPI) hosts over 400,000 packages.
Python 3 was released in 2008 and is the current major version.
"""

def chunk_document(text: str, chunk_size: int = 2) -> list[str]:
     # sentences = [s.strip() for s in text.split('.') if s.strip()]
    sentences = []

    for s in text.split('.'):
      if s.strip():
        sentences.append(s.strip())

    chunks = []
    for i in range(0, len(sentences), chunk_size):
        chunk_sentences = sentences[i:i+chunk_size]
        chunk = '. '.join(chunk_sentences)
        if chunk_sentences:
            chunk += '.'
        chunks.append(chunk)
    
    return chunks

def retrieve(query: str, chunks: list[str], embeddings: list[list[float]],
               client: OpenAI, top_k: int = 2) -> list[tuple[float, str]]:
      # Embed the query
      # Score each chunk via cosine_similarity
      # Return top_k (score, chunk) tuples, sorted descending
    query_embedding = get_embedding(client, query)
    scores = []
    for chunk, embedding in zip(chunks, embeddings):    
        score = cosine_similarity(query_embedding, embedding)
        scores.append((score, chunk))
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores[:top_k]

def main():
      client = OpenAI()
      chunks = chunk_document(DOCUMENT)
      print(f"Chunks ({len(chunks)} total):")
      for i, c in enumerate(chunks):
          print(f"  [{i}] {c[:80]}")
      print()
      chunk_embeddings = [get_embedding(client, c) for c in chunks]
      query = "What programming paradigms does Python support?"
      print(f"Query: {query}\n")
      results = retrieve(query, chunks, chunk_embeddings, client)
      print("Top matches:")
      for score, chunk in results:
          print(f"  [{score:.3f}] {chunk}")

if __name__ == "__main__":
      main()