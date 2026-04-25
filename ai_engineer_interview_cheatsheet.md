# AI Engineer Interview Cheatsheet
> Updated as projects progress. Covers concepts, patterns, and gotchas.

---

## Pydantic v2

### What it is
Runtime data validation library. Define a typed schema, Pydantic validates incoming data against it.

### BaseModel
```python
from pydantic import BaseModel

class WeatherInput(BaseModel):
    city: str               # required
    units: str = "celsius"  # optional, has default
```
- Annotations (`city: str`) are stored in `__annotations__` at class definition time
- Pydantic reads those and auto-generates `__init__`, type checking, and validation
- Fields end up as **instance variables**, not class variables

### field_validator
```python
from pydantic import field_validator

@field_validator("units")
@classmethod
def check_units(cls, v: str) -> str:
    if v not in ("celsius", "fahrenheit"):
        raise ValueError("must be celsius or fahrenheit")
    return v  # return value is used as the final field value
```
- Runs before the object is created — no instance exists yet, so `@classmethod` is required
- `v` = the value being validated
- Return the value (can transform it, e.g. `return v.lower()`)

### ValidationError
```python
from pydantic import ValidationError

try:
    validated = WeatherInput(**raw_input)
except ValidationError as e:
    return f"Invalid arguments: {e}"
```
- Raised when type check or field_validator fails
- Always catch at system boundaries (external data, LLM output)

### model_dump()
```python
validated = WeatherInput(city="London", units="celsius")
validated.model_dump()
# → {"city": "London", "units": "celsius"}
```
- Converts Pydantic object → plain dict
- Use `**validated.model_dump()` to unpack as function kwargs

---

## Claude API — tool_use

### How tool_use works (the loop)
```
You → Claude (messages + tools list)
Claude → stop_reason="tool_use"   # wants to call a tool
You → execute tool, collect result
You → Claude (messages + tool result)
Claude → stop_reason="end_turn"   # gives final answer
```
Repeat if Claude calls multiple tools in sequence.

### stop_reason values
| Value | Meaning |
|---|---|
| `"end_turn"` | Claude is done, final answer ready |
| `"tool_use"` | Claude wants to call one or more tools |
| `"max_tokens"` | Hit token limit before finishing |

### Tool schema (JSON Schema)
```python
{
    "name": "get_weather",
    "description": "Get current weather for a city.",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name"},
            "units": {"type": "string", "enum": ["celsius", "fahrenheit"]},
        },
        "required": ["city"],
    },
}
```
- `description` is critical — Claude uses it to decide when to call the tool
- `required` lists mandatory fields; omitted fields use defaults

### Tool result message format
```python
{"role": "user", "content": [
    {
        "type": "tool_result",
        "tool_use_id": block.id,   # must match the tool_use block id
        "content": "result string",
    }
]}
```
- Tool results go back as role `"user"` — not `"assistant"`
- `tool_use_id` links result to the specific tool call Claude made

### TOOL_MAP pattern
```python
TOOL_MAP = {
    "get_weather": (get_weather_fn, WeatherInput),
    "calculator":  (calculator_fn,  CalculatorInput),
}

def execute_tool(name, raw_input):
    fn, schema_cls = TOOL_MAP[name]
    validated = schema_cls(**raw_input)   # Pydantic validates
    return fn(**validated.model_dump())   # call with clean args
```
- Single dispatch point for all tools
- Keeps validation and dispatch logic in one place

---

## Streaming (Anthropic SDK)

### Non-streaming vs streaming
```python
# Non-streaming — waits for full response
response = client.messages.create(model=..., ...)

# Streaming — prints word by word
with client.messages.stream(model=..., ...) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    response = stream.get_final_message()  # same structure as non-streaming
```
- `get_final_message()` must be called **inside** the `with` block
- Returns same object as `messages.create()` — `.stop_reason`, `.content` all available
- `end=""` prevents newline per token; `flush=True` forces immediate output

### When to stream vs not
- Stream the **final text response** to the user (better UX)
- The tool loop itself works the same — `stop_reason` and `content` come from `get_final_message()`

---

## Python Concepts (relevant to agentic code)

