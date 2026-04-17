from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from dotenv import load_dotenv
import os

load_dotenv()

def main():

    loader = PyPDFLoader("Mavic Drone Manual.pdf")
    document = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(document)
    print(f"Number of chunks: {len(chunks)}")

    client = QdrantClient(":memory:")
    client.create_collection(
        collection_name="docs",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=os.getenv("OPENAI_API_KEY"))
    vector_store = QdrantVectorStore(client, collection_name="docs", embedding=embeddings)
    vector_store.add_documents(chunks)  

    results = vector_store.similarity_search_with_score("How do I take off with the Mavic drone?", k=3)
    for i, (doc, score) in enumerate(results):
        print(f"Score: {score:.4f}")
        print(f"Page: {doc.metadata.get('page', '?')}")
        print(f"Result {i+1}: {doc.page_content[:200]}...")

if __name__ == "__main__":
    main()  