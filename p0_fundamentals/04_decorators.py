"""
Python Fundamentals — Section 4: Decorators

Run: python 04_decorators.py
"""

from functools import wraps, cache, lru_cache
from dataclasses import dataclass
import time


# ============================================================
# PART 1 — BASIC DECORATOR (no @wraps yet — see what breaks)
# ============================================================

def part1_basic_decorator():
    print("\n--- PART 1: BASIC DECORATOR (no @wraps) ---")

    def loud(func):
        def wrapper(*args, **kwargs):
            print(f"  >>> calling {func.__name__}")
            result = func(*args, **kwargs)
            print(f"  <<< done")
            return result
        return wrapper

    @loud
    def add(x, y):
        """Adds two numbers."""
        return x + y

    print(f"  Result: {add(2, 3)}")
    print(f"  add.__name__ = {add.__name__}")    # 'wrapper' — broken!
    print(f"  add.__doc__  = {add.__doc__}")     # None — broken!


# ============================================================
# PART 2 — DECORATOR WITH @wraps (the right way)
# ============================================================

def part2_with_wraps():
    print("\n--- PART 2: DECORATOR WITH @wraps ---")

    def loud(func):
        @wraps(func)                      # ← preserves func's name, doc, etc.
        def wrapper(*args, **kwargs):
            print(f"  >>> calling {func.__name__}")
            result = func(*args, **kwargs)
            print(f"  <<< done")
            return result
        return wrapper

    @loud
    def add(x, y):
        """Adds two numbers."""
        return x + y

    print(f"  Result: {add(2, 3)}")
    print(f"  add.__name__ = {add.__name__}")    # 'add' — preserved
    print(f"  add.__doc__  = {add.__doc__}")     # 'Adds two numbers.'


# ============================================================
# PART 3 — DECORATOR WITH ARGUMENTS (3 layers)
# ============================================================

def part3_decorator_with_args():
    print("\n--- PART 3: PARAMETERIZED DECORATOR (3 layers) ---")

    def retry(max_attempts):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        print(f"  Attempt {attempt+1} failed: {e}")
                raise RuntimeError("All attempts failed")
            return wrapper
        return decorator

    counter = {"calls": 0}

    @retry(max_attempts=3)
    def flaky_call():
        counter["calls"] += 1
        if counter["calls"] < 3:
            raise ConnectionError("network blip")
        return "success"

    print(f"  Final result: {flaky_call()}")
    print(f"  Total calls: {counter['calls']}")


# ============================================================
# PART 4 — TIMING DECORATOR (practical example)
# ============================================================

def part4_timing_decorator():
    print("\n--- PART 4: TIMING DECORATOR ---")

    def timer(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            print(f"  {func.__name__} took {elapsed*1000:.1f}ms")
            return result
        return wrapper

    @timer
    def slow_function(n):
        return sum(range(n))

    @timer
    def slower_function(n):
        return sum(i*i for i in range(n))

    slow_function(1_000_000)
    slower_function(1_000_000)


# ============================================================
# PART 5 — @property (makes a method look like an attribute)
# ============================================================

def part5_property():
    print("\n--- PART 5: @property ---")

    class Stock:
        def __init__(self, ticker, price):
            self.ticker = ticker
            self._price = price

        @property
        def price(self):
            return self._price

        @price.setter
        def price(self, value):
            if value < 0:
                raise ValueError("Price must be positive")
            self._price = value

    s = Stock("AAPL", 150)
    print(f"  s.price = {s.price}")          # called like attribute

    s.price = 200                              # uses setter
    print(f"  After s.price = 200: {s.price}")

    try:
        s.price = -10                          # validation kicks in
    except ValueError as e:
        print(f"  Setter caught: {e}")


# ============================================================
# PART 6 — @cache (memoization)
# ============================================================

def part6_cache():
    print("\n--- PART 6: @cache (MEMOIZATION) ---")

    @cache
    def fibonacci(n):
        if n < 2:
            return n
        return fibonacci(n-1) + fibonacci(n-2)

    start = time.time()
    result = fibonacci(50)
    elapsed = time.time() - start
    print(f"  fibonacci(50) = {result} in {elapsed*1000:.2f}ms")

    # Second call — cache hit
    start = time.time()
    result = fibonacci(50)
    elapsed = time.time() - start
    print(f"  Cache hit: {elapsed*1000:.4f}ms")


# ============================================================
# PART 7 — @dataclass (auto-generate __init__, __repr__, __eq__)
# ============================================================

def part7_dataclass():
    print("\n--- PART 7: @dataclass ---")

    @dataclass
    class Stock:
        ticker: str
        price: float = 0.0

    s1 = Stock(ticker="AAPL", price=150)
    s2 = Stock(ticker="AAPL", price=150)
    s3 = Stock(ticker="GOOGL", price=2800)

    print(f"  s1: {s1}")              # __repr__ auto-generated
    print(f"  s1 == s2: {s1 == s2}")  # __eq__ auto-generated → True
    print(f"  s1 == s3: {s1 == s3}")  # → False


# ============================================================
# PART 8 — DECORATOR ORDER (multiple decorators)
# ============================================================

def part8_decorator_order():
    print("\n--- PART 8: MULTIPLE DECORATORS — ORDER MATTERS ---")

    def upper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result.upper()
        return wrapper

    def exclaim(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result + "!"
        return wrapper

    @upper          # outer — runs LAST on result
    @exclaim        # inner — runs FIRST on result
    def greet(name):
        return f"hi {name}"

    print(f"  greet('rajesh') = {greet('rajesh')}")
    # Order of execution:
    # 1. greet returns "hi rajesh"
    # 2. exclaim wraps → "hi rajesh!"
    # 3. upper wraps → "HI RAJESH!"

    # Equivalent: greet = upper(exclaim(greet))


# ============================================================
# PART 9 — REAL AGENTIC PATTERN: tool registry decorator
# ============================================================

def part9_tool_registry():
    print("\n--- PART 9: REAL AGENTIC PATTERN — TOOL REGISTRY ---")

    # Simulating @mcp.tool() / @tool from CrewAI
    TOOLS = {}

    def tool(name):                          # parameterized decorator
        def decorator(func):
            TOOLS[name] = func               # register in global dict
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @tool("get_price")
    def get_stock_price(ticker):
        return f"{ticker}: $150"

    @tool("get_news")
    def get_news_sentiment(ticker):
        return f"{ticker}: positive sentiment"

    print(f"  Registered tools: {list(TOOLS.keys())}")
    print(f"  Calling tool dynamically: {TOOLS['get_price']('AAPL')}")


if __name__ == "__main__":
    part1_basic_decorator()
    part2_with_wraps()
    part3_decorator_with_args()
    part4_timing_decorator()
    part5_property()
    part6_cache()
    part7_dataclass()
    part8_decorator_order()
    part9_tool_registry()
