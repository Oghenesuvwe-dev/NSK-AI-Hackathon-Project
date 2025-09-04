import streamlit as st
import requests
import time

st.set_page_config(
    page_title="Advanced RAG Multi-Hop Research Agent", 
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Advanced RAG Multi-Hop Research Agent")
st.markdown("**AI agent for complex multi-step reasoning and analysis**")
st.markdown("---")

# API Selection
api_options = {
    "Basic RAG": "http://localhost:8000",
    "Mock RAG": "http://localhost:8003", 
    "Market RAG": "http://localhost:8004"
}

selected_api = st.selectbox("Select RAG Engine:", list(api_options.keys()))
API_URL = api_options[selected_api]

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎯 Multi-Hop Query Interface")
    
    example_queries = {
        "Select an example...": "",
        "⚽ Sports Analysis": "How did Arsenal's victory over Manchester City affect Liverpool's title chances?",
        "💰 Financial Impact": "How did AAPL's earnings affect MSFT stock price?",
        "🏢 Business Chain": "How did Company X's weak Q3 earnings affect its supplier Company Y?",
        "🌍 Global Events": "How did the 2024 earthquake affect Japan's GDP and semiconductor supply?",
        "✍️ Custom Query": ""
    }
    
    selected_example = st.selectbox("Choose query type:", list(example_queries.keys()))
    
    if selected_example == "✍️ Custom Query":
        query = st.text_area("Enter your multi-hop research question:", height=120)
    else:
        query = example_queries[selected_example]
        if query:
            st.text_area("Query:", value=query, height=120, disabled=True)
    
    if st.button("🚀 Execute Multi-Hop Analysis", type="primary", use_container_width=True):
        if query:
            with st.spinner("🔄 Processing multi-hop reasoning..."):
                start_time = time.time()
                try:
                    response = requests.post(
                        f"{API_URL}/query",
                        headers={"Content-Type": "application/json"},
                        json={"query": query}
                    )
                    
                    processing_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Metrics
                        col_m1, col_m2, col_m3 = st.columns(3)
                        with col_m1:
                            st.metric("⏱️ Time", f"{processing_time:.2f}s")
                        with col_m2:
                            st.metric("🔗 Hops", len(data.get("reasoning_steps", [])))
                        with col_m3:
                            st.metric("📚 Sources", len(data.get("sources", [])))
                        
                        st.success("✅ Analysis Complete!")
                        
                        # Reasoning steps
                        if data.get("reasoning_steps"):
                            st.subheader("🧠 Multi-Hop Reasoning Steps")
                            for i, step in enumerate(data["reasoning_steps"], 1):
                                with st.expander(f"Step {i}", expanded=True):
                                    st.write(step)
                        
                        # Answer
                        st.subheader("📝 Synthesized Answer")
                        st.markdown(data["answer"])
                        
                        # Sources
                        if data.get("sources"):
                            st.subheader("📚 Knowledge Sources")
                            for source in data["sources"]:
                                st.info(f"📄 {source}")
                                
                    else:
                        st.error(f"❌ API Error: {response.status_code}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Check if server is running.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please select or enter a research question")

with col2:
    st.subheader("📊 System Status")
    
    try:
        health = requests.get(f"{API_URL}/health", timeout=2)
        if health.status_code == 200:
            st.success("✅ API Online")
            data = health.json()
            st.info(f"🤖 Model: {data.get('model', 'N/A')}")
            st.info(f"🔧 Status: {data.get('status', 'healthy')}")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Offline")
    
    st.markdown("---")
    
    st.subheader("🚀 Features")
    features = [
        "Multi-hop reasoning",
        "Query decomposition", 
        "Evidence synthesis",
        "Source attribution",
        "Real-time analysis"
    ]
    
    for feature in features:
        st.write(f"✓ {feature}")

st.markdown("---")
st.markdown("**Advanced RAG Multi-Hop Research Agent** - NSKAI Hackathon 2025")