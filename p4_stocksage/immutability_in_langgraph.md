# Immutability in LangGraph — State Management Patterns

## The Core Idea

In LangGraph, each node receives the current state and must return the updated state.
There are two ways to do this: **mutate in place** or **create a new dict**.

---

## Pattern 1 — Mutate In Place (explicit, readable)

```python
def gather_data(state: AgentState) -> AgentState:
    state["price_data"] = get_price_data(state["ticker"])
    state["fundamentals"] = get_fundamentals(state["ticker"])
    return state
```

- Modifies the **same dict** that was passed in
- Python passes dicts by reference — the caller's dict is also changed
- Simple and readable
- Safe for linear graphs (one node at a time)

---

## Pattern 2 — Immutable Return (create a new dict)

```python
def gather_data(state: AgentState) -> AgentState:
    return {
        **state,                              # copy ALL existing key-value pairs
        "price_data": get_price_data(...),    # override these specific keys
        "fundamentals": get_fundamentals(...) # last definition wins
    }
```

- Creates a **brand new dict** — original state is untouched
- `**state` is Python's dict unpacking operator — spreads all key-value pairs
- When a key appears twice, the **last one wins** (the overrides win)
- Safer when nodes run in parallel and share the same state object

---

## Why Immutability Matters

```
              ┌─────────────┐
              │    State    │ ← shared object
              └──────┬──────┘
                     │
          ┌──────────┼──────────┐
          │                     │
    ┌─────▼──────┐       ┌──────▼─────┐
    │  Node A    │       │  Node B    │
    │ mutates    │       │ mutates    │
    │ state      │       │ state      │
    └────────────┘       └────────────┘
```

If Node A and Node B both mutate the **same dict** in parallel, they overwrite
each other's changes — a race condition. Immutable returns prevent this:
each node works on its own copy, LangGraph merges the results.

---

## Python Refresher — `*` vs `**`

| Operator | Used with | Meaning |
|----------|-----------|---------|
| `*`  | list / tuple | Unpack into positional arguments |
| `**` | dict | Unpack into keyword (key=value) arguments |

```python
# * example
nums = [1, 2, 3]
print(*nums)          # same as print(1, 2, 3)

# ** example
d = {"a": 1, "b": 2}
new = {**d, "b": 99}  # {"a": 1, "b": 99}  ← b is overridden
```

---

## Pass by Reference in Python

Python always passes objects (dicts, lists) **by reference** — not by value.

```python
def modify(state):
    state["key"] = "new_value"   # modifies the ORIGINAL dict
    return state

s = {"key": "old"}
modify(s)
print(s["key"])   # "new_value" — the original was changed
```

This is why Pattern 1 (mutate in place) works — you're modifying the same
object LangGraph passed in, then returning it.

---

## Which Pattern to Use?

| Situation | Pattern |
|-----------|---------|
| Linear graph (nodes run one at a time) | Either works — use Pattern 1 for readability |
| Parallel branches sharing state | Pattern 2 (immutable) — prevents race conditions |
| LangGraph with `Annotated` reducers | LangGraph handles merging — Pattern 1 is fine |
