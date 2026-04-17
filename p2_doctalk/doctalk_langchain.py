import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
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
    pdf_path = "Mavic Drone Manual.pdf"
    question = "How do I return the drone to home automatically?"

    print("Building index...")
    vector_store = build_index(pdf_path)

    #     # Step 1 — wrap vector store as retriever and get docs
    # docs = vector_store.similarity_search(question, k=3)

    # # Step 2 — format docs into a context string
    # context = "\n\n---\n\n".join(
    #     f"[Page {doc.metadata.get('page', '?')}]\n{doc.page_content}"
    #     for doc in docs
    # )

    # # Step 3 — build the prompt messages manually
    # messages = [
    #     {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
    # ]

    # # Step 4 — call Claude
    # llm = ChatAnthropic(model="claude-sonnet-4-6")
    # response = llm.invoke(messages)

    # # Step 5 — extract the text
    # answer = response.content

    # print("\n--- Claude's Answer (plain Python) ---")
    # print(answer)

    # LCEL chain: retriever | prompt | llm | output parser
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Answer the question using only the context provided. Always mention which page(s) your answer comes from."),
        ("human", "Context:\n{context}\n\nQuestion: {question}")
    ])

    def format_docs(docs):
        return "\n\n---\n\n".join(
            f"[Page {doc.metadata.get('page', '?')}]\n{doc.page_content}"
            for doc in docs
        )

    llm = ChatAnthropic(model="claude-sonnet-4-6")

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print("\n--- Claude's Answer (via LangChain LCEL chain) ---")
    answer = chain.invoke(question)
    print(answer)
    
if __name__ == "__main__":    
    main()    