### async/await
```python
async def run_agent(message: str) -> None:
    response = await some_async_call()

asyncio.run(main())   # entry point for async programs
```
- `async def` marks a coroutine — must be awaited or run via `asyncio.run()`
- Lets I/O-bound work (API calls) run without blocking

### @classmethod vs instance method
```python
class Foo:
    def instance_method(self):    # receives object instance
        ...
    @classmethod
    def class_method(cls):        # receives the class itself
        ...
```
- Used in Pydantic validators because no instance exists yet at validation time

### **kwargs unpacking
```python
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}")

d = {"name": "Rajesh", "greeting": "Hi"}
greet(**d)   # same as greet(name="Rajesh", greeting="Hi")
```

---

## System Prompts

### What it is
A permanent instruction given to the LLM **before** the conversation starts. The user never sees it.
Sets persona, constraints, tool guidance, output format, and context for the entire session.

### Mental model
Like a job briefing you give an employee before their first day.
User messages are the work requests that come in after.

### Anthropic — separate `system` parameter
```python
client.messages.create(
    model="claude-opus-4-6",
    system="You are ToolBot, a helpful assistant...",  # ← separate param
    messages=[{"role": "user", "content": "..."}]
)
```

### OpenAI — inside messages list as role "system"
```python
client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are ToolBot..."},  # ← first message
        {"role": "user", "content": "..."}
    ]
)
```

### Gemini — passed in GenerateContentConfig
```python
client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents,
    config=types.GenerateContentConfig(
        system_instruction="You are ToolBot...",  # ← config param
        tools=TOOLS
    )
)
```

### What to put in a system prompt
| Purpose | Example |
|---|---|
| Persona | "You are a senior financial analyst" |
| Constraints | "Never discuss competitor products" |
| Tool guidance | "Always use the calculator tool for math, never compute yourself" |
| Output format | "Respond in bullet points, max 3 bullets" |
| Context | "You are helping Apple employees with internal IT issues" |

### Key gotcha — Anthropic vs OpenAI placement
- Anthropic: `system=` is a **separate top-level parameter**, not in messages list
- OpenAI: system prompt is `{"role": "system", ...}` as the **first item in messages**
- Gemini: `system_instruction=` inside `GenerateContentConfig`

---

## Context Management + Multi-Turn Memory

### The problem
If `messages = []` is created inside `run_agent()`, history resets on every call.
The agent has no memory of previous turns.

### The fix — lift messages to main()
```python
async def run_agent(user_message: str, messages: list) -> None:
    messages.append({"role": "user", "content": user_message})
    # ... rest of loop unchanged

async def main() -> None:
    messages = []   # lives here — persists across all turns
    while True:
        user_input = input("You: ")
        await run_agent(user_input, messages)
```

### Context window limits — simple truncation
```python
MAX_MESSAGES = 20

# After each run_agent call:
if len(messages) > MAX_MESSAGES:
    messages = messages[-MAX_MESSAGES:]  # keep most recent N messages
```

### Why truncation is tricky with tool loops
Tool calls add multiple messages per turn (user → assistant → tool_result → assistant).
Truncating mid-tool-call can corrupt the history.
Safe approach: truncate only after a full turn completes (after `end_turn`).

### Better strategies (for later projects)
| Strategy | How |
|---|---|
| Simple truncation | Keep last N messages (what we do in P1) |
| Token-budget trimming | LangGraph `trim_messages()` — respects token limits |
| Summarization | Use Claude Haiku to summarize old turns into one message |
| Sliding window | Keep system + first N + last M messages |

---

## Message History Pattern
```python
messages = [{"role": "user", "content": user_message}]

# After Claude responds:
messages.append({"role": "assistant", "content": response.content})

# After tool execution:
messages.append({"role": "user", "content": tool_results})
```
- Claude sees the full history on every API call — stateless API, stateful client
- Never mutate existing messages — always append

---

## Anthropic vs OpenAI — Side by Side

### Client setup
```python
# Anthropic
import anthropic
client = anthropic.Anthropic()

# OpenAI
from openai import OpenAI
client = OpenAI()
```

