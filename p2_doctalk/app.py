import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import anthropic
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

load_dotenv()

app = FastAPI()

# In-memory store: session_id → vector_store
sessions = {}

class AskRequest(BaseModel):
    session_id: str
    question: str

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
    <body>
      <h2>DocTalk — PDF Q&A</h2>

      <h3>Step 1: Upload a PDF</h3>
      <form id="uploadForm">
        <input type="file" id="pdfFile" accept=".pdf" />
        <button type="button" onclick="uploadPDF()">Upload</button>
      </form>
      <p id="uploadStatus"></p>

      <h3>Step 2: Ask a question</h3>
      <input type="text" id="question" size="60" placeholder="Ask something about the PDF..." />
      <button onclick="askQuestion()">Ask</button>
      <pre id="answer"></pre>

      <script>
        let sessionId = null;

        async function uploadPDF() {
          const file = document.getElementById('pdfFile').files[0];
          const form = new FormData();
          form.append('file', file);
          const res = await fetch('/upload', { method: 'POST', body: form });
          const data = await res.json();
          sessionId = data.session_id;
          document.getElementById('uploadStatus').innerText = 'Uploaded! Session: ' + sessionId;
        }

        async function askQuestion() {
          const question = document.getElementById('question').value;
          const res = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, question: question })
          });
          const data = await res.json();
          document.getElementById('answer').innerText = data.answer;
        }
      </script>
    </body>
    </html>
    """

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    tmp_path = f"/tmp/{file.filename}"
    with open(tmp_path, "wb") as f:
        f.write(await file.read())

    # Index the PDF — same pipeline as doctalk.py
    loader = PyPDFLoader(tmp_path)
    documents = loader.load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(documents)

    client = QdrantClient(":memory:")
    client.create_collection(
        collection_name="docs",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = QdrantVectorStore(client=client, collection_name="docs", embedding=embedding)
    vector_store.add_documents(chunks)

    # Store vector store under a new session ID
    session_id = str(uuid.uuid4())
    sessions[session_id] = vector_store

    return {"session_id": session_id, "chunks": len(chunks)}

@app.post("/ask")
async def ask(request: AskRequest):
    vector_store = sessions.get(request.session_id)
    if not vector_store:
        raise HTTPException(status_code=404, detail="Session not found. Upload a PDF first.")

    # Retrieve relevant chunks
    results = vector_store.similarity_search_with_score(request.question, k=3)

    # Format context
    context = "\n\n---\n\n".join(
        f"[Page {doc.metadata.get('page', '?')}, score: {score:.4f}]\n{doc.page_content}"
        for doc, score in results
    )

    # Call Claude
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="You are a helpful assistant. Answer the question using only the context provided. Always mention which page(s) your answer comes from.",
        messages=[{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {request.question}"}]
    )

    return {"answer": response.content[0].text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)