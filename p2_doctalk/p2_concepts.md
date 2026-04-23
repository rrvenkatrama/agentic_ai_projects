# P2 DocTalk — Concepts Guide
> Built from real questions asked during the project. Each section = a question that came up while coding.

---

## What is an embedding?

An embedding is a way to represent text as a list of numbers (a vector) such that **similar meanings end up close together** in that numeric space.

- Input: a string — `"The cat sat on the mat."`
- Output: a list of floats — `[0.023, -0.417, 0.891, ...]` (1536 numbers for `text-embedding-3-small`)

The numbers themselves are meaningless in isolation. What matters is the *relationship* between vectors. Two sentences with similar meaning produce vectors that point in nearly the same direction.

---

## Do I need to understand the math inside `client.embeddings.create()`?

No. For building RAG systems and agentic applications, you need to understand:

- **Input:** a string
- **Output:** a list of floats (a vector)
- **What the vector represents:** the string's position in a high-dimensional semantic space

The internals (transformer attention layers, tokenization, projection heads) are ML research territory. You don't need them to build production RAG pipelines.

What you *do* need to understand:
- Vectors from the same model can be compared meaningfully
- Vectors from different models cannot be mixed
- Cosine similarity measures the angle between two vectors = semantic similarity

---

## Do all models produce the same embeddings?

**No — each model produces completely incompatible vectors.**

| Model | Dimensions | Notes |
|---|---|---|
| OpenAI `text-embedding-3-small` | 1536 | Good quality, low cost |
| OpenAI `text-embedding-3-large` | 3072 | Higher quality, higher cost |
| Google `text-embedding-004` | 768 | Google's space |
| `all-MiniLM-L6-v2` (local) | 384 | Free, runs locally |
| `nomic-embed-text` (Ollama) | 768 | Free, runs locally via Ollama |
| **Anthropic Claude** | — | **No public embedding API** — Claude does text generation only |

"The cat sat on the mat" produces completely different numbers in OpenAI vs Google vs local models. The *relationships* may be structurally similar (cats and felines still end up close), but the actual coordinate values are totally different and incomparable.

---

## Can I mix models — embed documents with one model and queries with another?

**No. This is a hard rule: you must use the same model for both indexing and querying.**

**Why:** Each model creates its own "map" of semantic space. OpenAI places "cat" at certain coordinates in *its* space. A local model places "cat" at completely different coordinates in *its* space. If you embed your documents using OpenAI and embed a search query using a local model, the cosine similarity scores are meaningless — you're comparing GPS coordinates from two different planets.

```
✅ Correct:
  Index documents  → text-embedding-3-small
  Embed query      → text-embedding-3-small  (same model)

❌ Wrong:
  Index documents  → text-embedding-3-small
  Embed query      → all-MiniLM-L6-v2        (different model — results are garbage)
```

**Practical rule:** Choose your embedding model once, at the start of a project. Store which model you used alongside your vector database. Never change models without re-embedding all documents.

---

## Do I always need an API call to create embeddings?

No. There are two approaches:

### API-based (what P2 uses)
```python
response = client.embeddings.create(input=text, model="text-embedding-3-small")
vector = response.data[0].embedding
```
- Runs on remote server
- Costs per token
- High quality
- Requires internet + API key

### Local models (no API, no cost)
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
vector = model.encode("The cat sat on the mat")  # runs on your machine
```
- Runs locally, no API key, no cost
- Good for privacy-sensitive documents (nothing leaves your machine)
- Slightly lower quality than top commercial models
- Also available via Ollama: `ollama pull nomic-embed-text`

**P2 uses OpenAI API** because quality is better for a first RAG project and setup is simpler. Local embeddings appear in later projects when cost/privacy matters.

---

## What is cosine similarity and why does it work?

Cosine similarity measures the **angle** between two vectors in high-dimensional space, not the distance.

```
cosine_similarity(a, b) = dot(a, b) / (magnitude(a) * magnitude(b))
```

**Why angle, not distance?**
Without dividing by magnitudes, a long document (many words, larger raw values) would always score higher than a short one — purely due to size, not meaning. Dividing by magnitude normalizes both vectors to unit length. Now you're only measuring *direction* (= meaning), not *size* (= how much text).

**Why it returns 1.0 for identical vectors:**
Two identical vectors point in exactly the same direction. The angle between them is 0°. cos(0°) = 1.0. This is guaranteed by the math regardless of the actual values in the vector.

**Score interpretation:**
| Score | Meaning |
|---|---|
| 1.0 | Identical (or perfectly parallel) |
| 0.8–0.9 | Very similar meaning |
| 0.5–0.7 | Related topic |
| 0.1–0.3 | Unrelated |
| 0.0 | Completely orthogonal (no relationship) |
| < 0 | Opposite meaning (rare in practice) |

---

## What is RAG?

**RAG = Retrieval Augmented Generation**

**The problem it solves:** LLMs don't know your private documents. You can't fit a 100-page PDF into a prompt. RAG is the standard solution.

**Core idea:** Before asking the LLM a question, find the relevant parts of your document first, then send only those parts to the LLM.

### The two phases

```
INDEXING (done once, upfront)          QUERYING (done per user question)
──────────────────────────────         ─────────────────────────────────
Document                               User question
    │                                      │
    ▼                                      ▼