### Tool schema format
```python
# Anthropic
{
    "name": "get_weather",
    "description": "...",
    "input_schema": {           # ← key is "input_schema"
        "type": "object",
        "properties": { ... },
        "required": ["city"],
    }
}

# OpenAI
{
    "type": "function",         # ← extra wrapper
    "function": {
        "name": "get_weather",
        "description": "...",
        "parameters": {         # ← key is "parameters"
            "type": "object",
            "properties": { ... },
            "required": ["city"],
        }
    }
}
```

### API call
```python
# Anthropic
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=TOOLS,
    messages=messages,
)

# OpenAI
response = client.chat.completions.create(
    model="gpt-4o",
    max_tokens=1024,
    tools=TOOLS,
    messages=messages,
)
```

### Streaming
```python
# Anthropic
with client.messages.stream(model=..., ...) as stream:
    for text in stream.text_stream:          # text_stream gives strings directly
        print(text, end="", flush=True)
    response = stream.get_final_message()    # ← get_final_message()

# OpenAI
with client.chat.completions.stream(model=..., ...) as stream:
    for event in stream:                     # yields typed events, not strings
        if event.type == "content.delta":
            print(event.delta, end="", flush=True)
    response = stream.get_final_completion() # ← get_final_completion()
```

### Stop/finish reason
```python
# Anthropic
response.stop_reason == "end_turn"    # done
response.stop_reason == "tool_use"    # wants tools

# OpenAI
response.choices[0].finish_reason == "stop"        # done
response.choices[0].finish_reason == "tool_calls"  # wants tools
```

### Accessing tool calls
```python
# Anthropic — iterate response.content blocks
for block in response.content:
    if block.type == "tool_use":
        name = block.name
        args = block.input          # already a dict
        id   = block.id

# OpenAI — iterate message.tool_calls
for tool_call in response.choices[0].message.tool_calls:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)  # JSON string → dict
    id   = tool_call.id
```

### Feeding tool results back
```python
# Anthropic — single "user" message with list of results
messages.append({
    "role": "user",
    "content": [
        {"type": "tool_result", "tool_use_id": id, "content": result}
    ]
})

# OpenAI — one "tool" message per result
messages.append({"role": "assistant", "content": ..., "tool_calls": [...]})
messages.append({"role": "tool", "tool_call_id": id, "content": result})
```

### Accessing final text
```python
# Anthropic
for block in response.content:
    if hasattr(block, "text"):
        print(block.text)

# OpenAI
print(response.choices[0].message.content)
```

### Key gotcha — OpenAI streaming events
OpenAI's `stream()` context manager yields typed **event objects**, not raw text.
- `event.type == "content.delta"` → text chunk, access via `event.delta`
- `event.type == "chunk"` → raw chunk object, access via `event.chunk`
- Unlike Anthropic, there is no `text_stream` shortcut

---

## Gemini (google-genai SDK)

### Setup
```python
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
```

### Tool definition — two approaches

**Option 1: Pass Python functions directly (new SDK feature)**
```python
TOOLS = [get_weather, calculator, get_time]
```
The SDK uses Python's `inspect` module to read:
- Function name → tool name
- Parameter names + type hints → schema
- Docstring → description (CRITICAL — without it Gemini guesses from name only)

**Option 2: Explicit schema (like Anthropic/OpenAI)**
```python
# Not needed with new SDK — use docstrings on functions instead
```

### Always add docstrings when passing functions as tools
```python
def get_time(timezone: str = "UTC") -> str:
    """Get the current date and time for a given timezone.

    Args:
        timezone: IANA timezone name e.g. 'America/New_York'. Defaults to UTC.
    """
```
Without a docstring, Gemini only knows the function name and parameter names.
It will guess — and guess wrong on ambiguous or complex tools.

### API call
```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents,           # list, managed manually (no chat session)
    config=types.GenerateContentConfig(tools=TOOLS)
)
```

### Detect function calls
```python
fn_calls = [p for p in response.candidates[0].content.parts
            if p.function_call and p.function_call.name]
```

### Function call fields
```python
name = part.function_call.name
args = dict(part.function_call.args)   # already a dict — no json.loads() needed
```

