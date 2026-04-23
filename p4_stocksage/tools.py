import yfinance as yf
import pandas_ta as ta
from typing import Optional
import os
from dotenv import load_dotenv
from transformers import pipeline

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# Initialize sentiment classifier once (at module load)
sentiment_classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def get_news_sentiment(ticker: str, days: int = 7) -> dict:
    """
    Fetch recent news for a ticker and analyze sentiment.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL")
        days: Look back window (default 7 days)
    
    Returns:
        Dict with sentiment scores and news headlines
    """
    try:
        from datetime import datetime, timedelta
        import requests
        
        # Calculate date range
        to_date = datetime.now().date()
        from_date = to_date - timedelta(days=days)
        
        # Fetch news from NewsAPI
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": ticker,
            "from": str(from_date),
            "to": str(to_date),
            "sortBy": "relevance",
            "language": "en",
            "apiKey": NEWSAPI_KEY,
            "pageSize": 10
        }
        
        response = requests.get(url, params=params)
        articles = response.json().get("articles", [])
        
        if not articles:
            return {
                "ticker": ticker,
                "sentiment_score": 0.0,
                "sentiment": "NEUTRAL",
                "headline_count": 0,
                "headlines": []
            }
        
        # Analyze sentiment of headlines
        sentiments = []
        headlines = []
        
        for article in articles[:10]:  # Top 10 articles
            headline = article.get("title", "")
            if headline:
                headlines.append(headline)
                # Get sentiment
                result = sentiment_classifier(headline[:512])  # Truncate to 512 tokens
                label = result[0]["label"]  # "POSITIVE" or "NEGATIVE"
                score = result[0]["score"]
                
                # Map to -1, 0, +1
                if label == "POSITIVE":
                    sentiments.append(score)
                else:  # NEGATIVE
                    sentiments.append(-score)
        
        # Calculate aggregate sentiment
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        
        # Classify overall sentiment
        if avg_sentiment > 0.1:
            sentiment_label = "POSITIVE"
        elif avg_sentiment < -0.1:
            sentiment_label = "NEGATIVE"
        else:
            sentiment_label = "NEUTRAL"
        
        return {
            "ticker": ticker,
            "sentiment_score": round(avg_sentiment, 2),
            "sentiment": sentiment_label,
            "headline_count": len(headlines),
            "headlines": headlines
        }
        
    except Exception as e:
        return {"error": str(e)}

def get_price_data(ticker: str, period: str = "3mo") -> dict:
    """
    Fetch price history and compute technical indicators.

    Args:
        ticker: Stock symbol (e.g., "AAPL")
        period: Data period (e.g., "3mo", "1y", "6mo")

    Returns:
        Dict with price, RSI, MACD, SMA50, SMA200, and analysis
    """
    try:
        tick = yf.Ticker(ticker)
        hist = tick.history(period=period)

        if hist.empty:
            return {"error": f"No data found for {ticker}"}

        # Compute indicators using pandas-ta
        rsi_series = hist.ta.rsi(length=14)
        macd_df = hist.ta.macd()  # Returns DataFrame with MACD, Signal, Histogram
        sma_50_series = hist.ta.sma(length=50)
        sma_200_series = hist.ta.sma(length=200)

        # Get latest values safely using .values (handles Series or DataFrame)
        try:
            current_price = float(hist["Close"].values[-1])
        except (ValueError, TypeError, IndexError):
            current_price = None

        try:
            rsi_val = float(rsi_series.values[-1]) if rsi_series is not None else None
        except (ValueError, TypeError, IndexError):
            rsi_val = None

        try:
            macd_val = float(macd_df.values[-1, 0]) if macd_df is not None else None
            macd_signal_val = float(macd_df.values[-1, 1]) if macd_df is not None else None
        except (ValueError, TypeError, IndexError):
            macd_val = macd_signal_val = None

        try:
            sma_50_val = float(sma_50_series.values[-1]) if sma_50_series is not None else None
        except (ValueError, TypeError, IndexError):
            sma_50_val = None

        try:
            sma_200_val = float(sma_200_series.values[-1]) if sma_200_series is not None else None
        except (ValueError, TypeError, IndexError):
            sma_200_val = None

        # Golden cross detection
        golden_cross = sma_50_val > sma_200_val if (sma_50_val is not None and sma_200_val is not None) else None
        price_vs_sma50 = ((current_price - sma_50_val) / sma_50_val * 100) if sma_50_val else None

        return {
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "rsi": round(rsi_val, 2) if rsi_val else None,
            "macd": round(macd_val, 4) if macd_val else None,
            "macd_signal": round(macd_signal_val, 4) if macd_signal_val else None,
            "sma_50": round(sma_50_val, 2) if sma_50_val else None,
            "sma_200": round(sma_200_val, 2) if sma_200_val else None,
            "golden_cross": golden_cross,
            "price_vs_sma50_pct": round(price_vs_sma50, 2) if price_vs_sma50 else None,
        }
    except Exception as e:
        return {"error": str(e)}


def get_fundamentals(ticker: str) -> dict:
    """
    Fetch fundamental metrics from Yahoo Finance.
    
    Args:
        ticker: Stock symbol
    
    Returns:
        Dict with PE ratio, market cap, sector, growth metrics
    """
    try:
        tick = yf.Ticker(ticker)
        info = tick.info
        
        return {
            "ticker": ticker,
            "pe_ratio": info.get("trailingPE", None),
            "market_cap": info.get("marketCap", None),
            "sector": info.get("sector", None),
            "revenue_growth": info.get("revenueGrowth", None),
            "profit_margin": info.get("profitMargins", None),
            "dividend_yield": info.get("dividendYield", None),
            "debt_to_equity": info.get("debtToEquity", None),
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import json
    
    print("=" * 60)
    print("PRICE DATA TEST")
    print("=" * 60)
    print(json.dumps(get_price_data("AAPL"), indent=2))
    
    print("\n" + "=" * 60)
    print("FUNDAMENTALS TEST")
    print("=" * 60)
    print(json.dumps(get_fundamentals("AAPL"), indent=2))
