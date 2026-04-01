"""
P1 ToolBot — Phase A: Openai tool_use agent
Concepts: async/await, Pydantic v2 validation, tool loop, streaming
"""

import asyncio
import os
import json
import math
from datetime import datetime
from zoneinfo import ZoneInfo

from google import genai
from google.genai import types
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

# TOOLS = [
#     {
#         "type":"function", 
#         "function": {
#             "name": "get_weather",
#             "description": "Get current weather for a city.",
#             "parameters": {
#                "type": "object", 
#                "properties": {
#                    "city": {"type": "string", "description": "City name"},
#                    "units": {
#                        "type": "string",
#                        "enum": ["celsius", "fahrenheit"],
#                       "description": "Temperature units",
#                      },
#                 },
#                 "required": ["city"],
#             }
#          }
#         ,
#     },
#     {
#         "type":"function", 
#         "function": {
#              "name": "calculator",
#              "description": "Evaluate a math expression. Supports standard math functions like sqrt, sin, cos, log.",
#              "parameters": {
#                 "type": "object",  
#                 "properties": {
#                 "expression": {"type": "string", "description": "Math expression to evaluate"},
#                 },
#                 "required": ["expression"],
#         }
#         },
#     },
#     {
#         "type":"function", 
#         "function": {
#                 "name": "get_time",
#                 "description": "Get the current date and time in a given timezone.",
#                 "parameters": {
#                     "type": "object", 
#                     "properties": {
#                     "timezone": {
#                     "type": "string",
#                     "description": "IANA timezone name, e.g. 'America/New_York'",
#                      },
#                 },
#                 "required": [],
#                  }
#         },
#     },
# ]

# TOOLS = genai.protos.Tool(
#     function_declarations=[
#         genai.protos.FunctionDeclaration(
#             name="get_weather",
#             description="Get current weather for a city.",
#             parameters=genai.protos.Schema(
#                 type=genai.protos.Type.OBJECT,
#                 properties={
#                     "city":  genai.protos.Schema(
#                         type=genai.protos.Type.STRING
#                     ),
#                     "units": genai.protos.Schema(
#                         type=genai.protos.Type.STRING,
#                         enum=["celsius", "fahrenheit"]
#                     ),
#                 },
#                 required=["city"]
#             )
#         ),
#         genai.protos.FunctionDeclaration(
#             name="calculator",
#             description="Evaluate a math expression. Supports standard math functions like sqrt, sin, cos, log.",
#             parameters=genai.protos.Schema(
#                 type=genai.protos.Type.OBJECT,
#                 properties={
#                     "expression": genai.protos.Schema(
#                         type=genai.protos.Type.STRING,
#                         description="IANA timezone name, e.g. 'America/New_York'"
#                     ),
#                 },
#                 required=["expression"]
#             )
#         ),
#         genai.protos.FunctionDeclaration(
#             name="get_time",
#             description= "Get the current date and time in a given timezone.",
#             parameters=genai.protos.Schema(
#                 type=genai.protos.Type.OBJECT,
#                 properties={
#                     "timezone": genai.protos.Schema(
#                         type=genai.protos.Type.STRING,
#                         description="Timezone of the place"
#                     ),
#                 },
#                 required=[]
#             )
#         )
#         # ... calculator, get_time
#     ]
# )


TOOLS = [get_weather, calculator, get_time]


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
    #client = OpenAI()

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    contents = [{"role": "user", "parts": [{"text": user_message}]}]

    print(f"\nYou: {user_message}")
    print("─" * 60)

    while True:
        # API call
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
            config=types.GenerateContentConfig(tools=TOOLS))
        # check if any part is a function call
        fn_calls = [p for p in response.candidates[0].content.parts 
                    if p.function_call and p.function_call.name]
        if not fn_calls:
            # no tools — done
            print(response.text)
            break
        else: 
            # append assistant's response to history
            contents.append(response.candidates[0].content)

            # execute each tool and collect results
            tool_results = []
            for part in fn_calls:
                name = part.function_call.name
                args = dict(part.function_call.args)
                print(f"  [tool] {name}({args})")
                result = execute_tool(name, args)
                print(f"  [result] {result}")
                tool_results.append(
                    types.Part(function_response=types.FunctionResponse(
                        name=name,
                        response={"result": result}
                    ))
                )

            # append all tool results as one user turn
            contents.append(types.Content(parts=tool_results, role="user"))


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
