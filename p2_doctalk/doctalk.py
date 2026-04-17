import os
import anthropic
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


load_dotenv()
def main():
    def build_index(pdf_path):
        loader = PyPDFLoader(pdf_path)
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

        return vector_store
    def retrieve(vector_store, question, k=3):

        results = vector_store.similarity_search_with_score(question, k=k)
        return results
    def format_context(results):
        context = ""
        for i, (doc, score) in enumerate(results):
            context += f"[Page: {doc.metadata.get('page', '?')}, score: {score:.4f}]\n"
            context += f"Result {i+1}: {doc.page_content[:200]}...\n\n"
        return context
    def ask_claude(question, context):
        
        client = anthropic.Anthropic()
        response = client.messages.create(model="claude-sonnet-4-6", 
            max_tokens=1024, 
            system="You are a helpful assistant. Answer the question using only the context provided. Always mention which page(s) your answer comes from.",
            messages=[{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ])
        return response.content[0].text
    
    pdf_path = "Mavic Drone Manual.pdf"
    question = "How do I return the drone to home automatically?"

    print("Building index...")
    vector_store = build_index(pdf_path)

    print("Retrieving relevant chunks...")
    results = retrieve(vector_store, question)

    context = format_context(results)

    print("\n--- Retrieved Context ---")
    print(context)

    print("\n--- Claude's Answer ---")
    answer = ask_claude(question, context)
    print(answer)
    
if __name__ == "__main__":    
    main()    