### Feed results back
```python
# append assistant response to history
contents.append(response.candidates[0].content)

# collect all tool results into one Content block
tool_results = []
for part in fn_calls:
    result = execute_tool(part.function_call.name, dict(part.function_call.args))
    tool_results.append(types.Part(
        function_response=types.FunctionResponse(
            name=part.function_call.name,
            response={"result": result}
        )
    ))

contents.append(types.Content(parts=tool_results, role="user"))
```

### Final text
```python
print(response.text)
```

### History management
Gemini new SDK has no chat session — you manage `contents` manually, same pattern as Anthropic/OpenAI `messages`.

### Streaming
Gemini streaming with tool calls is not straightforward — use non-streaming for tool loops, add streaming only for pure text responses.

### Current models (as of 2026-03-31)
| Model | Use case |
|---|---|
| `gemini-2.5-flash` | Best price/performance, function calling ✓ |
| `gemini-2.5-pro` | Most capable, complex reasoning |
| `gemini-2.5-flash-lite` | Fastest, most economical |

### Key gotcha — deprecated package
`google-generativeai` is fully deprecated. Use `google-genai`:
```bash
pip install google-genai
```
```python
from google import genai          # new
# NOT: import google.generativeai  # old, deprecated
```

---

## All Three LLMs — Tool Calling Comparison

| | Anthropic | OpenAI | Gemini |
|---|---|---|---|
| Tool args format | dict (`block.input`) | JSON string (`json.loads(...)`) | dict (`dict(part.function_call.args)`) |
| Tool result role | `"user"` | `"tool"` | `"user"` (as Content) |
| Stop signal | `stop_reason == "end_turn"` | `finish_reason == "stop"` | no fn_calls in parts |
| History | manual `messages` list | manual `messages` list | manual `contents` list |
| Streaming helper | `text_stream` (strings) | typed events (`event.type`) | non-trivial with tools |
| Tool schema | explicit JSON Schema | explicit JSON Schema | Python functions or explicit |

---

## Embeddings

### What an embedding is
A list of floats that represents a string's position in semantic space.
- Input: string
- Output: `list[float]` — 1536 numbers for `text-embedding-3-small`
- Vectors with similar meaning point in nearly the same direction

### OpenAI embedding API call
```python
response = client.embeddings.create(input=text, model="text-embedding-3-small")
vector = response.data[0].embedding   # list[float], length 1536
```

### Local embeddings (no API, no cost)
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")  # 384 dimensions
vector = model.encode("some text")   # runs on your machine
```
Use local when: cost matters, data is sensitive, or no internet.

### Embedding model comparison
| Model | Dims | Type | Cost |
|---|---|---|---|
| OpenAI `text-embedding-3-small` | 1536 | API | Per token |
| OpenAI `text-embedding-3-large` | 3072 | API | Per token |
| Google `text-embedding-004` | 768 | API | Per token |
| `all-MiniLM-L6-v2` | 384 | Local | Free |
| Anthropic Claude | — | N/A | **No embedding API** |

### Hard rule: never mix embedding models
You must use the same model for indexing AND querying. Different models produce vectors in incompatible spaces — mixing them makes cosine similarity scores meaningless.

```
✅  Index with text-embedding-3-small → query with text-embedding-3-small
❌  Index with text-embedding-3-small → query with all-MiniLM-L6-v2
```

### Cosine similarity
```python
def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(a[i] * b[i] for i in range(len(a)))
    mag_a = math.sqrt(sum(x**2 for x in a))
    mag_b = math.sqrt(sum(x**2 for x in b))
    return dot / (mag_a * mag_b)
