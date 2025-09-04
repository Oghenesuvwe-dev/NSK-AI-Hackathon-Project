from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from groq import Groq
import json
import glob
from pathlib import Path

load_dotenv()

app = FastAPI(title="Real RAG Multi-Hop Research Agent", version="6.0.0")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    reasoning_steps: list
    sources: list
    retrieved_documents: list

def load_documents():
    """Load real documents from data directory"""
    documents = {}
    data_dir = Path("data")
    
    if not data_dir.exists():
        return {}
    
    for file_path in data_dir.glob("*"):
        if file_path.is_file():
            try:
                content = file_path.read_text(encoding='utf-8')
                documents[file_path.name] = {
                    "content": content,
                    "metadata": {
                        "source": file_path.name,
                        "type": file_path.suffix[1:] if file_path.suffix else "txt",
                        "size": len(content)
                    }
                }
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    return documents

# Load documents at startup
DOCUMENT_DATABASE = load_documents()

def semantic_search(query: str, documents: dict, top_k: int = 2):
    """Simulate semantic search with keyword matching and relevance scoring"""
    query_lower = query.lower()
    results = []
    
    for doc_name, doc_data in documents.items():
        content_lower = doc_data["content"].lower()
        
        # Simple relevance scoring based on keyword matches
        score = 0
        query_words = query_lower.split()
        
        for word in query_words:
            if len(word) > 3:  # Skip short words
                score += content_lower.count(word) * len(word)
        
        if score > 0:
            results.append({
                "document": doc_name,
                "score": score,
                "content": doc_data["content"],
                "metadata": doc_data["metadata"]
            })
    
    # Sort by relevance score and return top_k
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def multi_hop_retrieval(sub_query: str, main_query: str):
    """Perform retrieval for a sub-query"""
    # Combine sub-query with main query for better context
    search_query = f"{sub_query} {main_query}"
    
    # Perform semantic search
    results = semantic_search(search_query, DOCUMENT_DATABASE, top_k=1)
    
    if results:
        best_match = results[0]
        return {
            "sub_question": sub_query,
            "document": best_match["document"],
            "relevance_score": best_match["score"],
            "content": best_match["content"][:500] + "..." if len(best_match["content"]) > 500 else best_match["content"],
            "source": best_match["metadata"]["source"]
        }
    else:
        return {
            "sub_question": sub_query,
            "document": "No relevant document found",
            "relevance_score": 0,
            "content": "No matching content found for this query.",
            "source": "None"
        }

@app.post("/query", response_model=QueryResponse)
def run_query(request: QueryRequest):
    try:
        if not DOCUMENT_DATABASE:
            raise HTTPException(status_code=500, detail="No documents loaded. Please add documents to the data/ directory.")
        
        # Step 1: Query decomposition
        decomposition_prompt = f"""
        Decompose this complex query into 2-4 specific sub-questions for multi-hop reasoning:
        Query: "{request.query}"
        
        Each sub-question should target a specific piece of information needed to answer the main query.
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
        
        # Step 2: Multi-hop document retrieval
        retrieved_docs = []
        reasoning_steps = []
        
        for i, sub_q in enumerate(sub_questions, 1):
            doc_result = multi_hop_retrieval(sub_q, request.query)
            retrieved_docs.append(doc_result)
            reasoning_steps.append(f"Step {i}: {sub_q} → Retrieved from {doc_result['source']} (score: {doc_result['relevance_score']})")
        
        # Step 3: Evidence synthesis
        synthesis_prompt = f"""
        You are an expert analyst. Synthesize information from multiple documents to answer this query:
        
        Original Query: {request.query}
        
        Retrieved Evidence:
        {json.dumps([{k: v for k, v in doc.items() if k != 'content'} for doc in retrieved_docs], indent=2)}
        
        Document Contents:
        {chr(10).join([f"Document: {doc['document']}{chr(10)}{doc['content']}{chr(10)}" for doc in retrieved_docs])}
        
        Provide a comprehensive answer that:
        1. Directly addresses the original query
        2. Uses specific facts and numbers from the documents
        3. Shows clear reasoning connecting the evidence
        4. Cites sources appropriately
        """
        
        final_response = client.chat.completions.create(
            messages=[{"role": "user", "content": synthesis_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=2000
        )
        
        sources = list(set([doc["source"] for doc in retrieved_docs if doc["source"] != "None"]))
        
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
        "message": "Real RAG Multi-Hop Research Agent", 
        "version": "6.0.0",
        "features": ["Real document processing", "Semantic search", "Multi-hop reasoning"],
        "documents_loaded": len(DOCUMENT_DATABASE)
    }

@app.get("/health")
def health():
    return {
        "status": "healthy", 
        "model": "llama-3.3-70b-versatile",
        "documents_loaded": len(DOCUMENT_DATABASE),
        "document_types": list(set([doc["metadata"]["type"] for doc in DOCUMENT_DATABASE.values()])),
        "real_rag": True
    }

@app.get("/documents")
def list_documents():
    return {
        "total_documents": len(DOCUMENT_DATABASE),
        "documents": [
            {
                "filename": name, 
                "type": doc["metadata"]["type"],
                "size": doc["metadata"]["size"],
                "preview": doc["content"][:100] + "..." if len(doc["content"]) > 100 else doc["content"]
            } 
            for name, doc in DOCUMENT_DATABASE.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)