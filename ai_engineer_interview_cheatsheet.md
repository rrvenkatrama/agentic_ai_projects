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
*Last updated: 2026-03-31 — covers P1 ToolBot (Phase A, A+, B, C)*
