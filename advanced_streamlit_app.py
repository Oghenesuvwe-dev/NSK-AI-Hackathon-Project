import streamlit as st
import requests
import time
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import json

st.set_page_config(
    page_title="Advanced RAG Multi-Hop Research Agent", 
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get API URL from secrets or use default
try:
    API_URL = st.secrets["API_URL"]
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    API_URL = "http://localhost:8003"
    GROQ_API_KEY = None

st.markdown('<h1 style="text-align: center;">🔍 Advanced RAG Multi-Hop Research Agent</h1>', unsafe_allow_html=True)
st.markdown("<div style='text-align: center; margin-bottom: 2rem;'>AI agent for complex multi-step reasoning and analysis</div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Status
    try:
        health = requests.get(f"{API_URL}/health", timeout=2)
        if health.status_code == 200:
            st.success("🟢 API Online")
        else:
            st.error("🔴 API Offline")
    except:
        st.error("🔴 API Disconnected")

# Main Interface
tab1, tab2 = st.tabs(["🎯 Query Interface", "📊 Analytics"])

with tab1:
    st.subheader("🎯 Multi-Hop Query Interface")
    
    example_queries = {
        "Select Example": "",
        "Sports Analysis": "How did Arsenal's victory over Manchester City affect Liverpool's title chances?",
        "Financial Impact": "How did AAPL's earnings affect MSFT stock price?",
        "Business Chain": "How did Company X's weak Q3 earnings affect its supplier Company Y?",
        "Global Events": "How did the 2024 earthquake affect Japan's GDP and semiconductor supply?"
    }
    
    selected_example = st.selectbox("Choose query type:", list(example_queries.keys()))
    
    if selected_example == "Select Example":
        query = st.text_area("Enter your multi-hop research question:", height=120)
    else:
        query = example_queries[selected_example]
        st.text_area("Query:", value=query, height=120, disabled=True)
    
    if st.button("🚀 Execute Multi-Hop Analysis", type="primary"):
        if query:
            with st.spinner("🔄 Processing multi-hop reasoning..."):
                try:
                    response = requests.post(
                        f"{API_URL}/query",
                        headers={"Content-Type": "application/json"},
                        json={"query": query}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        st.success("✅ Multi-Hop Analysis Complete!")
                        
                        # Metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🔗 Reasoning Hops", len(data.get("reasoning_steps", [])))
                        with col2:
                            st.metric("📚 Sources Found", len(data.get("sources", [])))
                        with col3:
                            st.metric("✅ Status", "Complete")
                        
                        # Reasoning steps
                        if data.get("reasoning_steps"):
                            st.subheader("🧠 Multi-Hop Reasoning Chain")
                            for i, step in enumerate(data["reasoning_steps"], 1):
                                with st.expander(f"🔗 Hop {i}: {step[:50]}...", expanded=i==1):
                                    st.write(step)
                        
                        # Final answer
                        st.subheader("📝 Synthesized Answer")
                        st.info(data["answer"])
                        
                        # Sources
                        if data.get("sources"):
                            st.subheader("📚 Knowledge Sources")
                            for source in data["sources"]:
                                st.write(f"📄 {source}")
                                
                    else:
                        st.error(f"❌ API Error: {response.status_code}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Using mock response for demo.")
                    
                    # Mock response for deployment demo
                    st.success("✅ Multi-Hop Analysis Complete! (Demo Mode)")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🔗 Reasoning Hops", "3")
                    with col2:
                        st.metric("📚 Sources Found", "4")
                    with col3:
                        st.metric("✅ Status", "Complete")
                    
                    st.subheader("🧠 Multi-Hop Reasoning Chain")
                    with st.expander("🔗 Hop 1: Initial Query Analysis", expanded=True):
                        st.write("Analyzing the complex query to identify key components and relationships...")
                    
                    with st.expander("🔗 Hop 2: Multi-Source Retrieval"):
                        st.write("Retrieving relevant information from multiple document sources...")
                    
                    with st.expander("🔗 Hop 3: Evidence Synthesis"):
                        st.write("Synthesizing evidence from different sources to form coherent answer...")
                    
                    st.subheader("📝 Synthesized Answer")
                    st.info("This is a demo response showing how the multi-hop RAG system would analyze your query by breaking it down into sub-questions, retrieving evidence from multiple sources, and synthesizing a comprehensive answer with proper citations.")
                    
                    st.subheader("📚 Knowledge Sources")
                    st.write("📄 Document 1: Primary source analysis")
                    st.write("📄 Document 2: Supporting evidence")
                    st.write("📄 Document 3: Cross-reference validation")
                    st.write("📄 Document 4: Additional context")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please select or enter a research question")

with tab2:
    st.subheader("📊 Analytics Dashboard")
    
    # Mock analytics data
    col1, col2 = st.columns(2)
    
    with col1:
        query_types = ['Sports', 'Financial', 'Business', 'Global Events']
        query_counts = [15, 23, 18, 12]
        
        fig_pie = px.pie(values=query_counts, names=query_types, title="Query Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        response_times = [2.1 + 0.5 * (i % 7) for i in range(30)]
        
        fig_line = px.line(x=dates, y=response_times, title="Response Time Trends")
        fig_line.update_xaxes(title="Date")
        fig_line.update_yaxes(title="Response Time (s)")
        st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")
st.markdown("<div style='text-align: center;'>**Advanced RAG Multi-Hop Research Agent** - NSKAI Hackathon 2025</div>", unsafe_allow_html=True)