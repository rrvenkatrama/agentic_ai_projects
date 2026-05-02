"""
Python Fundamentals — Section 7: Pydantic Essentials

Run: python 07_pydantic.py

Requires: pip install pydantic   (already installed in our .venv)
"""

from pydantic import BaseModel, Field, field_validator, ValidationError, ConfigDict
from typing import Optional


# ============================================================
# PART 1 — BASIC MODEL
# ============================================================

def part1_basic():
    print("\n--- PART 1: BASIC MODEL ---")

    class Stock(BaseModel):
        ticker: str
        price: float
        period: str = "3mo"            # default

    s = Stock(ticker="AAPL", price=150.0)
    print(f"  s = {s}")
    print(f"  type(s.price) = {type(s.price).__name__}")

    # Type coercion — string "150.50" auto-converted to float
    s2 = Stock(ticker="GOOGL", price="2800.50")
    print(f"  s2 = {s2}")
    print(f"  s2.price is now a {type(s2.price).__name__}")


# ============================================================
# PART 2 — VALIDATION ERRORS
# ============================================================

def part2_validation_errors():
    print("\n--- PART 2: VALIDATION ERRORS ---")

    class Stock(BaseModel):
        ticker: str
        price: float

    try:
        Stock(ticker="AAPL", price="not a number")
    except ValidationError as e:
        print("  Caught ValidationError:")
        print(f"  {e}")


# ============================================================
# PART 3 — VALIDATE FROM DICT / JSON
# ============================================================

def part3_validate_from_dict():
    print("\n--- PART 3: VALIDATE FROM DICT / JSON ---")

    class Stock(BaseModel):
        ticker: str
        price: float

    # Validate from dict (most common in agent code)
    data = {"ticker": "AAPL", "price": 150.0}
    s1 = Stock.model_validate(data)
    print(f"  from dict: {s1}")

    # Or just spread (equivalent)
    s2 = Stock(**data)
    print(f"  from spread: {s2}")

    # Validate from JSON string
    json_str = '{"ticker": "GOOGL", "price": 2800}'
    s3 = Stock.model_validate_json(json_str)
    print(f"  from JSON: {s3}")


# ============================================================
# PART 4 — SERIALIZE TO DICT / JSON
# ============================================================

def part4_serialize():
    print("\n--- PART 4: SERIALIZE TO DICT / JSON ---")

    class Stock(BaseModel):
        ticker: str
        price: float

    s = Stock(ticker="AAPL", price=150)
    print(f"  model_dump() → {s.model_dump()}")
    print(f"  model_dump_json() → {s.model_dump_json()}")


# ============================================================
# PART 5 — OPTIONAL / DEFAULT FIELDS
# ============================================================

def part5_optional():
    print("\n--- PART 5: OPTIONAL FIELDS ---")

    class Stock(BaseModel):
        ticker: str
        price: Optional[float] = None
        signal: str = "HOLD"

    s1 = Stock(ticker="AAPL")
    print(f"  with defaults: {s1}")

    s2 = Stock(ticker="AAPL", price=150, signal="BUY")
    print(f"  fully specified: {s2}")


# ============================================================
# PART 6 — NESTED MODELS
# ============================================================

def part6_nested():
    print("\n--- PART 6: NESTED MODELS ---")

    class Tool(BaseModel):
        name: str
        description: str

    class AgentConfig(BaseModel):
        model: str = "claude-opus-4-7"
        tools: list[Tool] = []

    # Nested dicts auto-validated to Tool instances
    config = AgentConfig(
        model="claude-sonnet-4-6",
        tools=[
            {"name": "get_price", "description": "Get stock price"},
            {"name": "get_news", "description": "Get news sentiment"},
        ],
    )
    print(f"  model: {config.model}")
    for t in config.tools:
        print(f"  tool: {t.name} — {t.description}")
        print(f"    type: {type(t).__name__}")


# ============================================================
# PART 7 — FIELD CONSTRAINTS
# ============================================================

def part7_constraints():
    print("\n--- PART 7: FIELD CONSTRAINTS ---")

    class Stock(BaseModel):
        ticker: str = Field(min_length=1, max_length=5,
                            description="Stock ticker symbol")
        price: float = Field(gt=0, description="Current price in USD")
        quantity: int = Field(ge=0, default=0)

    s = Stock(ticker="AAPL", price=150)
    print(f"  valid: {s}")

    # Try violations
    for bad_args in [
        {"ticker": "", "price": 150},                  # min_length=1
        {"ticker": "TOOLONGTICKER", "price": 150},     # max_length=5
        {"ticker": "AAPL", "price": -5},               # gt=0
    ]:
        try:
            Stock(**bad_args)
        except ValidationError as e:
            print(f"  {bad_args} → caught: {e.errors()[0]['msg']}")


# ============================================================
# PART 8 — CUSTOM VALIDATOR
# ============================================================

def part8_custom_validator():
    print("\n--- PART 8: CUSTOM VALIDATOR ---")

    class Stock(BaseModel):
        ticker: str
        price: float

        @field_validator("ticker")
        @classmethod
        def ticker_uppercase(cls, v: str) -> str:
            if not v.isupper():
                raise ValueError("Ticker must be UPPERCASE")
            return v

    s = Stock(ticker="AAPL", price=150)
    print(f"  valid: {s}")

    try:
        Stock(ticker="aapl", price=150)
    except ValidationError as e:
        print(f"  'aapl' → caught: {e.errors()[0]['msg']}")


# ============================================================
# PART 9 — REAL AGENTIC PATTERN: Tool input schema
# ============================================================

def part9_tool_input_schema():
    print("\n--- PART 9: TOOL INPUT SCHEMA (real agentic pattern) ---")

    class GetPriceInput(BaseModel):
        ticker: str = Field(description="Stock ticker symbol like AAPL")
        period: str = Field(default="3mo",
                            description="Time period: 1d, 1mo, 3mo, 1y")

    # Generate JSON schema (this is what gets sent to Claude as input_schema)
    schema = GetPriceInput.model_json_schema()
    print("  Generated JSON schema:")
    import json
    print(json.dumps(schema, indent=2))


# ============================================================
# PART 10 — STRICT MODE (no coercion)
# ============================================================

def part10_strict_mode():
    print("\n--- PART 10: STRICT MODE ---")

    class StrictStock(BaseModel):
        model_config = ConfigDict(strict=True)
        price: float

    # In strict mode, "150" string is NOT coerced to float
    try:
        StrictStock(price="150")
    except ValidationError as e:
        print(f"  '150' string in strict mode → caught: {e.errors()[0]['msg']}")

    # Real float works
    s = StrictStock(price=150.0)
    print(f"  valid: {s}")


# ============================================================
# Run all parts
# ============================================================

if __name__ == "__main__":
    part1_basic()
    part2_validation_errors()
    part3_validate_from_dict()
    part4_serialize()
    part5_optional()
    part6_nested()
    part7_constraints()
    part8_custom_validator()
    part9_tool_input_schema()
    part10_strict_mode()