```
- Measures the **angle** between two vectors, not distance
- Dividing by magnitude normalizes for document length — you measure *meaning*, not *size*
- Returns 1.0 for identical vectors (angle = 0°, cos(0°) = 1.0)
- Score guide: 1.0 = identical, 0.8+ = very similar, 0.5–0.7 = related, <0.3 = unrelated

---

## RAG (Retrieval Augmented Generation)

### What it solves
LLMs don't know your private documents and can't fit a 100-page PDF in a prompt. RAG retrieves the relevant parts first, then sends only those to the LLM.

### Two-phase pipeline
```
INDEXING (once):   document → chunk → embed each chunk → store in vector DB
QUERYING (per Q):  question → embed → find top-K similar chunks → LLM → answer
```

### Why chunks, not full documents
- Token limits on embedding APIs
- A small focused chunk scores higher similarity than a large unfocused one
- Precision: find 2–3 sentences that answer the question, not the whole document

### Chunk size tradeoff
| Smaller chunks | Larger chunks |
|---|---|
| More precise retrieval | More context per chunk |
| May lose surrounding context | May dilute the similarity score |
| More API calls to embed | Fewer chunks to manage |

Typical starting point: 2–5 sentences, or 256–512 tokens.

### Chunking strategy
Never embed full documents or individual sentences — embed *chunks* (3–10 sentences / 256–512 tokens).

| Granularity | Problem |
|---|---|
| Single sentences | Too little context — not self-contained |
| Full document | Answer gets diluted in averaged vector |
| **Chunks** | Self-contained + specific = high retrieval precision |

**Default starting point:** 256–512 tokens, 50-token overlap between chunks.

**Overlap matters:** consecutive chunks share 50 characters/tokens — so context at the end of one chunk is repeated at the start of the next. Answers that straddle a boundary aren't lost.

**Self-contained test:** read the chunk in isolation — would it make sense as a standalone answer?

**LangChain splitter:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_text(text)
```

### RAG vs fine-tuning
| | RAG | Fine-tuning |
|---|---|---|
| Updates knowledge | Add to vector DB | Retrain model |
| Cost | Embedding + retrieval | Expensive GPU training |
| Accuracy | Cites sources | Bakes in knowledge |
| Use when | Dynamic documents, Q&A | Style/behavior changes |

### LangChain + Qdrant RAG stack (used in DocTalk)

| Component | Package | Role |
|---|---|---|
| `PyPDFLoader` | `langchain-community` | Loads PDF → list of `Document` objects (one per page) |
| `RecursiveCharacterTextSplitter` | `langchain-text-splitters` | Splits pages into chunks |
| `OpenAIEmbeddings` | `langchain-openai` | Calls OpenAI API to convert text → 1536-float vector |
| `QdrantClient` | `qdrant-client` | Creates/manages in-memory vector store |
| `QdrantVectorStore` | `langchain-qdrant` | LangChain wrapper over Qdrant — add/search documents |

**LangChain's role:** orchestration + unified API. Actual vector storage and cosine math is Qdrant's job. LangChain lets you swap Qdrant for Pinecone by changing one line.

**In-memory Qdrant** (`QdrantClient(":memory:")`) — no API key, no server, runs in RAM. Only needs a key for Qdrant Cloud.

**`text-embedding-3-small`** — preferred OpenAI embedding model (better and cheaper than `ada-002`). Outputs 1536 dimensions → `VectorParams(size=1536, distance=Distance.COSINE)`.

### Full RAG pipeline with generation (doctalk.py pattern)

```python
# 1. Index
loader = PyPDFLoader("doc.pdf")
documents = loader.load()
chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(documents)
client = QdrantClient(":memory:")
client.create_collection("docs", vectors_config=VectorParams(size=1536, distance=Distance.COSINE))
embedding = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = QdrantVectorStore(client=client, collection_name="docs", embedding=embedding)
vector_store.add_documents(chunks)

# 2. Retrieve
results = vector_store.similarity_search_with_score(question, k=3)

# 3. Format context with citations
context = ""
for doc, score in results:
    context += f"[Page {doc.metadata.get('page','?')}, score: {score:.4f}]\n{doc.page_content}\n\n---\n\n"

# 4. Generate with Claude
response = anthropic.Anthropic().messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="Answer using only the context provided. Cite page numbers.",
    messages=[{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}]
)
print(response.content[0].text)
```

**Why cosine similarity is fast:** embedding is slow (neural network + API call, done once at index time). Cosine similarity is just a dot product on vectors already in RAM — milliseconds regardless of corpus size.

**Citation pattern:** page numbers come from `doc.metadata['page']` — injected into the context string so Claude can reference them in its answer.

---

## LangGraph

