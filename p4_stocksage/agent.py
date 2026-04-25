
import json
import anthropic
from typing import TypedDict
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from dotenv import load_dotenv
from tools import get_price_data, get_fundamentals, get_news_sentiment, get_earnings_context


load_dotenv()

class StockAnalysis(BaseModel):
    ticker: str
    recommendation: str          # "BUY" | "HOLD" | "SELL"
    confidence: str              # "HIGH" | "MEDIUM" | "LOW"
    price_signal: str            # "BULLISH" | "BEARISH" | "NEUTRAL"
    sentiment_signal: str        # "POSITIVE" | "NEGATIVE" | "NEUTRAL"
    key_risks: list[str]
    key_catalysts: list[str]
    reasoning: str


class AgentState(TypedDict):
    ticker: str
    price_data: dict
    fundamentals: dict
    news_sentiment: dict
    earnings_context: dict
    recommendation: dict

def gather_data(state: AgentState) -> AgentState:
    ticker = state["ticker"]
    print(f"\n[gather_data] Fetching data for {ticker}...")

    price_data = get_price_data(ticker, period="1y")      # 1y for SMA200
    fundamentals = get_fundamentals(ticker)
    news_sentiment = get_news_sentiment(ticker)
    earnings_context = get_earnings_context(
        ticker,
        query="What did management say about growth, AI, and risks?"
    )

    print(f"  Price: ${price_data.get('current_price')} | RSI: {price_data.get('rsi')}")
    print(f"  Sentiment: {news_sentiment.get('sentiment')} ({news_sentiment.get('sentiment_score')})")
    print(f"  Earnings chunks: {earnings_context.get('chunk_count', 0)}")

    return {
        **state,
        "price_data": price_data,
        "fundamentals": fundamentals,
        "news_sentiment": news_sentiment,
        "earnings_context": earnings_context,
    }

def synthesize(state: AgentState) -> AgentState:
    print("\n[synthesize] Sending data to Claude for recommendation...")

    client = anthropic.Anthropic()

    prompt = f"""You are a professional stock analyst. Analyze the following data for {state['ticker']} and provide a structured investment recommendation.

## Technical Signals
{json.dumps(state['price_data'], indent=2)}

## Fundamentals
{json.dumps(state['fundamentals'], indent=2)}

## News Sentiment
Sentiment: {state['news_sentiment'].get('sentiment')} (score: {state['news_sentiment'].get('sentiment_score')})
Headlines: {json.dumps(state['news_sentiment'].get('headlines', []), indent=2)}

## Earnings Call Context
{chr(10).join(state['earnings_context'].get('context', ['No earnings data available']))}

Based on ALL of the above, respond with ONLY valid JSON matching this exact schema:
{{
  "ticker": "{state['ticker']}",
  "recommendation": "BUY" | "HOLD" | "SELL",
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "price_signal": "BULLISH" | "BEARISH" | "NEUTRAL",
  "sentiment_signal": "POSITIVE" | "NEGATIVE" | "NEUTRAL",
  "key_risks": ["risk1", "risk2"],
  "key_catalysts": ["catalyst1", "catalyst2"],
  "reasoning": "2-3 sentence explanation"
}}"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if Claude wrapped the JSON
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    # Parse and validate with Pydantic
    analysis = StockAnalysis(**json.loads(raw))

    print(f"\n[synthesize] Recommendation: {analysis.recommendation} ({analysis.confidence} confidence)")
    print(f"  Reasoning: {analysis.reasoning}")

    return {**state, "recommendation": analysis.model_dump()}

def build_agent() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("gather_data", gather_data)
    graph.add_node("synthesize", synthesize)

    graph.set_entry_point("gather_data")
    graph.add_edge("gather_data", "synthesize")
    graph.add_edge("synthesize", END)

    return graph.compile()


if __name__ == "__main__":
    agent = build_agent()

    initial_state = {
        "ticker": "AAPL",
        "price_data": {},
        "fundamentals": {},
        "news_sentiment": {},
        "earnings_context": {},
        "recommendation": {},
    }

    result = agent.invoke(initial_state)

    print("\n" + "=" * 60)
    print("FINAL RECOMMENDATION")
    print("=" * 60)
    print(json.dumps(result["recommendation"], indent=2))
