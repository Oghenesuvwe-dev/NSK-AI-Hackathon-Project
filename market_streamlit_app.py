import streamlit as st
import requests
import json
import time

st.set_page_config(
    page_title="Market Data RAG Agent", 
    page_icon="📈",
    layout="wide"
)

st.title("📈 Market Data RAG Multi-Hop Agent")
st.markdown("**Real-Time Market Analysis with Multi-Document Reasoning**")
st.markdown("---")

API_URL = "http://localhost:8004"

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎯 Market Analysis Query")
    
    market_queries = {
        "Select example...": "",
        "Stock Impact Analysis": "How did AAPL's latest earnings affect MSFT's stock price?",
        "Market Correlation": "What's the relationship between TSLA stock performance and NVDA?",
        "Sector Analysis": "How did tech sector news impact GOOGL and META stocks?",
        "Custom Query": ""
    }
    
    selected_query = st.selectbox("Choose market query:", list(market_queries.keys()))
    
    if selected_query == "Custom Query":
        query = st.text_area("Enter market analysis question:", height=120)
    else:
        query = market_queries[selected_query]
        if query:
            st.text_area("Query:", value=query, height=120, disabled=True)
    
    # Quick stock lookup
    st.subheader("📊 Quick Stock Data")
    col_a, col_b = st.columns(2)
    
    with col_a:
        symbol = st.text_input("Stock Symbol:", placeholder="AAPL")
    
    with col_b:
        if st.button("Get Real-Time Data"):
            if symbol:
                try:
                    response = requests.get(f"{API_URL}/market/{symbol}")
                    if response.status_code == 200:
                        data = response.json()
                        if "error" not in data:
                            st.success(f"**{data['company_name']}** ({data['symbol']})")
                            st.metric("Price", f"${data['current_price']}", f"{data['change']} ({data['change_percent']}%)")
                            st.write(f"Volume: {data['volume']:,}")
                        else:
                            st.error(data['error'])
                except:
                    st.error("Failed to fetch data")
    
    if st.button("🚀 Execute Market Analysis", type="primary", use_container_width=True):
        if query:
            with st.spinner("📈 Analyzing market data..."):
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
                        
                        st.success(f"✅ Market Analysis Complete! ({processing_time:.2f}s)")
                        
                        # Display retrieved market data
                        if data.get("retrieved_data"):
                            st.subheader("📊 Retrieved Market Data")
                            for i, item in enumerate(data["retrieved_data"], 1):
                                with st.expander(f"Data Source {i}: {item['sub_question']}", expanded=True):
                                    st.info(f"**Source:** {item['data_source']}")
                                    st.code(item['content'])
                        
                        # Display reasoning
                        if data.get("reasoning_steps"):
                            st.subheader("🧠 Analysis Pipeline")
                            for step in data["reasoning_steps"]:
                                st.write(f"• {step}")
                        
                        # Display analysis
                        st.subheader("📝 Market Analysis")
                        st.markdown(data["answer"])
                        
                        # Display sources
                        if data.get("sources"):
                            st.subheader("📡 Data Sources")
                            for source in data["sources"]:
                                st.success(f"📈 {source}")
                                
                    else:
                        st.error(f"❌ API Error: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a market query")

with col2:
    st.subheader("📊 System Status")
    
    try:
        health = requests.get(f"{API_URL}/health", timeout=2)
        if health.status_code == 200:
            data = health.json()
            st.success("✅ Market Data System Online")
            st.info(f"🤖 Model: {data.get('model', 'Unknown')}")
            st.info(f"📈 Real-Time Data: {data.get('real_time_data', False)}")
            
            st.subheader("📡 Data Sources")
            for source in data.get('data_sources', []):
                st.write(f"• {source}")
        else:
            st.error("❌ System Offline")
    except:
        st.error("❌ Cannot connect to system")
    
    st.markdown("---")
    
    st.subheader("📈 Supported Symbols")
    symbols = ["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA", "AMZN", "META"]
    for symbol in symbols:
        st.write(f"• {symbol}")
    
    st.subheader("🔧 Features")
    features = [
        "Real-time stock data",
        "Market news integration",
        "Multi-hop analysis",
        "Financial synthesis",
        "Cross-asset correlation"
    ]
    
    for feature in features:
        st.write(f"✓ {feature}")

st.markdown("---")
st.markdown("**Market Data RAG Agent** - Real-Time Financial Analysis | NSKAI Hackathon")