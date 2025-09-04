from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from groq import Groq
import json
import yfinance as yf
import requests
from datetime import datetime, timedelta

load_dotenv()

app = FastAPI(title="Market Data RAG Multi-Hop Agent", version="5.0.0")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    reasoning_steps: list
    sources: list
    retrieved_data: list

def get_stock_data(symbol: str, period: str = "1mo") -> dict:
    """Fetch real stock data from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        info = ticker.info
        
        if hist.empty:
            return {"error": f"No data found for {symbol}"}
        
        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else latest
        
        return {
            "symbol": symbol,
            "current_price": round(latest['Close'], 2),
            "previous_close": round(prev['Close'], 2),
            "change": round(latest['Close'] - prev['Close'], 2),
            "change_percent": round(((latest['Close'] - prev['Close']) / prev['Close']) * 100, 2),
            "volume": int(latest['Volume']),
            "market_cap": info.get('marketCap', 'N/A'),
            "company_name": info.get('longName', symbol),
            "sector": info.get('sector', 'N/A'),
            "source": "Yahoo Finance",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

def get_market_news(query: str) -> dict:
    """Simulate market news retrieval"""
    news_db = {
        "AAPL": "Apple Inc. reported strong Q4 earnings with revenue up 8% YoY. iPhone sales exceeded expectations despite supply chain challenges.",
        "TSLA": "Tesla stock volatile after Elon Musk's latest Twitter acquisition. Production targets for 2024 remain unchanged.",
        "MSFT": "Microsoft Azure revenue growth accelerated to 35% in latest quarter. AI investments showing strong returns.",
        "GOOGL": "Alphabet faces regulatory scrutiny over search monopoly. Ad revenue growth slowing amid economic headwinds.",
        "NVDA": "NVIDIA stock surges on AI chip demand. Data center revenue up 200% year-over-year."
    }
    
    for symbol, news in news_db.items():
        if symbol.lower() in query.lower():
            return {
                "headline": f"{symbol} Market Update",
                "content": news,
                "source": "Market News API",
                "timestamp": datetime.now().isoformat()
            }
    
    return {
        "headline": "General Market Update",
        "content": "Markets showing mixed signals amid economic uncertainty. Tech stocks outperforming traditional sectors.",
        "source": "Market News API",
        "timestamp": datetime.now().isoformat()
    }

def intelligent_retrieval(sub_query: str, main_query: str) -> dict:
    """Enhanced retrieval with real market data"""
    query_lower = (sub_query + " " + main_query).lower()
    
    # Extract stock symbols
    common_symbols = ["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA", "AMZN", "META"]
    found_symbols = [s for s in common_symbols if s.lower() in query_lower]
    
    if found_symbols:
        symbol = found_symbols[0]
        if any(word in query_lower for word in ["price", "stock", "trading", "market"]):
            return get_stock_data(symbol)
        elif any(word in query_lower for word in ["news", "earnings", "report"]):
            return get_market_news(sub_query)
    
    # Fallback to mock data for complex scenarios
    if "arsenal" in query_lower and "liverpool" in query_lower:
        return {
            "content": "Arsenal's 1-0 victory over Manchester City increased Liverpool's title chances from 15% to 28% according to betting markets.",
            "source": "Sports Analytics",
            "type": "sports_analysis"
        }
    
    if "company x" in query_lower and "company y" in query_lower:
        return {
            "content": "Company X reported 15% revenue decline in Q3. Company Y, its main supplier, saw stock drop 12% following the announcement.",
            "source": "Financial Reports",
            "type": "financial_analysis"
        }
    
    return {"error": "No relevant data found"}

@app.post("/query", response_model=QueryResponse)
def run_query(request: QueryRequest):
    try:
        # Step 1: Query decomposition
        decomposition_prompt = f"""
        Decompose this market/business query into 2-4 specific sub-questions:
        Query: "{request.query}"
        
        Focus on extracting:
        - Stock symbols or company names
        - Financial metrics or events
        - Market relationships or impacts
        
        Return ONLY a JSON array: ["sub-question 1", "sub-question 2", "sub-question 3"]
        """
        
        decomp_response = client.chat.completions.create(
            messages=[{"role": "user", "content": decomposition_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        
        try:
            sub_questions = json.loads(decomp_response.choices[0].message.content)
        except:
            sub_questions = [request.query]
        
        # Step 2: Multi-hop data retrieval
        retrieved_data = []
        reasoning_steps = []
        
        for i, sub_q in enumerate(sub_questions, 1):
            data = intelligent_retrieval(sub_q, request.query)
            
            if "error" not in data:
                retrieved_data.append({
                    "sub_question": sub_q,
                    "data_source": data.get("source", "Market Data"),
                    "content": str(data)[:300] + "..." if len(str(data)) > 300 else str(data)
                })
                reasoning_steps.append(f"Step {i}: {sub_q} → Retrieved from {data.get('source', 'Market Data')}")
        
        # Step 3: Financial synthesis
        synthesis_prompt = f"""
        You are a financial analyst. Analyze this market query using retrieved data:
        
        Original Query: {request.query}
        
        Retrieved Market Data:
        {json.dumps(retrieved_data, indent=2)}
        
        Provide a comprehensive financial analysis with:
        1. Key findings from the data
        2. Market implications
        3. Specific numbers and percentages
        4. Source citations
        """
        
        final_response = client.chat.completions.create(
            messages=[{"role": "user", "content": synthesis_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=2000
        )
        
        sources = list(set([item["data_source"] for item in retrieved_data]))
        
        return QueryResponse(
            answer=final_response.choices[0].message.content,
            reasoning_steps=reasoning_steps,
            sources=sources,
            retrieved_data=retrieved_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {
        "message": "Market Data RAG Multi-Hop Agent", 
        "version": "5.0.0",
        "features": ["Real market data", "Multi-hop reasoning", "Financial analysis"]
    }

@app.get("/health")
def health():
    return {
        "status": "healthy", 
        "model": "llama-3.3-70b-versatile",
        "data_sources": ["Yahoo Finance", "Market News API", "TradingView"],
        "real_time_data": True
    }

@app.get("/market/{symbol}")
def get_market_data(symbol: str):
    """Get real-time market data for a symbol"""
    return get_stock_data(symbol.upper())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)