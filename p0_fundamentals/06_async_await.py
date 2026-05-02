"""
Python Fundamentals — Section 6: async/await Patterns

Run: python 06_async_await.py
"""

import asyncio
import time


# Helper for timestamps
start_time = None
def t():
    return f"[{time.time() - start_time:5.2f}s]"


# ============================================================
# PART 1 — BASIC async def + await + asyncio.run
# ============================================================

async def part1_basic():
    print("\n--- PART 1: BASIC async def + await ---")
    print(f"{t()} part1: started")
    await asyncio.sleep(0.5)
    print(f"{t()} part1: woke up")


# ============================================================
# PART 2 — SEQUENTIAL awaits (each waits for previous)
# ============================================================

async def step(name, delay):
    print(f"{t()} step {name} start")
    await asyncio.sleep(delay)
    print(f"{t()} step {name} done")
    return f"result-{name}"


async def part2_sequential():
    print("\n--- PART 2: SEQUENTIAL awaits ---")
    a = await step("A", 0.5)
    b = await step("B", 0.5)
    c = await step("C", 0.5)
    print(f"{t()} part2: results = {[a, b, c]}")
    print(f"{t()} part2: total ~1.5s (sequential)")


# ============================================================
# PART 3 — CONCURRENT with asyncio.gather (the speed win)
# ============================================================

async def part3_gather():
    print("\n--- PART 3: CONCURRENT via asyncio.gather ---")
    results = await asyncio.gather(
        step("X", 0.5),
        step("Y", 0.5),
        step("Z", 0.5),
    )
    print(f"{t()} part3: results = {results}")
    print(f"{t()} part3: total ~0.5s (concurrent)")


# ============================================================
# PART 4 — gather with return_exceptions
# ============================================================

async def flaky(name, should_fail=False):
    await asyncio.sleep(0.2)
    if should_fail:
        raise RuntimeError(f"{name} failed!")
    return f"ok-{name}"


async def part4_gather_with_errors():
    print("\n--- PART 4: gather with return_exceptions=True ---")
    results = await asyncio.gather(
        flaky("A"),
        flaky("B", should_fail=True),
        flaky("C"),
        return_exceptions=True,
    )
    for r in results:
        if isinstance(r, Exception):
            print(f"{t()}   ⚠️ got exception: {r}")
        else:
            print(f"{t()}   ✓ got: {r}")


# ============================================================
# PART 5 — create_task (fire-and-forget background work)
# ============================================================

async def heartbeat():
    """Background task — prints periodically."""
    for i in range(4):
        await asyncio.sleep(0.3)
        print(f"{t()}   💓 heartbeat {i}")


async def part5_create_task():
    print("\n--- PART 5: create_task (background) ---")

    # Start heartbeat in background — DON'T await it
    bg = asyncio.create_task(heartbeat())

    # Main work continues immediately
    print(f"{t()} part5: main work starting")
    await asyncio.sleep(1.5)        # heartbeat ticks DURING this await
    print(f"{t()} part5: main work done")

    # Wait for background to finish
    await bg
    print(f"{t()} part5: background also done")


# ============================================================
# PART 6 — async context manager (already used in P6 MCP)
# ============================================================

class AsyncResource:
    async def __aenter__(self):
        print(f"{t()}   async __aenter__: opening resource")
        await asyncio.sleep(0.1)
        return self

    async def __aexit__(self, exc_type, exc_val, tb):
        print(f"{t()}   async __aexit__: closing resource")
        await asyncio.sleep(0.1)

    async def do_work(self):
        await asyncio.sleep(0.2)
        return "work-done"


async def part6_async_with():
    print("\n--- PART 6: async with ---")
    async with AsyncResource() as r:
        result = await r.do_work()
        print(f"{t()}   got: {result}")


# ============================================================
# PART 7 — async iterator (async for)
# ============================================================

async def event_stream():
    """Mimics streaming LLM response — yields events one at a time."""
    for i in range(4):
        await asyncio.sleep(0.2)
        yield f"chunk-{i}"


async def part7_async_for():
    print("\n--- PART 7: async for (async iterator) ---")
    async for chunk in event_stream():
        print(f"{t()}   received: {chunk}")


# ============================================================
# PART 8 — bridging sync and async (asyncio.to_thread)
# ============================================================

def cpu_blocking_function(n):
    """Simulates CPU-bound or blocking I/O work — would freeze event loop."""
    time.sleep(0.5)        # blocking
    return n * 2


async def part8_to_thread():
    print("\n--- PART 8: bridging sync code with asyncio.to_thread ---")
    # Run blocking function on a separate thread, await the result
    result = await asyncio.to_thread(cpu_blocking_function, 21)
    print(f"{t()} part8: blocking function returned {result}")


# ============================================================
# PART 9 — TIMEOUT pattern
# ============================================================

async def slow_operation():
    await asyncio.sleep(3)
    return "completed"


async def part9_timeout():
    print("\n--- PART 9: timeout pattern ---")
    try:
        async with asyncio.timeout(0.5):       # 0.5s timeout
            result = await slow_operation()
            print(f"{t()} part9: {result}")
    except asyncio.TimeoutError:
        print(f"{t()} part9: ⏱️  timed out (slow_operation needed 3s, only had 0.5s)")


# ============================================================
# Run all parts
# ============================================================

async def main():
    global start_time
    start_time = time.time()

    await part1_basic()
    await part2_sequential()
    await part3_gather()
    await part4_gather_with_errors()
    await part5_create_task()
    await part6_async_with()
    await part7_async_for()
    await part8_to_thread()
    await part9_timeout()


if __name__ == "__main__":
    asyncio.run(main())
