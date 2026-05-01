"""
Python Fundamentals — Section 5: with / Context Managers

Run: python 05_with_context_managers.py
"""

from contextlib import contextmanager
import asyncio


# ============================================================
# PART 1 — BUILT-IN CONTEXT MANAGER (file)
# ============================================================

def part1_builtin_file():
    print("\n--- PART 1: BUILT-IN — open() AS A CONTEXT MANAGER ---")

    # File auto-closes after the with block
    with open("/tmp/_test_section5.txt", "w") as f:
        f.write("hello from with\n")
        print(f"  inside with: file is open, f.closed={f.closed}")

    print(f"  outside with: f.closed={f.closed}")    # True — auto-closed

    # Equivalent without with:
    f = open("/tmp/_test_section5.txt", "w")
    try:
        f.write("hello manual\n")
    finally:
        f.close()
    print(f"  manual try/finally: also closed, f.closed={f.closed}")


# ============================================================
# PART 2 — CUSTOM CONTEXT MANAGER (class with __enter__/__exit__)
# ============================================================

def part2_class_based():
    print("\n--- PART 2: CLASS-BASED CONTEXT MANAGER ---")

    class Timer:
        def __enter__(self):
            print("  >>> __enter__ — starting timer")
            import time
            self.start = time.time()
            return self                       # `as t` binds to this

        def __exit__(self, exc_type, exc_val, tb):
            import time
            elapsed = time.time() - self.start
            print(f"  <<< __exit__ — elapsed: {elapsed*1000:.1f}ms")
            print(f"        exception info: type={exc_type}, val={exc_val}")
            return False                       # don't suppress exceptions

    with Timer() as t:
        sum(range(1_000_000))
        print(f"  inside with: t.start = {t.start}")


# ============================================================
# PART 3 — EXCEPTION HANDLING IN __exit__
# ============================================================

def part3_exception_handling():
    print("\n--- PART 3: HOW __exit__ SEES EXCEPTIONS ---")

    class Watcher:
        def __enter__(self):
            print("  >>> entered")
            return self
        def __exit__(self, exc_type, exc_val, tb):
            if exc_type is None:
                print("  <<< exited normally")
            else:
                print(f"  <<< exited with exception: {exc_type.__name__}: {exc_val}")
            return False                       # re-raise

    # Normal exit
    print("  Test 1 — normal exit:")
    with Watcher():
        x = 1 + 1

    # Exception exit
    print("\n  Test 2 — exception inside body:")
    try:
        with Watcher():
            raise ValueError("oops")
    except ValueError as e:
        print(f"  caught at outer level: {e}")


# ============================================================
# PART 4 — SUPPRESSING EXCEPTIONS WITH return True
# ============================================================

def part4_suppression():
    print("\n--- PART 4: SUPPRESS EXCEPTIONS (rarely a good idea) ---")

    class Swallower:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, tb):
            print(f"  __exit__ saw {exc_type}, returning True to suppress")
            return True                        # ⚠️ swallows the exception

    with Swallower():
        raise ValueError("this should be raised but won't")
    print("  reached this line — exception was silently swallowed!")


# ============================================================
# PART 5 — @contextmanager DECORATOR (the easy way)
# ============================================================

def part5_contextmanager_decorator():
    print("\n--- PART 5: @contextmanager DECORATOR ---")

    @contextmanager
    def file_logger(path):
        print(f"  opening {path}")
        f = open(path, "a")
        try:
            yield f                            # what `as x` gets
        finally:
            f.close()
            print(f"  closed {path}")

    with file_logger("/tmp/_test_section5_dec.txt") as f:
        f.write("hello from decorator\n")
        print("  inside with body")


# ============================================================
# PART 6 — MULTIPLE CONTEXT MANAGERS
# ============================================================

def part6_multiple_managers():
    print("\n--- PART 6: MULTIPLE MANAGERS IN ONE with ---")

    @contextmanager
    def named(name):
        print(f"  >>> entering {name}")
        try:
            yield name
        finally:
            print(f"  <<< exiting {name}")

    # Single with, multiple managers — comma-separated
    with named("A") as a, named("B") as b, named("C") as c:
        print(f"  body: a={a}, b={b}, c={c}")
    # Note: cleanup happens in REVERSE order (C, B, A)


# ============================================================
# PART 7 — ASYNC CONTEXT MANAGERS (__aenter__ / __aexit__)
# ============================================================

async def part7_async_context():
    print("\n--- PART 7: ASYNC CONTEXT MANAGER ---")

    class AsyncSession:
        async def __aenter__(self):
            print("  >>> async connect")
            await asyncio.sleep(0.1)           # simulate connect
            return self

        async def __aexit__(self, exc_type, exc_val, tb):
            print("  <<< async disconnect")
            await asyncio.sleep(0.1)           # simulate disconnect

        async def do_work(self):
            print("  doing work...")

    async with AsyncSession() as sess:
        await sess.do_work()


# ============================================================
# PART 8 — REAL AGENTIC PATTERN (mimicking MCP client)
# ============================================================

async def part8_mcp_pattern():
    print("\n--- PART 8: MCP-STYLE NESTED ASYNC CONTEXTS ---")

    @contextmanager
    def streams():
        print("  >>> opening streams")
        try:
            yield ("read_stream", "write_stream", "metadata")
        finally:
            print("  <<< closing streams")

    @contextmanager
    def session(read, write):
        print(f"  >>> session opened with {read}, {write}")
        try:
            yield "session_object"
        finally:
            print("  <<< session closed")

    # Same shape as: async with streamablehttp_client(...) as (r, w, _):
    #                   async with ClientSession(r, w) as session: ...
    with streams() as (read, write, _):
        with session(read, write) as sess:
            print(f"  body: using {sess}")
    # cleanup happens in reverse


if __name__ == "__main__":
    part1_builtin_file()
    part2_class_based()
    part3_exception_handling()
    part4_suppression()
    part5_contextmanager_decorator()
    part6_multiple_managers()
    asyncio.run(part7_async_context())
    asyncio.run(part8_mcp_pattern())
