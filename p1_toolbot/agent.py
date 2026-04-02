"""
P1 ToolBot — Phase A: Claude tool_use agent
Concepts: async/await, Pydantic v2 validation, tool loop, streaming
"""

import asyncio
import json
import math
from datetime import datetime
from zoneinfo import ZoneInfo

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, field_validator

load_dotenv()

# ── 1. Tool input schemas (Pydantic v2) ───────────────────────────────────────
# Pydantic validates that Claude's JSON arguments match exactly what we expect.
# If Claude hallucinates a bad argument, we catch it before it crashes.

class WeatherInput(BaseModel):
    city: str
    units: str = "celsius"

    @field_validator("units")
    @classmethod
    def check_units(cls, v: str) -> str:
        if v not in ("celsius", "fahrenheit"):
            raise ValueError("units must be 'celsius' or 'fahrenheit'")
        return v


class CalculatorInput(BaseModel):
    expression: str  # e.g. "2 ** 10", "sqrt(144)"


class TimeInput(BaseModel):
    timezone: str = "UTC"  # e.g. "America/Los_Angeles"


# ── 2. Tool implementations ───────────────────────────────────────────────────
# These are fake/stub implementations — in a real agent you'd call real APIs.

def get_weather(city: str, units: str = "celsius") -> str:
    fake_temps = {"celsius": 22, "fahrenheit": 72}
    temp = fake_temps[units]
    unit_symbol = "°C" if units == "celsius" else "°F"
    return f"Weather in {city}: Partly cloudy, {temp}{unit_symbol}, humidity 60%."


def calculator(expression: str) -> str:
    # Safe eval: only allow math operations
    allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
    allowed["__builtins__"] = {}
    try:
        result = eval(expression, allowed)  # noqa: S307
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"


def get_time(timezone: str = "UTC") -> str:
    try:
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)
        return f"Current time in {timezone}: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    except Exception:
        return f"Unknown timezone: {timezone}"


# ── 3. Tool registry ──────────────────────────────────────────────────────────
# Claude's API needs a list of tool schemas. We define them once here.
# The "input_schema" is JSON Schema — Claude uses this to know what args to pass.

TOOLS = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "units": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature units",
                },
            },
            "required": ["city"],
        },
    },
    {
        "name": "calculator",
        "description": "Evaluate a math expression. Supports standard math functions like sqrt, sin, cos, log.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression to evaluate"},
            },
            "required": ["expression"],
        },
    },
    {
        "name": "get_time",
        "description": "Get the current date and time in a given timezone.",
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "IANA timezone name, e.g. 'America/New_York'",
                },
            },
            "required": [],
        },
    },
]
SYSTEM_PROMPT = """You are ToolBot, a helpful assistant
with access to three tools:
- get_weather: get current weather for any city
- calculator: evaluate math expressions
- get_time: get current time in any timezone

Always use the appropriate tool when the user asks about
weather, math, or time.
Be concise and friendly. If a tool returns an error,
explain it clearly to the user."""

MAX_MESSAGES = 20     

# ── 4. Tool dispatcher ────────────────────────────────────────────────────────
# Maps tool name → (function, Pydantic schema class)

TOOL_MAP = {
    "get_weather": (get_weather, WeatherInput),
    "calculator": (calculator, CalculatorInput),
    "get_time": (get_time, TimeInput),
}


def execute_tool(name: str, raw_input: dict) -> str:
    """Validate args with Pydantic, then call the tool function."""
    fn, schema_cls = TOOL_MAP[name]
    try:
        validated = schema_cls(**raw_input)
    except ValidationError as e:
        return f"Invalid tool arguments: {e}"
    return fn(**validated.model_dump())


# ── 5. The agent loop ─────────────────────────────────────────────────────────
# This is the core of how tool_use works with Claude:
#
#   You → Claude (messages + tools)
#   Claude → stop_reason="tool_use" (wants to call a tool)
#   You → execute the tool, add result to messages
#   You → Claude again (now with tool result)
#   Claude → stop_reason="end_turn" (final answer)
#   ... repeat if Claude calls multiple tools

async def run_agent(user_message: str, messages: list) -> None:
    client = anthropic.Anthropic()

    # messages = [{"role": "user", "content": user_message}]

    messages.append({"role": "user", "content":user_message})
    print(f"\nYou: {user_message}")
    print("─" * 60)

    while True:
        # Call Claude (non-streaming for the tool loop; streaming in Phase A+)
        # response = client.messages.create(
        #    model="claude-opus-4-6",
        #    max_tokens=1024,
        #    tools=TOOLS,
        #    messages=messages,
        #)

        with client.messages.stream(model="claude-opus-4-6", 
            max_tokens=1024,tools=TOOLS, system=SYSTEM_PROMPT, 
            messages=messages ) as stream:
            for text in stream.text_stream:                                          
                 print(text, end="", flush=True) 
            response = stream.get_final_message()
        # Add Claude's response to message history
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Claude already printed while streaming — print the final text response
            print()
            break

        elif response.stop_reason == "tool_use":
            # Claude wants to call one or more tools
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    print(f"  [tool] {block.name}({json.dumps(block.input)})")
                    result = execute_tool(block.name, block.input)
                    print(f"  [result] {result}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            # Feed tool results back to Claude
            messages.append({"role": "user", "content": tool_results})

        else:
            print(f"Unexpected stop_reason: {response.stop_reason}")
            break


# ── 6. CLI loop ───────────────────────────────────────────────────────────────

async def main() -> None:

    messages = []    # ← lives here now, persists across turns
    print("ToolBot (Claude) — type 'quit' to exit")
    print("Tools available: weather, calculator, time\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break
                                                           

        await run_agent(user_input, messages)
        if len(messages) > MAX_MESSAGES:                         
            messages = messages[-MAX_MESSAGES:]         


if __name__ == "__main__":
    asyncio.run(main())
