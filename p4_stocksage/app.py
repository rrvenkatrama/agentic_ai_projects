
import json
import sys
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Add parent dir so we can import agent
sys.path.insert(0, str(Path(__file__).parent))

from agent import build_agent

app = FastAPI(title="StockSage")
agent = build_agent()

class AnalyzeRequest(BaseModel):
    ticker: str

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>StockSage</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 60px auto; padding: 0 20px; }
            input { padding: 10px; font-size: 16px; width: 200px; }
            button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
            #result { margin-top: 30px; white-space: pre-wrap; background: #f4f4f4; padding: 20px; border-radius: 8px; }
            .BUY { color: green; font-size: 24px; font-weight: bold; }
            .HOLD { color: orange; font-size: 24px; font-weight: bold; }
            .SELL { color: red; font-size: 24px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>StockSage</h1>
        <p>Enter a ticker symbol to get an AI-powered stock recommendation.</p>
        <input id="ticker" type="text" placeholder="e.g. AAPL" />
        <button onclick="analyze()">Analyze</button>
        <div id="result"></div>

        <script>
            async function analyze() {
                const ticker = document.getElementById("ticker").value.trim().toUpperCase();
                if (!ticker) return;

                const resultDiv = document.getElementById("result");
                resultDiv.innerHTML = "Analyzing " + ticker + "... (this takes ~30 seconds)";

                const response = await fetch("/analyze", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ ticker: ticker })
                });

                if (!response.ok) {
                    resultDiv.innerHTML = "Error: " + await response.text();
                    return;
                }

                const data = await response.json();
                const rec = data.recommendation;

                resultDiv.innerHTML = `
<span class="${rec}">${rec}</span> — ${data.confidence} confidence

Ticker: ${data.ticker}
Price Signal: ${data.price_signal}
Sentiment Signal: ${data.sentiment_signal}

Key Catalysts:
${data.key_catalysts.map(c => "  • " + c).join("\\n")}

Key Risks:
${data.key_risks.map(r => "  • " + r).join("\\n")}

Reasoning:
${data.reasoning}
                `.trim();
            }
        </script>
    </body>
    </html>
    """

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    ticker = request.ticker.strip().upper()

    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker is required")

    initial_state = {
        "ticker": ticker,
        "price_data": {},
        "fundamentals": {},
        "news_sentiment": {},
        "earnings_context": {},
        "recommendation": {},
    }

    result = agent.invoke(initial_state)
    return result["recommendation"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
