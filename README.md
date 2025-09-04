# Advanced RAG Multi-Hop Research Agent

AI agent that decomposes complex questions into sub-queries, retrieves evidence from multiple documents, and synthesizes cited answers.

**Example:** "How did Company X's Q3 earnings affect supplier Company Y's stock?"
1. Find main supplier → Company Y
2. Get Q3 data → 15% profit drop Oct 25th  
3. Check Y stock → 12% decline Oct 26-31
4. Synthesize with citations

## 🚀 Quick Start

```bash
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key" > .env

# Real RAG (Recommended)
python -m uvicorn real_rag_engine:app --port 8006 & streamlit run final_streamlit_app.py

# Market Data RAG  
python -m uvicorn market_data_rag:app --port 8004 & streamlit run market_streamlit_app.py

# Mock RAG
python -m uvicorn mock_rag_engine:app --port 8003 & streamlit run advanced_streamlit_app.py
```

## 🔍 Features

- Multi-hop reasoning with query decomposition
- Real market data via Yahoo Finance API
- Multi-source document retrieval and synthesis
- Automatic citation and source attribution

## 📊 Multi-Hop Examples

**Football:** "How did Arsenal's victory over City affect Liverpool's title chances?"
→ Match result + League table + Expert analysis

**Economics:** "Impact of Noto Peninsula earthquake on Japan's GDP/semiconductors?"
→ Disaster scale + GDP forecasts + Production disruptions

**Corporate:** "How did OpenAI investment impact Microsoft Azure revenue?"
→ Investment details + Revenue reports + Analyst attribution

## 🛠️ Tech Stack

- **Backend:** FastAPI + Groq LLM (llama-3.3-70b)
- **Vector DB:** ChromaDB + SentenceTransformers
- **Data:** Yahoo Finance API, PDF/CSV/MD processing
- **Frontend:** Streamlit + REST API

## 🏗️ Architecture

```
User Query → Decomposition → Multi-Hop Retrieval → Synthesis → Cited Answer
     │            │               │                │
   Groq LLM   Sub-queries   Vector Search     Final Response
```

1. LLM decomposes query into sub-questions
2. Each sub-query searches document sources  
3. Evidence collected with metadata
4. LLM synthesizes coherent, cited answer

## 📡 API Endpoints

| System | Port | Endpoints |
|--------|------|----------|
| **Real RAG** (Recommended) | 8006 | `POST /query`, `GET /documents`, `GET /health` |
| **Market Data** | 8004 | `POST /query`, `GET /market/{symbol}`, `GET /health` |
| **Mock RAG** | 8003 | `POST /query`, `GET /documents`, `GET /health` |

## 🎯 NSKAI Hackathon Submission

**Repository:** https://github.com/Oghenesuvwe-dev/NSKAI-RAG-Bootcamp-2025  
**Branch:** Multi-Hop-Research-Agent  
**Demo:** Streamlit Cloud deployment ready