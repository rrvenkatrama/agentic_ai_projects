"""
Python Fundamentals — Section 2: Lambdas, map, filter, sorted with key

Run: python 02_lambdas_map_filter_sorted.py
"""


# ============================================================
# PART 1 — LAMBDAS (anonymous functions)
# ============================================================

def part1_lambda_basics():
    print("\n--- PART 1: LAMBDA BASICS ---")

    # Named function
    def square(x):
        return x * x

    # Equivalent lambda — same thing, no name
    square_lambda = lambda x: x * x

    print("Named:  square(5) =", square(5))
    print("Lambda: square_lambda(5) =", square_lambda(5))

    # Lambda with multiple args
    add = lambda a, b: a + b
    print("add(3, 4) =", add(3, 4))

    # Lambda with default args
    greet = lambda name, prefix="Hello": f"{prefix}, {name}"
    print(greet("Rajesh"))
    print(greet("Rajesh", "Hi"))

    # Lambda with conditional (ternary expression)
    abs_value = lambda x: x if x >= 0 else -x
    print("abs_value(-7) =", abs_value(-7))


def part2_lambda_limitations():
    print("\n--- PART 2: LAMBDA LIMITATIONS ---")

    # ✅ Lambdas can have only ONE expression
    valid = lambda x: x * 2

    # ❌ Cannot have statements (assignments, loops, prints, etc.)
    # invalid = lambda x: print(x); return x   # SyntaxError

    # ❌ Cannot span multiple lines easily
    # If you need any of these, use def

    # ✅ Conditional expressions DO work (they're expressions, not statements)
    classify = lambda price: "expensive" if price > 200 else "cheap"
    print("classify(150):", classify(150))
    print("classify(300):", classify(300))


# ============================================================
# PART 3 — MAP (apply function to every item)
# ============================================================

def part3_map_basics():
    print("\n--- PART 3: MAP ---")

    prices = [100, 200, 300]

    # map(func, iterable) returns an ITERATOR (not a list)
    doubled_iter = map(lambda x: x * 2, prices)
    print("Iterator object:", doubled_iter)

    # Convert to list to see contents
    doubled = list(map(lambda x: x * 2, prices))
    print("Doubled:", doubled)

    # Map with named function
    def to_thousands(x):
        return x / 1000

    thousands = list(map(to_thousands, prices))
    print("In thousands:", thousands)

    # Map over multiple iterables (function takes 2+ args)
    a = [1, 2, 3]
    b = [10, 20, 30]
    summed = list(map(lambda x, y: x + y, a, b))
    print("Element-wise sum:", summed)

    # Map vs list comprehension — comprehension is preferred
    via_map = list(map(lambda x: x * 2, prices))
    via_comp = [x * 2 for x in prices]
    print("Same result:", via_map == via_comp)


# ============================================================
# PART 4 — FILTER (keep items matching condition)
# ============================================================

def part4_filter_basics():
    print("\n--- PART 4: FILTER ---")

    prices = [100, 250, 175, 300, 50]

    # filter(func, iterable) — keeps items where func returns True
    expensive = list(filter(lambda x: x > 200, prices))
    print("Expensive (>200):", expensive)

    # filter with None — removes falsy items (0, "", None, [], {})
    mixed = [1, 0, "hello", "", None, [1], []]
    truthy = list(filter(None, mixed))
    print("Truthy items:", truthy)

    # filter vs list comprehension
    via_filter = list(filter(lambda x: x > 200, prices))
    via_comp = [x for x in prices if x > 200]
    print("Same result:", via_filter == via_comp)


# ============================================================
# PART 5 — SORTED with key
# ============================================================

def part5_sorted_basics():
    print("\n--- PART 5: SORTED WITH KEY ---")

    # Simple sort
    nums = [3, 1, 4, 1, 5, 9, 2, 6]
    print("Sorted:", sorted(nums))
    print("Reverse:", sorted(nums, reverse=True))

    # Sort strings — alphabetical by default
    tickers = ["MSFT", "AAPL", "GOOGL"]
    print("Alphabetical:", sorted(tickers))

    # Sort by LENGTH using key
    by_length = sorted(tickers, key=len)
    print("By length:", by_length)

    # Sort by custom key with lambda
    by_last_char = sorted(tickers, key=lambda t: t[-1])
    print("By last char:", by_last_char)


