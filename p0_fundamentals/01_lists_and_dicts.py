"""
Python Fundamentals — Section 1: Lists and Dicts

Run: python 01_lists_and_dicts.py

This file demonstrates:
1. List basics, indexing, slicing
2. List operations (add, remove, search, sort)
3. List comprehensions
4. Nested lists (list of lists)
5. Dict basics, lookup, iteration
6. Dict operations (add, remove, merge)
7. Dict comprehensions
8. Nested dicts
9. Common gotchas
"""


# ============================================================
# PART 1 — LISTS
# ============================================================

def part1_list_basics():
    print("\n--- PART 1: LIST BASICS ---")

    # Create
    tickers = ["AAPL", "GOOGL", "MSFT", "AMD", "TSLA"]
    print("List:", tickers)
    print("Length:", len(tickers))

    # Index — by position
    print("First (index 0):", tickers[0])
    print("Last (index -1):", tickers[-1])
    print("Second to last (-2):", tickers[-2])

    # Slice — [start:stop:step], stop is exclusive
    print("First 2 [0:2]:", tickers[0:2])
    print("From index 2 [2:]:", tickers[2:])
    print("Every other [::2]:", tickers[::2])
    print("Reversed [::-1]:", tickers[::-1])


def part2_list_operations():
    print("\n--- PART 2: LIST OPERATIONS ---")

    tickers = ["AAPL", "GOOGL", "MSFT"]

    # Add
    tickers.append("AMD")          # adds at end
    tickers.insert(0, "TSLA")      # adds at index 0
    tickers.extend(["NVDA", "META"])  # adds multiple
    print("After adds:", tickers)

    # Search
    print("AAPL in list?", "AAPL" in tickers)
    print("Index of MSFT:", tickers.index("MSFT"))

    # Remove
    tickers.remove("AAPL")         # by value (first occurrence)
    popped = tickers.pop()         # removes & returns last
    print("After remove/pop, removed value:", popped)
    print("List now:", tickers)

    # Sort
    sorted_copy = sorted(tickers)  # returns new list
    tickers.sort()                 # mutates in place
    print("Sorted:", tickers)
    print("Reverse sorted:", sorted(tickers, reverse=True))

    # Aggregation
    nums = [10, 20, 30, 40]
    print("Sum:", sum(nums))
    print("Min/Max:", min(nums), max(nums))


def part3_list_comprehensions():
    print("\n--- PART 3: LIST COMPREHENSIONS ---")

    tickers = ["AAPL", "GOOGL", "MSFT", "AMD", "TSLA"]

    # Pattern: [expr for item in iterable if condition]

    # Filter
    a_only = [t for t in tickers if t.startswith("A")]
    print("Starting with A:", a_only)

    # Transform
    lower = [t.lower() for t in tickers]
    print("Lowercased:", lower)

    # Filter + transform
    short_lower = [t.lower() for t in tickers if len(t) <= 4]
    print("Short tickers, lowercased:", short_lower)

    # Equivalent loop (for understanding)
    result = []
    for t in tickers:
        if t.startswith("A"):
            result.append(t)
    print("Same result via loop:", result)


def part4_nested_lists():
    print("\n--- PART 4: NESTED LISTS ---")

    matrix = [
        ["AAPL", 150.0, "BUY"],
        ["GOOGL", 2800.0, "HOLD"],
        ["MSFT", 300.0, "BUY"],
    ]

    print("First row:", matrix[0])
    print("Row 0, column 1:", matrix[0][1])
    print("Last row, last col:", matrix[-1][-1])

    # Iterate with unpacking
    for ticker, price, signal in matrix:
        print(f"  {ticker}: ${price} → {signal}")

    # Gotcha: don't do [[0]*3]*3
    bad_grid = [[0] * 3] * 3       # all rows share the same inner list
    bad_grid[0][0] = 9
    print("Bad grid (mutation propagates):", bad_grid)

    good_grid = [[0] * 3 for _ in range(3)]   # fresh inner list each time
    good_grid[0][0] = 9
    print("Good grid:", good_grid)


# ============================================================
# PART 2 — DICTS
# ============================================================

def part5_dict_basics():
    print("\n--- PART 5: DICT BASICS ---")

    prices = {"AAPL": 150.0, "GOOGL": 2800.0, "MSFT": 300.0}
    print("Dict:", prices)
    print("Length:", len(prices))

    # Lookup by key (O(1) — uses hash table)
    print("AAPL price:", prices["AAPL"])

    # Safe lookup with default — won't raise KeyError
    print("Unknown ticker .get():", prices.get("UNKNOWN", "N/A"))

    # Membership check
    print("AAPL in prices?", "AAPL" in prices)

    # Iterate
    print("Keys:", list(prices.keys()))
    print("Values:", list(prices.values()))
    print("Items (key, value pairs):", list(prices.items()))

    for ticker, price in prices.items():
        print(f"  {ticker}: ${price}")


