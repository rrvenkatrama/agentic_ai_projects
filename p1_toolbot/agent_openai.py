"""
P1 ToolBot — Phase A: Openai tool_use agent
Concepts: async/await, Pydantic v2 validation, tool loop, streaming
"""

import asyncio
import json
import math
from datetime import datetime
from zoneinfo import ZoneInfo

from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, field_validator

load_dotenv()

# ── 1. Tool input schemas (Pydantic v2) ───────────────────────────────────────
# Pydantic validates that Openai's JSON arguments match exactly what we expect.
# If Openai hallucinates a bad argument, we catch it before it crashes.

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
# Openai's API needs a list of tool schemas. We define them once here.
# The "input_schema" is JSON Schema — Openai uses this to know what args to pass.

TOOLS = [
    {
        "type":"function", 
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city.",
            "parameters": {
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
            }
         }
        ,
    },
    {
        "type":"function", 
        "function": {
             "name": "calculator",
             "description": "Evaluate a math expression. Supports standard math functions like sqrt, sin, cos, log.",
             "parameters": {
                "type": "object",  
                "properties": {
                "expression": {"type": "string", "description": "Math expression to evaluate"},
                },
                "required": ["expression"],
        }
        },
    },
    {
        "type":"function", 
        "function": {
                "name": "get_time",
                "description": "Get the current date and time in a given timezone.",
                "parameters": {
                    "type": "object", 
                    "properties": {
                    "timezone": {
                    "type": "string",
                    "description": "IANA timezone name, e.g. 'America/New_York'",
                     },
                },
                "required": [],
                 }
        },
    },
]


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
# This is the core of how tool_use works with openai:
#
#   You → Openai (messages + tools)
#   Openai → stop_reason="tool_use" (wants to call a tool)
#   You → execute the tool, add result to messages
#   You → Openai again (now with tool result)
#   Openai → stop_reason="end_turn" (final answer)
#   ... repeat if Openai calls multiple tools

async def run_agent(user_message: str) -> None:
    client = OpenAI()

    messages = [{"role": "user", "content": user_message}]

    print(f"\nYou: {user_message}")
    print("─" * 60)

    while True:


        with client.chat.completions.stream(model="gpt-4o", 
            max_tokens=1024,tools=TOOLS,
            messages=messages ) as stream:
            for event in stream:                                        
                if event.type == "content.delta":                                        
                     print(event.delta, end="", flush=True)   
            response = stream.get_final_completion()

        if response.choices[0].finish_reason == "stop":
            # Openai already printed while streaming — print the final text response
            print()
            break

        elif response.choices[0].finish_reason == "tool_calls":
            # append assistant message WITH tool_calls (only once, here)           
            messages.append({                                                        
             "role": "assistant",
             "content": response.choices[0].message.content,                      
             "tool_calls": response.choices[0].message.tool_calls,                
            }) 

            for tool_call in response.choices[0].message.tool_calls:                 
                name = tool_call.function.name                                     
                args = json.loads(tool_call.function.arguments)                      
                print(f"  [tool] {name}({json.dumps(args)})")                        
                result = execute_tool(name, args)                                    
                print(f"  [result] {result}")                                        
                                                                               
                # each tool result is its own message with role "tool"             
                messages.append({                                                    
                "role": "tool",                               
                "tool_call_id": tool_call.id,                                    
                "content": result,                                               
                })                                                                   
                

        else:
            print(f"Unexpected finish_reason: {response.choices[0].finish_reason}")
            break


# ── 6. CLI loop ───────────────────────────────────────────────────────────────

async def main() -> None:
    print("ToolBot (Openai) — type 'quit' to exit")
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

        await run_agent(user_input)


if __name__ == "__main__":
    asyncio.run(main())
