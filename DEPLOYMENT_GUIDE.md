# Streamlit Cloud Deployment Guide

## 🚀 Deploy to Streamlit Cloud

### Step 1: Prepare Environment Variables

Create `.streamlit/secrets.toml` for Streamlit Cloud:

```toml
[secrets]
GROQ_API_KEY = "your_groq_api_key_here"
API_URL = "https://your-fastapi-app.herokuapp.com"
```

### Step 2: Update Streamlit App for Cloud

The app will automatically use Streamlit secrets in cloud environment.

### Step 3: Deploy Options

#### Option A: Streamlit Cloud Only (Recommended)
1. Go to https://share.streamlit.io
2. Connect GitHub repository: `Oghenesuvwe-dev/NSKAI-RAG-Bootcamp-2025`
3. Select branch: `Multi-Hop-Research-Agent`
4. Main file: `advanced_streamlit_app.py`
5. Add secrets in Streamlit Cloud dashboard

#### Option B: FastAPI + Streamlit Separate
1. Deploy FastAPI to Heroku/Railway
2. Deploy Streamlit to Streamlit Cloud
3. Update API_URL in secrets

## 🔧 Local Development

```bash
# 1. Clone repository
git clone https://github.com/Oghenesuvwe-dev/NSKAI-RAG-Bootcamp-2025.git
cd NSKAI-RAG-Bootcamp-2025
git checkout Multi-Hop-Research-Agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# 4. Run FastAPI (Terminal 1)
python -m uvicorn mock_rag_engine:app --port 8003

# 5. Run Streamlit (Terminal 2)
streamlit run advanced_streamlit_app.py
```

## 📋 Environment Variables

Required for deployment:
- `GROQ_API_KEY`: Your Groq API key
- `API_URL`: FastAPI endpoint (optional for local)