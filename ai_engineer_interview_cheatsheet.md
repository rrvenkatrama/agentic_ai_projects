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
*Last updated: 2026-03-31 — covers P1 ToolBot (Phase A, A+, B)*
