
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'p4_stocksage'))

from mcp.server.fastmcp import FastMCP
from tools import get_news_sentiment, get_price_data, get_fundamentals, get_earnings_context

mcp = FastMCP("StockSage Analysis Server", host="0.0.0.0", port=8002)

@mcp.tool()
def stock_price_data(ticker: str, period: str = "3mo") -> str:
    """Get historical price data and technical indicators (RSI, MACD, moving averages) for a stock ticker."""
    result = get_price_data(ticker, period)
    return str(result)

@mcp.tool()
def stock_sentiment(ticker: str) -> str:
    """Get recent news sentiment score and headlines for a stock ticker."""
    result = get_news_sentiment(ticker)
    return str(result)

@mcp.tool()
def stock_fundamentals(ticker: str) -> str:
    """Get fundamental data (P/E ratio, market cap, revenue, earnings) for a stock ticker."""
    result = get_fundamentals(ticker)
    return str(result)

@mcp.tool()
def stock_earnings_context(ticker: str, query: str) -> str:
    """Search earnings call transcripts for a stock ticker given a specific query."""
    result = get_earnings_context(ticker, query)
    return str(result)

@mcp.resource("stocks://transcripts/AAPL")
def get_aapl_transcript() -> str:
    """AAPL Q1 2025 earnings call transcript."""
    path = os.path.join(os.path.dirname(__file__), '..', 'p4_stocksage', 'data', 'AAPL_earnings_Q1_2025.txt')
    with open(path) as f:
        return f.read()

@mcp.prompt()
def full_stock_analysis(ticker: str) -> str:
    """Full stock analysis prompt — guides LLM to use all available tools in sequence."""
    return (
        f"You are a senior financial analyst. Perform a complete analysis of {ticker} "
        f"using all available tools in this order: "
        f"1) stock_price_data — get technical indicators, "
        f"2) stock_sentiment — get news sentiment, "
        f"3) stock_fundamentals — get valuation metrics, "
        f"4) stock_earnings_context — search earnings transcripts for recent guidance. "
        f"Synthesize all findings into a BUY / HOLD / SELL recommendation with confidence level."
    )

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
