from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = FastAPI(title="Advanced RAG Multi-Hop Research Agent", version="1.0.0")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    reasoning_steps: list
    sources: list

@app.post("/query", response_model=QueryResponse)
def run_query(request: QueryRequest):
    try:
        prompt = f"""
        You are an expert multi-hop research agent. For the query: "{request.query}"
        
        Please:
        1. Break down the query into logical sub-questions
        2. Answer each sub-question step by step
        3. Synthesize the information to provide a comprehensive final answer
        4. Show your reasoning process clearly
        
        Format your response as:
        REASONING STEPS:
        1. [First step]
        2. [Second step]
        3. [Third step]
        
        FINAL ANSWER:
        [Comprehensive answer]
        """
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=3000
        )
        
        content = response.choices[0].message.content
        
        # Parse reasoning steps
        steps = []
        if "REASONING STEPS:" in content:
            reasoning_section = content.split("REASONING STEPS:")[1].split("FINAL ANSWER:")[0]
            steps = [line.strip() for line in reasoning_section.split('\n') if line.strip() and line.strip().startswith(('1.', '2.', '3.', '4.', '5.'))]
        
        # Extract final answer
        final_answer = content
        if "FINAL ANSWER:" in content:
            final_answer = content.split("FINAL ANSWER:")[1].strip()
        
        return QueryResponse(
            answer=final_answer,
            reasoning_steps=steps,
            sources=["Multi-hop LLM Analysis"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "Advanced RAG Multi-Hop Research Agent", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy", "model": "llama-3.3-70b-versatile"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)