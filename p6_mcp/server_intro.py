
import yfinance as yf
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("StockSage MCP Server", host="0.0.0.0", port=8001)

@mcp.resource("stocks://earnings/{ticker}")
def get_earnings_note(ticker: str) -> str:
    """Returns analyst earnings notes for a given ticker."""
    notes = {
        "AAPL": "Q1 2025: Revenue $124B, beat estimates by 3%. Services grew 14% YoY.",
        "GOOGL": "Q1 2025: Ad revenue $61B, cloud grew 28% YoY. Beat on EPS.",
        "MSFT": "Q1 2025: Azure grew 31% YoY. Copilot driving enterprise adoption.",
    }
    return notes.get(ticker.upper(), f"No earnings notes for {ticker.upper()}")

@mcp.prompt()
def stock_analysis_prompt(ticker: str, price: str) -> str:
    """Standard prompt for analyzing a stock given ticker and current price."""
    return (
        f"You are a financial analyst. Analyze {ticker} currently trading at {price}. "
        f"Consider: recent earnings, market trends, and risk factors. "
        f"Give a concise BUY / HOLD / SELL recommendation with 2-3 bullet point reasons."
    )


@mcp.tool()
def get_stock_price(ticker: str) -> str:
    """Get the current stock price for a given ticker symbol."""
    stock = yf.Ticker(ticker)
    info = stock.info
    price = info.get("currentPrice") or info.get("regularMarketPrice", "N/A")
    name = info.get("shortName", ticker)
    return f"{name} ({ticker.upper()}): ${price}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
