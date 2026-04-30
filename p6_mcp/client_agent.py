
import sys
import asyncio
import anthropic
from dotenv import load_dotenv
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

load_dotenv()

SERVER_URL = "http://localhost:8002/mcp"
MODEL = "claude-opus-4-7"

async def run_analysis(ticker: str):
    async with streamablehttp_client(SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Get prompt template from MCP server
            prompt = await session.get_prompt("full_stock_analysis", {"ticker": ticker})
            system_text = prompt.messages[0].content.text

            # Get tool schemas from MCP server, convert to Claude format
            tools_result = await session.list_tools()
            claude_tools = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.inputSchema
                }
                for t in tools_result.tools
            ]

            client = anthropic.Anthropic()
            messages = [{"role": "user", "content": system_text}]

            # Agentic loop — Claude calls tools until end_turn
            while True:
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=4096,
                    tools=claude_tools,
                    messages=messages
                )

                if response.stop_reason == "end_turn":
                    for block in response.content:
                        if hasattr(block, "text"):
                            print(block.text)
                    break

                # Process tool calls — dispatch each to MCP server
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"Calling: {block.name}({block.input})")
                        result = await session.call_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result.content[0].text
                        })
                messages.append({"role": "user", "content": tool_results})

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    print(f"\nAnalyzing {ticker} via StockSage MCP Server...\n")
    asyncio.run(run_analysis(ticker))
