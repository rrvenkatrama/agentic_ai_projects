
import asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

SERVER_URL = "http://localhost:8001/mcp"

async def get_price(session, ticker):
    result = await session.call_tool("get_stock_price", {"ticker": ticker})
    return result.content[0].text

async def main():
    async with streamablehttp_client(SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available tools:")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description}")

            print()
            tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
            prices = await asyncio.gather(
                *[get_price(session, t) for t in tickers]
            )
            for price in prices:
                print(price)

if __name__ == "__main__":
    asyncio.run(main())