def part6_dict_operations():
    print("\n--- PART 6: DICT OPERATIONS ---")

    prices = {"AAPL": 150.0, "GOOGL": 2800.0}

    # Add or update (same syntax)
    prices["MSFT"] = 300.0          # add new key
    prices["AAPL"] = 175.0          # overwrite existing
    print("After adds/updates:", prices)

    # Remove
    del prices["GOOGL"]
    popped = prices.pop("MSFT", None)   # returns value or None default
    print("Popped MSFT:", popped)
    print("Now:", prices)

    # Merge — Python 3.9+ uses | operator (overrides win)
    defaults = {"period": "3mo", "currency": "USD", "lang": "en"}
    overrides = {"period": "1y", "lang": "fr"}

    merged = defaults | overrides
    print("Merged (| operator):", merged)

    # In-place merge
    config = defaults.copy()
    config |= overrides
    print("Merged (|= in-place):", config)

    # Pre-3.9 way (still works, more explicit)
    merged_v2 = {**defaults, **overrides}
    print("Merged (** unpacking):", merged_v2)


def part7_dict_comprehensions():
    print("\n--- PART 7: DICT COMPREHENSIONS ---")

    prices = {"AAPL": 150.0, "GOOGL": 2800.0, "MSFT": 300.0, "AMD": 100.0}

    # Pattern: {key_expr: value_expr for k, v in old_dict.items() if cond}

    # Filter — keep only expensive
    expensive = {t: p for t, p in prices.items() if p > 200}
    print("Price > 200:", expensive)

    # Transform values
    in_thousands = {t: p / 1000 for t, p in prices.items()}
    print("In thousands:", in_thousands)

    # Build dict from a list
    tickers = ["AAPL", "GOOGL", "MSFT"]
    placeholder_dict = {t: 0.0 for t in tickers}
    print("Initialized to 0:", placeholder_dict)

    # Invert a dict (swap keys and values)
    inverted = {v: k for k, v in prices.items()}
    print("Inverted:", inverted)


def part8_nested_dicts():
    print("\n--- PART 8: NESTED DICTS ---")

    portfolio = {
        "AAPL": {"price": 270.0, "pe": 34.3, "signal": "BUY"},
        "GOOGL": {"price": 2800.0, "pe": 28.5, "signal": "HOLD"},
    }

    # Direct access
    print("AAPL price:", portfolio["AAPL"]["price"])

    # Safe access — chain .get() so missing keys don't crash
    print("AMD signal (safe):", portfolio.get("AMD", {}).get("signal", "N/A"))

    # Iterate
    for ticker, details in portfolio.items():
        print(f"  {ticker}: ${details['price']} (PE={details['pe']}) → {details['signal']}")


def part9_gotchas():
    print("\n--- PART 9: COMMON GOTCHAS ---")

    # 1. Assignment is NOT a copy
    a = [1, 2, 3]
    b = a               # b and a point to the SAME list
    b.append(4)
    print("a after b.append:", a)   # [1, 2, 3, 4]  — surprised?

    # Fix: explicit copy
    a = [1, 2, 3]
    b = a.copy()        # or a[:] or list(a)
    b.append(4)
    print("With .copy(), a stays:", a)

    # 2. Dict keys must be hashable
    valid = {("AAPL", "Q1"): 150.0}    # tuple is hashable
    print("Tuple as key works:", valid)

    try:
        invalid = {["AAPL"]: 150.0}    # list is mutable → not hashable
    except TypeError as e:
        print("List as key fails:", e)

    # 3. Modifying a dict during iteration → RuntimeError
    prices = {"AAPL": 150.0, "GOOGL": 2800.0, "MSFT": 300.0}
    try:
        for k in prices:
            if prices[k] < 200:
                del prices[k]          # bad
    except RuntimeError as e:
        print("Modify during iter fails:", e)

    # Fix: iterate over a copy of keys
    prices = {"AAPL": 150.0, "GOOGL": 2800.0, "MSFT": 300.0}
    for k in list(prices.keys()):
        if prices[k] < 200:
            del prices[k]
    print("After safe deletion:", prices)


if __name__ == "__main__":
    part1_list_basics()
    part2_list_operations()
    part3_list_comprehensions()
    part4_nested_lists()
    part5_dict_basics()
    part6_dict_operations()
    part7_dict_comprehensions()
    part8_nested_dicts()
    part9_gotchas()
