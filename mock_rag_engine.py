from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from groq import Groq
import json

load_dotenv()

app = FastAPI(title="Advanced RAG Multi-Hop Research Agent", version="4.0.0")
client = Groq(api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY"))

# Mock document database
MOCK_DOCUMENTS = {
    "arsenal_vs_city_match.md": {
        "content": "Arsenal defeated Manchester City 1-0 on March 31, 2024, at Emirates Stadium. Gabriel Martinelli scored the winning goal in the 86th minute. This crucial victory moved Arsenal to 2nd place in the Premier League table.",
        "metadata": {"source": "Match Report", "date": "2024-03-31", "type": "sports"}
    },
    "premier_league_table_april2024.csv": {
        "content": "Team,Points,Position\nManchester City,73,1\nArsenal,71,2\nLiverpool,70,3\nAfter Arsenal's victory: City 73pts, Arsenal 74pts, Liverpool 70pts",
        "metadata": {"source": "Premier League Official", "date": "2024-04-01", "type": "standings"}
    },
    "sports_analytics_report.pdf": {
        "content": "Arsenal's victory over City increased Liverpool's title chances from 15% to 28%. With City dropping points, Liverpool now needs to win remaining fixtures while hoping for further City slip-ups.",
        "metadata": {"source": "The Athletic Analytics", "date": "2024-04-01", "type": "analysis"}
    },
    "company_x_earnings_q3.pdf": {
        "content": "Company X reported Q3 earnings with revenue down 15% to $2.1B. CEO cited supply chain disruptions and reduced demand. Stock fell 8% in after-hours trading.",
        "metadata": {"source": "SEC Filing", "date": "2024-10-25", "type": "financial"}
    },
    "supply_chain_analysis.md": {
        "content": "Company Y supplies 40% of Company X's critical components. The companies have a 10-year partnership. Company Y's revenue is 60% dependent on Company X orders.",
        "metadata": {"source": "Industry Analysis", "date": "2024-09-15", "type": "business"}
    },
    "nasdaq_prices_oct2024.csv": {
        "content": "Date,Company_Y_Price\n2024-10-24,$45.20\n2024-10-25,$44.80\n2024-10-26,$42.15\n2024-10-27,$41.90\n2024-10-28,$40.25",
        "metadata": {"source": "NASDAQ", "date": "2024-10-28", "type": "market_data"}
    }
}

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    reasoning_steps: list
    sources: list
    retrieved_documents: list

def mock_retrieval(sub_query: str, query_context: str) -> dict:
    """Simulate document retrieval based on query content"""
    query_lower = sub_query.lower() + " " + query_context.lower()
    
    # Simple keyword matching for document retrieval
    if any(word in query_lower for word in ["arsenal", "city", "liverpool", "premier league", "title"]):
        if "match" in query_lower or "result" in query_lower:
            return MOCK_DOCUMENTS["arsenal_vs_city_match.md"]
        elif "table" in query_lower or "standings" in query_lower:
            return MOCK_DOCUMENTS["premier_league_table_april2024.csv"]
        elif "chances" in query_lower or "probability" in query_lower:
            return MOCK_DOCUMENTS["sports_analytics_report.pdf"]
    
    elif any(word in query_lower for word in ["company x", "earnings", "supplier", "company y"]):
        if "earnings" in query_lower or "financial" in query_lower:
            return MOCK_DOCUMENTS["company_x_earnings_q3.pdf"]
        elif "supplier" in query_lower or "supply chain" in query_lower:
            return MOCK_DOCUMENTS["supply_chain_analysis.md"]
        elif "stock price" in query_lower or "price" in query_lower:
            return MOCK_DOCUMENTS["nasdaq_prices_oct2024.csv"]
    
    return {"content": "No relevant document found", "metadata": {"source": "None", "type": "none"}}

@app.post("/query", response_model=QueryResponse)
def run_query(request: QueryRequest):
    try:
        # Step 1: Query decomposition
        decomposition_prompt = f"""
        Decompose this complex query into 2-4 sub-questions for multi-hop reasoning:
        Query: "{request.query}"
        
        Return ONLY a JSON array of sub-questions, like:
        ["sub-question 1", "sub-question 2", "sub-question 3"]
        """
        
        decomp_response = client.chat.completions.create(
            messages=[{"role": "user", "content": decomposition_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        
        try:
            sub_questions = json.loads(decomp_response.choices[0].message.content)
        except:
            sub_questions = [request.query]  # Fallback
        
        # Step 2: Multi-hop retrieval
        retrieved_docs = []
        reasoning_steps = []
        
        for i, sub_q in enumerate(sub_questions, 1):
            doc = mock_retrieval(sub_q, request.query)
            retrieved_docs.append({
                "sub_question": sub_q,
                "document": doc["metadata"]["source"],
                "content": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
            })
            reasoning_steps.append(f"Step {i}: {sub_q} → Retrieved from {doc['metadata']['source']}")
        
        # Step 3: Synthesis
        synthesis_prompt = f"""
        Original Query: {request.query}
        
        Retrieved Evidence:
        {json.dumps(retrieved_docs, indent=2)}
        
        Synthesize a comprehensive answer using the retrieved evidence. Include specific facts and maintain citations.
        """
        
        final_response = client.chat.completions.create(
            messages=[{"role": "user", "content": synthesis_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=2000
        )
        
        sources = list(set([doc["document"] for doc in retrieved_docs]))
        
        return QueryResponse(
            answer=final_response.choices[0].message.content,
            reasoning_steps=reasoning_steps,
            sources=sources,
            retrieved_documents=retrieved_docs
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {
        "message": "Advanced RAG Multi-Hop Research Agent", 
        "version": "4.0.0",
        "features": ["Multi-hop reasoning", "Document retrieval", "Evidence synthesis", "Citation support"]
    }

@app.get("/health")
def health():
    return {
        "status": "healthy", 
        "model": "llama-3.3-70b-versatile",
        "documents_loaded": len(MOCK_DOCUMENTS),
        "rag_enabled": True
    }

@app.get("/documents")
def list_documents():
    return {
        "total_documents": len(MOCK_DOCUMENTS),
        "documents": [
            {"filename": k, "source": v["metadata"]["source"], "type": v["metadata"]["type"]} 
            for k, v in MOCK_DOCUMENTS.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)