Split into chunks                    Embed the question
    │                                      │
    ▼                                      ▼
Embed each chunk                     Compare against all chunk embeddings
    │                                      │
    ▼                                      ▼
Store in vector DB                   Find top-K most similar chunks
                                           │
                                           ▼
                                     Send chunks + question → LLM
                                           │
                                           ▼
                                        Answer (with citations)
```

### Why chunks, not the full document?

- Embedding APIs have token limits
- A small focused chunk scores *higher* similarity than a large unfocused one
- You want precision — find the 2–3 sentences that actually answer the question, not the whole document

### Why this matters for DocTalk

DocTalk (P2) lets you chat with a PDF using exactly this pipeline:
- PDF → chunks → embed → store in Qdrant (vector DB)
- User question → embed → find similar chunks → Claude answers with citations

`rag_simple.py` is the raw version of this pipeline with no libraries — so you understand what LangChain and Qdrant are actually doing under the hood.

---

---

## What do you embed — sentences, paragraphs, or full documents?

**You almost never embed individual sentences or full documents. You embed *chunks*.**

A chunk is a contiguous piece of text — typically 3–10 sentences or 256–512 tokens. The extremes both fail:

| Granularity | Problem |
|---|---|
| Single sentences | Too little context. "It was released in 1991." — released *what*? Not retrievable. |
| Full document / page | Too much noise. 500 sentences averaged into one vector — the specific answer gets diluted. |
| **Chunks (sweet spot)** | Self-contained enough to make sense. Small enough to score high against a focused query. |

---

## How do you determine chunk size for a PDF?

### Step 1: Look at the document's natural structure

| Document type | Natural chunk boundary |
|---|---|
| Legal contracts | Clauses / numbered sections |
| Research papers | Paragraphs (each makes one point) |
| Technical manuals | Sections with headers |
| FAQ pages | One Q&A pair per chunk |
| Code documentation | One function/class description |

**Rule of thumb: chunk at semantic boundaries, not arbitrary character counts.**

### Step 2: The self-contained test

Read a chunk in isolation. Ask: *"If someone asked a question answered by this chunk, would this chunk alone make sense as an answer?"*

- Yes → chunk size is right
- Too vague → chunk too small, merge with neighbors
- Too many topics → chunk too large, split further

### Step 3: The 256–512 token starting point

If you don't know the document well, start with **256–512 tokens with ~50 token overlap**.

```
Chunk 1: tokens 0–256
Chunk 2: tokens 206–462   ← 50-token overlap with chunk 1
Chunk 3: tokens 412–668   ← 50-token overlap with chunk 2
```

**Why overlap?** Answers often straddle chunk boundaries. Overlap ensures the answer isn't split and lost.

### Step 4: Validate with a retrieval test

Run 5 representative queries you'd expect users to ask. Check if top-2 retrieved chunks actually contain the answer. If not — chunk size is wrong. Adjust and re-embed.

### LangChain's RecursiveCharacterTextSplitter (used in DocTalk)

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # target tokens per chunk
    chunk_overlap=50,     # overlap between chunks
    separators=["\n\n", "\n", ". ", " "]  # tries these in order
)
chunks = splitter.split_text(full_document_text)
```

Tries to split on paragraph breaks first (`\n\n`), then line breaks, then sentences, then words — preserving semantic boundaries as much as possible.

### Chunking decision tree

```
Does the doc have clear sections/headers?
    YES → split on headers (semantic chunking)
    NO  → Is it dense technical text?
              YES → 256 tokens, 50 overlap
              NO  → 512 tokens, 50 overlap

Always: run a retrieval test with real queries and adjust if top results miss the answer.
```

