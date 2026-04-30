"""
Python Fundamentals — Section 3: *args and **kwargs

Run: python 03_args_kwargs.py
"""


# ============================================================
# PART 1 — *args (pack extra positional args into a tuple)
# ============================================================

def part1_args_basics():
    print("\n--- PART 1: *args BASICS ---")

    def add_all(*nums):
        print(f"  Inside: nums = {nums}, type = {type(nums).__name__}")
        return sum(nums)

    print("add_all(1, 2, 3) =", add_all(1, 2, 3))
    print("add_all(1, 2, 3, 4, 5) =", add_all(1, 2, 3, 4, 5))
    print("add_all() =", add_all())


def part2_args_with_regular_params():
    print("\n--- PART 2: *args MIXED WITH REGULAR PARAMS ---")

    def greet(prefix, *names):
        for name in names:
            print(f"  {prefix}, {name}")

    greet("Hello", "Rajesh", "Anna", "Carlos")
    print()
    greet("Hi")    # *names is empty tuple


# ============================================================
# PART 3 — *list at CALL site (unpack into positional args)
# ============================================================

def part3_unpacking_call_site():
    print("\n--- PART 3: UNPACK A LIST WITH * AT CALL SITE ---")

    def divide(a, b):
        return a / b

    values = [10, 2]

    # Without *  — passes the list as a single arg → error
    try:
        divide(values)
    except TypeError as e:
        print(f"  divide(values) without *: {e}")

    # With *  — unpacks into positional args
    print(f"  divide(*values) = {divide(*values)}")    # 5.0

    # Real agentic example — asyncio.gather
    print("\n  Real example: tickers list unpacked for asyncio.gather()")
    tickers = ["AAPL", "GOOGL", "MSFT"]
    print(f"  *tickers spreads into individual args: {[t for t in tickers]}")


# ============================================================
# PART 4 — **kwargs (pack extra keyword args into a dict)
# ============================================================

def part4_kwargs_basics():
    print("\n--- PART 4: **kwargs BASICS ---")

    def make_config(**opts):
        print(f"  Inside: opts = {opts}, type = {type(opts).__name__}")
        return opts

    config = make_config(model="opus", temperature=0.7, max_tokens=1000)
    print(f"  Returned: {config}")

    empty = make_config()
    print(f"  Empty: {empty}")


def part5_kwargs_with_regular_params():
    print("\n--- PART 5: **kwargs MIXED WITH REGULAR PARAMS ---")

    def call_llm(prompt, **opts):
        print(f"  Prompt: {prompt}")
        print(f"  Options: {opts}")

    call_llm("What's AAPL?", model="claude-opus-4-7", temperature=0.7, max_tokens=1000)


# ============================================================
# PART 6 — **dict at CALL site (unpack into keyword args)
# ============================================================

def part6_unpacking_dict_at_call_site():
    print("\n--- PART 6: UNPACK A DICT WITH ** AT CALL SITE ---")

    def call_llm(prompt, model="sonnet", temperature=0.5, max_tokens=512):
        print(f"  Calling LLM: prompt={prompt!r}, model={model}, temp={temperature}, max={max_tokens}")

    config = {"model": "claude-opus-4-7", "temperature": 0.7, "max_tokens": 1000}

    # Without ** — passes the dict as a single positional arg → wrong
    try:
        call_llm("Hello", config)
    except TypeError as e:
        print(f"  Without **: {e}")

    # With ** — unpacks into keyword args
    call_llm("Hello", **config)


# ============================================================
# PART 7 — COMBINING EVERYTHING
# ============================================================

def part7_combining_all():
    print("\n--- PART 7: COMBINING POSITIONAL, *args, KEYWORD-ONLY, **kwargs ---")

    def super_func(a, b, *args, c, d=10, **kwargs):
        print(f"  a = {a}")
        print(f"  b = {b}")
        print(f"  args = {args}")    # extra positional
        print(f"  c = {c} (keyword-only)")
        print(f"  d = {d} (keyword, has default)")
        print(f"  kwargs = {kwargs}")  # extra keyword

    super_func(1, 2, 3, 4, 5, c="REQUIRED", d=99, extra1="x", extra2="y")


# ============================================================
# PART 8 — DECORATORS USING *args, **kwargs (the canonical use)
# ============================================================

def part8_decorator_pattern():
    print("\n--- PART 8: DECORATOR PATTERN USING *args/**kwargs ---")

    def loud(func):
        def wrapper(*args, **kwargs):              # accept ANY signature
            print(f"  >>> Calling {func.__name__}({args}, {kwargs})")
            result = func(*args, **kwargs)         # forward EXACTLY what we got
            print(f"  <<< {func.__name__} returned {result}")
            return result
        return wrapper

    @loud
    def add(x, y):
        return x + y

    @loud
    def greet(name, greeting="Hello"):
        return f"{greeting}, {name}"

    add(2, 3)
    greet("Rajesh")
    greet("Rajesh", greeting="Hi")


# ============================================================
# PART 9 — KEYWORD-ONLY ENFORCEMENT WITH BARE *
# ============================================================

def part9_keyword_only():
    print("\n--- PART 9: KEYWORD-ONLY PARAMS WITH BARE * ---")

    def call(prompt, *, model, temperature=0.7):
        # Anything after * MUST be passed by keyword
        print(f"  prompt={prompt!r}, model={model}, temp={temperature}")

    call("Hi", model="opus")           # ✅ keyword
    call("Hi", model="opus", temperature=0.5)

    try:
        call("Hi", "opus")             # ❌ positional not allowed for model
    except TypeError as e:
        print(f"  Error: {e}")


# ============================================================
# PART 10 — REAL AGENTIC AI PATTERN
# ============================================================

def part10_real_agentic_pattern():
    print("\n--- PART 10: REAL AGENTIC PATTERN — TOOL DISPATCH ---")

    # Simulate an MCP tool definition
    def get_stock_price(ticker, period="3mo"):
        return f"  Got price for {ticker} over {period}"

    # Simulate a tool_use block from an LLM
    tool_use_block = {
        "name": "get_stock_price",
        "input": {"ticker": "AAPL", "period": "1y"},
    }

    # Generic dispatch — works for ANY tool, ANY input
    tool_function = get_stock_price
    tool_input = tool_use_block["input"]
    result = tool_function(**tool_input)        # spread dict into named args
    print(result)

    # Same call WITHOUT spreading would be wrong:
    # tool_function(tool_input)   # would pass dict as ticker — error!


if __name__ == "__main__":
    part1_args_basics()
    part2_args_with_regular_params()
    part3_unpacking_call_site()
    part4_kwargs_basics()
    part5_kwargs_with_regular_params()
    part6_unpacking_dict_at_call_site()
    part7_combining_all()
    part8_decorator_pattern()
    part9_keyword_only()
    part10_real_agentic_pattern()