def part6_sorted_complex():
    print("\n--- PART 6: SORTED COMPLEX EXAMPLES ---")

    # Sort list of tuples by 2nd element
    prices = [("AAPL", 150), ("GOOGL", 2800), ("MSFT", 300)]

    by_price = sorted(prices, key=lambda x: x[1])
    print("By price:", by_price)

    # Same using operator.itemgetter (slightly faster, more idiomatic)
    from operator import itemgetter
    by_price2 = sorted(prices, key=itemgetter(1))
    print("By price (itemgetter):", by_price2)

    # Sort list of dicts
    portfolio = [
        {"ticker": "AAPL", "price": 150, "pe": 34},
        {"ticker": "GOOGL", "price": 2800, "pe": 28},
        {"ticker": "MSFT", "price": 300, "pe": 35},
    ]

    by_pe = sorted(portfolio, key=lambda x: x["pe"])
    print("\nBy PE:")
    for p in by_pe:
        print(f"  {p['ticker']}: PE={p['pe']}")

    # Sort by MULTIPLE keys — return a tuple from the key function
    # Python sorts tuples lexicographically: first element, then second, etc.
    multi = sorted(portfolio, key=lambda x: (x["pe"], x["price"]))
    print("\nBy PE then price:")
    for p in multi:
        print(f"  {p['ticker']}: PE={p['pe']}, ${p['price']}")

    # Reverse sort
    by_price_desc = sorted(portfolio, key=lambda x: x["price"], reverse=True)
    print("\nBy price descending:")
    for p in by_price_desc:
        print(f"  {p['ticker']}: ${p['price']}")


def part7_sorted_attrgetter():
    print("\n--- PART 7: SORTED WITH OBJECTS (attrgetter) ---")

    from operator import attrgetter

    class Stock:
        def __init__(self, ticker, price, pe):
            self.ticker = ticker
            self.price = price
            self.pe = pe

        def __repr__(self):
            return f"Stock({self.ticker}, ${self.price}, PE={self.pe})"

    stocks = [
        Stock("AAPL", 150, 34),
        Stock("GOOGL", 2800, 28),
        Stock("MSFT", 300, 35),
    ]

    # Sort by attribute via lambda
    by_pe = sorted(stocks, key=lambda s: s.pe)
    print("By PE (lambda):", by_pe)

    # Same using attrgetter — cleaner for object attributes
    by_pe2 = sorted(stocks, key=attrgetter("pe"))
    print("By PE (attrgetter):", by_pe2)


# ============================================================
# PART 8 — REDUCE (less common, but worth knowing)
# ============================================================

def part8_reduce():
    print("\n--- PART 8: REDUCE (functools) ---")

    from functools import reduce

    # reduce(func, iterable, initial) — folds list into single value
    nums = [1, 2, 3, 4, 5]

    # Sum all
    total = reduce(lambda acc, x: acc + x, nums)
    print("Sum:", total)

    # Multiply all
    product = reduce(lambda acc, x: acc * x, nums)
    print("Product:", product)

    # With initial value
    total_plus_100 = reduce(lambda acc, x: acc + x, nums, 100)
    print("Sum + 100:", total_plus_100)

    # In practice — use sum(), max(), min() instead of reduce when possible
    print("Use sum() instead:", sum(nums))


# ============================================================
# PART 9 — REAL AGENTIC CODE PATTERNS
# ============================================================

def part9_real_agentic_patterns():
    print("\n--- PART 9: REAL AGENTIC PATTERNS ---")

    # Pattern 1 — extract tool_use blocks from LLM response
    response_blocks = [
        {"type": "text", "text": "Let me check the price."},
        {"type": "tool_use", "name": "get_stock_price", "input": {"ticker": "AAPL"}},
        {"type": "text", "text": "And the news."},
        {"type": "tool_use", "name": "get_news_sentiment", "input": {"ticker": "AAPL"}},
    ]

    tool_calls = [b for b in response_blocks if b["type"] == "tool_use"]
    print(f"Tool calls extracted: {len(tool_calls)}")
    for tc in tool_calls:
        print(f"  {tc['name']}({tc['input']})")

    # Pattern 2 — sort search results by score
    search_results = [
        {"doc": "doc_a", "score": 0.72},
        {"doc": "doc_b", "score": 0.91},
        {"doc": "doc_c", "score": 0.85},
    ]
    top = sorted(search_results, key=lambda x: x["score"], reverse=True)
    print("\nTop results:")
    for r in top:
        print(f"  {r['doc']}: {r['score']}")

    # Pattern 3 — convert MCP tool list to Claude format using map (or comprehension)
    mcp_tools = [
        {"name": "tool_a", "description": "does A", "inputSchema": {}},
        {"name": "tool_b", "description": "does B", "inputSchema": {}},
    ]

    claude_format = list(map(
        lambda t: {"name": t["name"], "description": t["description"], "input_schema": t["inputSchema"]},
        mcp_tools
    ))
    # More idiomatic — comprehension
    claude_format_v2 = [
        {"name": t["name"], "description": t["description"], "input_schema": t["inputSchema"]}
        for t in mcp_tools
    ]
    print("\nClaude format (map vs comprehension):")
    print("  Same?", claude_format == claude_format_v2)


if __name__ == "__main__":
    part1_lambda_basics()
    part2_lambda_limitations()
    part3_map_basics()
    part4_filter_basics()
    part5_sorted_basics()
    part6_sorted_complex()
    part7_sorted_attrgetter()
    part8_reduce()
    part9_real_agentic_patterns()