### What it is
A framework for building stateful multi-step agent workflows as directed graphs. Replaces LangChain's old Chains/agents API. Built on LangChain core.

### Core pattern
```
State (TypedDict) → flows through → Nodes (functions) → connected by → Edges
```

### Key concepts

| Concept | What it is |
|---|---|
| `StateGraph(Schema)` | Creates the graph. Argument is the state schema — NOT inheritance |
| `TypedDict` | Defines the shape of the shared state dict |
| Node | Plain Python function: takes full state, returns dict of changed fields only |
| Fixed edge | `add_edge("a", "b")` — always go from a to b |
| Conditional edge | `add_conditional_edges("a", router_fn)` — branch based on state |
| `set_entry_point()` | Which node runs first |
| `END` | Terminal constant — graph stops when an edge points here |
| `compile()` | Validates graph, returns a Runnable with `.invoke()` |

### State update rules
- Scalar fields (`str`, `int`) — **overwritten** when a node returns them
- List fields with `Annotated[list, operator.add]` — **appended** when a node returns them
- Fields not returned by a node — **unchanged**

```python
from typing import TypedDict, Annotated
import operator

class ResearchState(TypedDict):
    topic: str                                       # overwrite
    search_queries: Annotated[list[str], operator.add]   # append
    findings: Annotated[list[str], operator.add]         # append
    summary: str                                     # overwrite
```

### Node signature
```python
def my_node(state: ResearchState) -> dict:
    # read from state
    topic = state['topic']
    # return only what changed
    return {"search_queries": ["query1", "query2"]}
```

### State passing — immutability rule
Python passes dicts by object reference, so `state` inside a node *is* the live dict. But **never mutate it in place** — always return a delta:
```python
# CORRECT — return a delta dict
def generate_queries(state: ResearchState) -> dict:
    return {"search_queries": ["q1", "q2"]}

# WRONG — mutating in place
def generate_queries(state: ResearchState) -> dict:
    state["search_queries"] = ["q1", "q2"]  # breaks reducers, checkpointing, parallel nodes
    return {}
```
Why it breaks:
- **Reducers** (`operator.add`) never run — the merge step is bypassed
- **Checkpointing** — LangGraph saves state snapshots between nodes; in-place mutation corrupts them
- **Parallel branches** — two nodes running concurrently would race on the same dict

Mental model: treat state as **read-only inside a node**. Return only what changed. Same pattern as React's `setState`.

### Execution flow
```
invoke(initial_state)
    │
    ▼
Node 1 → reads state, returns partial update → LangGraph merges
    │
    ▼  (edge)
Node 2 → reads updated state, returns partial update → LangGraph merges
    │
    ▼  (edge)
Node 3 → reads updated state, returns partial update → LangGraph merges
    │
    ▼  (edge to END)
invoke() returns final state dict
```

### Conditional edges — routing
```python
def route_summary(state: ResearchState) -> str:
    if len(state['findings']) >= 11:
        return "detailed_summary"
    else:
        return "brief_summary"

# Without dict — router return values must match node names exactly
graph.add_conditional_edges("research", route_summary)

# With dict — translation layer (router returns readable strings, dict maps to node names)
graph.add_conditional_edges("research", route_summary, {
    "enough": "detailed_summary",
    "not_enough": "brief_summary"
})
# The dict is a lookup table — LangGraph reads it, not Python
```
- Router is pure logic — reads state, returns a string, no side effects
- Both terminal nodes need their own `add_edge(..., END)`

### Mermaid diagram
```python
print(app.get_graph().draw_mermaid())  # paste output into mermaid.live
```
- `-->` solid arrow = fixed edge
- `-.->` dashed arrow = conditional edge (decided at runtime by router)
- Shows graph shape only — condition logic inside router is NOT in the diagram
- Edge labels not auto-generated — edit raw Mermaid output by hand to add them

### LangGraph vs LangChain Chains
| | Chains | LangGraph |
|---|---|---|
| Structure | Linear only | Graph — branch + loop |
| State | Implicit | Explicit TypedDict |
| Human-in-the-loop | Awkward | Built-in |
| Checkpointing | No | Yes |