---

---

## Python: `zip()`

Pairs up two (or more) lists element by element, stopping at the shortest.

```python
chunks     = ["chunk A", "chunk B", "chunk C"]
embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]

for chunk, embedding in zip(chunks, embeddings):
    print(chunk, embedding)
# chunk A [0.1, 0.2]
# chunk B [0.3, 0.4]
# chunk C [0.5, 0.6]
```

**Why it's useful in RAG:** chunks and their embeddings are always parallel lists — same index, same item. `zip` lets you iterate both together cleanly without index math (`chunks[i]`, `embeddings[i]`).

Without `zip`:
```python
for i in range(len(chunks)):
    score = cosine_similarity(query_vec, embeddings[i])
    scores.append((score, chunks[i]))
```

With `zip` (cleaner):
```python
for chunk, embedding in zip(chunks, embeddings):
    score = cosine_similarity(query_vec, embedding)
    scores.append((score, chunk))
```

---

## Python: `lambda`

A one-line anonymous function. Used when you need a simple function in one place and don't want to name it.

```python
# Regular function
def get_score(x):
    return x[0]

# Same thing as a lambda
get_score = lambda x: x[0]
```

**Most common use: as a `key=` argument to `sort()` or `sorted()`**

```python
scores = [(0.44, "chunk B"), (0.73, "chunk A"), (0.12, "chunk C")]

# Sort by the first element (the score)
scores.sort(key=lambda x: x[0], reverse=True)
# → [(0.73, "chunk A"), (0.44, "chunk B"), (0.12, "chunk C")]
```

`key=lambda x: x[0]` means: *"for each item `x` in the list, use `x[0]` as the sort value"*

**In `retrieve()`**, this is how the top chunks are found:
```python

 # highest score first
return scores[:top_k]                            # take top 2
```

**Rule of thumb:** use `lambda` only for simple one-liners. If the logic is more than one expression, write a proper `def`.

---

---

## What is the full RAG loop with generation? (doctalk.py)

The full pipeline adds an LLM at the end of retrieval:

```
PDF → chunks → embeddings → Qdrant → similarity search → format context → Claude → cited answer
```

The key addition is **context injection** — the retrieved chunks are formatted into a text block with page numbers and scores, then sent to Claude as part of the prompt. Claude's system prompt instructs it to only use the provided context and to cite page numbers.

This is what makes RAG answers **grounded**: Claude cannot hallucinate because it's explicitly told to use only what was retrieved. Every claim traces back to a specific page.

---

## What goes in the system prompt for a RAG pipeline?

Minimal but effective:
```
"You are a helpful assistant. Answer the question using only the context provided. 
Always mention which page(s) your answer comes from."
```

Two critical instructions:
1. **"Only the context provided"** — prevents hallucination
2. **"Mention which page(s)"** — forces Claude to use the page metadata you injected

---

## Why are nested functions inside `main()` not ideal?

In doctalk.py, `build_index`, `retrieve`, `format_context`, and `ask_claude` are defined inside `main()`. This works, but the better pattern is to define them at module level:

- Module-level functions can be imported and reused in other files
- Easier to test individually
- Cleaner to read

Nested functions are fine for quick scripts, but for production code define them at module level.

---

## LangChain package split — why so many packages?

LangChain split its monolithic package into sub-packages so you only install what you need:

| Package | Contents |
|---|---|
| `langchain` | Core abstractions, chains, agents |
| `langchain-community` | Community-contributed integrations (PyPDFLoader etc.) |
| `langchain-text-splitters` | Text splitting utilities |
| `langchain-openai` | OpenAI wrappers (co-maintained with OpenAI) |
| `langchain-qdrant` | Qdrant integration (maintained by Qdrant team) |

The `langchain-<provider>` naming is used by both LangChain and external providers — check PyPI for the actual maintainer.

---

---

## What does `similarity_search_with_score()` actually do at call time?

Two things happen inside this one call:

1. **OpenAI API call** — embeds the *question string* into a 1536-float vector
2. **Qdrant search** — compares that query vector against all stored chunk vectors using cosine similarity, returns top-k matches

The chunk embeddings were already stored during `add_documents()` earlier. `similarity_search_with_score()` only embeds the *query* — not the chunks again.

**Common mistake:** thinking this call embeds the chunks. It doesn't. Chunks are embedded once at index time. The query is embedded once at search time.

---

*Updated: 2026-04-09 — P2 DocTalk complete, quiz 6.5/8*