### "Runnable" — not a Python built-in
`Runnable` is a LangChain/LangGraph concept — any object with `.invoke()`. `graph.compile()` returns a Runnable. In plain Python the equivalent is any callable (object with `__call__`). LangGraph standardises on `.invoke()` as the interface.

---
---

## LangGraph — State Immutability Deep Dive

### Two valid patterns for returning state

**Pattern 1 — Immutable (create new dict):**
```python
def gather_data(state: AgentState) -> AgentState:
    price = get_price_data(state["ticker"])
    return {
        **state,              # spread all existing key-value pairs
        "price_data": price,  # override specific keys (last definition wins)
    }
```
- `**state` unpacks the dict into key=value pairs inside the new `{}`
- Creates a **brand new dict** — original state is untouched
- Safest for parallel branches sharing the same state object

**Pattern 2 — Mutable (modify in place):**
```python
def gather_data(state: AgentState) -> AgentState:
    state["price_data"] = get_price_data(state["ticker"])
    return state
```
- Modifies the **same dict** in memory (Python passes dicts by reference)
- Simpler and more readable
- Safe for linear graphs (nodes run one at a time)

**When to use which:**
| Situation | Pattern |
|-----------|---------|
| Linear graph, one node at a time | Either — use Pattern 2 for readability |
| Parallel branches sharing state | Pattern 1 (immutable) — prevents race conditions |
| Using `Annotated` reducers | Return a delta dict (not full state) |

---

## Python — `*` vs `**` Unpacking

| Operator | Used with | Meaning |
|----------|-----------|---------|
| `*`  | list / tuple | Unpack into positional arguments |
| `**` | dict | Unpack into keyword (key=value) arguments |

```python
# * unpacks a list into positional args
nums = [1, 2, 3]
print(*nums)           # same as print(1, 2, 3)

# ** unpacks a dict into keyword args
d = {"name": "Rajesh", "greeting": "Hi"}
greet(**d)             # same as greet(name="Rajesh", greeting="Hi")

# ** in a dict literal — spreads and overrides
base = {"a": 1, "b": 2, "c": 3}
merged = {**base, "b": 99}
print(merged)          # {"a": 1, "b": 99, "c": 3}  ← b is overridden
```

`**` is NOT a pointer (no relation to C/C++). It is Python-only syntax for dict spreading.

---

## Python — Pass by Reference vs Value

Python always passes objects (dicts, lists) **by reference**, not by value.

```python
def modify(state):
    state["key"] = "new_value"   # modifies the ORIGINAL dict
    return state

s = {"key": "old"}
modify(s)
print(s["key"])   # "new_value" — original was changed
```

- **By reference:** same object in memory — function modifies the caller's dict
- **By value (not Python):** would copy the dict — caller's dict unchanged
- Primitive types (`int`, `str`, `float`) behave like pass-by-value because they are immutable

---

---

## Multi-Tool Orchestration (P4 Pattern)

### Routing vs Orchestration
| | P3 Routing | P4 Orchestration |
|---|---|---|
| Tools called | One at a time, conditionally | All at once, always |
| Decision | "Should I search again?" | "Synthesize all results" |
| LLM role | Decides next step | Reasons over combined data |

### Pattern
```
User request
    → Call ALL tools (price, news, fundamentals, earnings)
    → Feed ALL results to Claude in one prompt
    → Claude returns structured recommendation
```

### Key design rule
Build domain tools first (pure Python, no LLM), wire them into the agent after. Tools do one thing well — the LLM synthesizes.

---

## Technical Indicators (Stock Analysis)

| Indicator | What it measures | Signal |
|-----------|-----------------|--------|
| RSI (14) | Momentum (0–100) | >70 overbought, <30 oversold |
| MACD | Trend direction | MACD > signal line = bullish |
| SMA50 | 50-day moving average | Support/resistance level |
| SMA200 | 200-day moving average | Long-term trend |
| Golden Cross | SMA50 > SMA200 | Bullish signal |

**Data window matters:** SMA200 needs ~200 trading days (~1 year). 3 months = ~60 days = SMA200 is null.

```python
import yfinance as yf
import pandas_ta as ta

tick = yf.Ticker("AAPL")
hist = tick.history(period="1y")   # need 1y for SMA200
rsi = hist.ta.rsi(length=14)
macd_df = hist.ta.macd()
sma_50 = hist.ta.sma(length=50)
sma_200 = hist.ta.sma(length=200)
```

---

## Sentiment Models — Domain Mismatch

**Problem:** General sentiment models trained on movie reviews score financial headlines incorrectly.

| Model | Trained on | Use for |
|-------|-----------|---------|
| `distilbert-sst-2` | Movie reviews | General text only |
| `ProsusAI/finbert` | Financial news | Stock/finance sentiment ✅ |

```python
# Production — use finbert
from transformers import pipeline
classifier = pipeline("sentiment-analysis", model="ProsusAI/finbert")
```

---

## Local Embeddings (sentence-transformers)

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")  # 384 dimensions, ~80MB, CPU-friendly
vector = model.encode("some text")   # returns numpy array of 384 floats
```

**vs OpenAI embeddings:**
| | sentence-transformers | OpenAI API |
|---|---|---|
| Cost | Free | Per token |
| Dimensions | 384 (MiniLM) | 1536 (text-embedding-3-small) |
| Offline | Yes | No |
| Quality | Good | Better |

---

## Chroma Vector Store (local)

```python
import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.Client()          # in-memory, no server needed
model = SentenceTransformer("all-MiniLM-L6-v2")

# Index
collection = client.create_collection("earnings")
embeddings = model.encode(chunks).tolist()
collection.add(documents=chunks, embeddings=embeddings, ids=["chunk_0", "chunk_1"])

# Query
query_embedding = model.encode(["What did management say about AI?"]).tolist()
results = collection.query(query_embeddings=query_embedding, n_results=3)
chunks = results["documents"][0]    # list of top-3 matching chunks
```

**Which chunks are returned:** cosine similarity between query vector and every stored chunk vector. Highest scores win. `n_results` caps the count.

---

## Structured Output with Pydantic (LLM responses)

Pattern: tell Claude to return JSON, parse + validate with Pydantic.

```python
class StockAnalysis(BaseModel):
    ticker: str
    recommendation: str    # "BUY" | "HOLD" | "SELL"
    confidence: str        # "HIGH" | "MEDIUM" | "LOW"
    reasoning: str

# Strip markdown fences Claude sometimes adds
raw = response.content[0].text.strip()
if raw.startswith("```"):
    raw = raw.split("```")[1]
    if raw.startswith("json"):
        raw = raw[4:]
    raw = raw.strip()

analysis = StockAnalysis(**json.loads(raw))   # parse + validate
```

**Gotcha:** Claude often wraps JSON in ` ```json ``` ` fences. Always strip before parsing.

---

## FastAPI — sync def vs async def

```python
# Use async def when you have real await calls
@app.post("/data")
async def get_data():
    result = await async_db_query()   # actual I/O await
    return result

# Use plain def for blocking calls — FastAPI runs in threadpool automatically
@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    result = agent.invoke(...)        # blocking call — no await
    return result
```

**Rule:** `async def` without any `await` inside is lying to FastAPI — it blocks the event loop on every request.

---

## async/await — How it works

```
Event Loop (one thread)
    ├── Coroutine A: hits await → pauses, hands control back
    ├── Coroutine B: runs now
    └── Coroutine A: response arrived → resumes
```

- `async def` — marks a coroutine (can be paused)
- `await` — pause here, let others run until this completes
- Only helps for **I/O-bound** work (network, DB, files)
- CPU-bound work (math, ML inference) — async does nothing, use threads/multiprocessing

**Global variable danger in async:**
```python
current_ticker = ""   # shared across ALL users

async def analyze(ticker: str):
    current_ticker = ticker           # User A sets "AAPL"
    result = await slow_api()         # yields here — User B sets "TSLA"
    return analyze(current_ticker)    # User A gets TSLA's data!

# Fix: always use local variables inside handlers
```

---

*Last updated: 2026-04-25 — P4 StockSage complete: multi-tool orchestration, technical indicators, sentiment, Chroma RAG, structured output, FastAPI async patterns*
