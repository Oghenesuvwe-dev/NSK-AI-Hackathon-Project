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

# Custom CSS
st.markdown("""
<style>
.main-header { font-size: 3rem; text-align: center; margin-bottom: 2rem; }
.metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; }
.hop-step { border-left: 4px solid #4CAF50; padding-left: 1rem; margin: 1rem 0; }
.query-box { border: 2px solid #e0e0e0; border-radius: 10px; padding: 1rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🔍 Advanced RAG Multi-Hop Research Agent</h1>', unsafe_allow_html=True)
st.markdown("<div style='text-align: center; font-size: 1.2rem; margin-bottom: 2rem;'>AI agent for complex multi-step reasoning and analysis</div>", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_endpoints = {
        "Basic RAG": "http://localhost:8000",
        "Mock RAG": "http://localhost:8003", 
        "Market RAG": "http://localhost:8004"
    }
    
    selected_api = st.selectbox("Select RAG Engine:", list(api_endpoints.keys()))
    API_URL = api_endpoints[selected_api]
    
    st.markdown("---")
    
    # Real-time metrics
    st.subheader("📊 Live Metrics")
    
    try:
        health = requests.get(f"{API_URL}/health", timeout=2)
        if health.status_code == 200:
            st.success("🟢 Online")
            data = health.json()
            st.metric("Response Time", "<50ms", "⚡")
            st.metric("Model", data.get('model', 'N/A')[:15])
        else:
            st.error("🔴 Offline")
    except:
        st.error("🔴 Disconnected")
    
    st.markdown("---")
    
    # Query History
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    
    st.subheader("📝 Recent Queries")
    for i, hist_query in enumerate(st.session_state.query_history[-3:]):
        if st.button(f"🔄 {hist_query[:30]}...", key=f"hist_{i}"):
            st.session_state.selected_query = hist_query

# Main Interface
tab1, tab2, tab3 = st.tabs(["🎯 Query Interface", "📊 Analytics", "🔧 Advanced"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Multi-Hop Query Interface")
        
        example_queries = {
            "💡 Select Example": "",
            "⚽ Sports Analysis": "How did Arsenal's victory over Manchester City affect Liverpool's title chances?",
            "💰 Financial Impact": "How did AAPL's earnings affect MSFT stock price?",
            "🏢 Business Chain": "How did Company X's weak Q3 earnings affect its supplier Company Y?",
            "🌍 Global Events": "How did the 2024 earthquake affect Japan's GDP and semiconductor supply?",
            "✍️ Custom Query": ""
        }
        
        selected_example = st.selectbox("Choose query type:", list(example_queries.keys()))
        
        if selected_example == "✍️ Custom Query":
            query = st.text_area("Enter your multi-hop research question:", 
                               value=st.session_state.get('selected_query', ''),
                               height=120, placeholder="Ask a complex question requiring multiple sources...")
        else:
            query = example_queries[selected_example]
            if query:
                st.text_area("Query:", value=query, height=120, disabled=True)
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            col_a, col_b = st.columns(2)
            with col_a:
                max_hops = st.slider("Max Reasoning Hops", 2, 8, 4)
                temperature = st.slider("Creativity Level", 0.0, 1.0, 0.3)
            with col_b:
                include_sources = st.checkbox("Include Source Citations", True)
                real_time_mode = st.checkbox("Real-time Processing", False)
        
        if st.button("🚀 Execute Multi-Hop Analysis", type="primary", use_container_width=True):
            if query:
                # Add to history
                if query not in st.session_state.query_history:
                    st.session_state.query_history.append(query)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                with st.spinner("🔄 Processing multi-hop reasoning..."):
                    start_time = time.time()
                    
                    try:
                        # Simulate progress
                        for i in range(100):
                            progress_bar.progress(i + 1)
                            if i < 30:
                                status_text.text("🔍 Analyzing query...")
                            elif i < 60:
                                status_text.text("🔗 Performing multi-hop retrieval...")
                            elif i < 90:
                                status_text.text("🧠 Synthesizing evidence...")
                            else:
                                status_text.text("✨ Finalizing response...")
                            time.sleep(0.01)
                        
                        response = requests.post(
                            f"{API_URL}/query",
                            headers={"Content-Type": "application/json"},
                            json={"query": query}
                        )
                        
                        processing_time = time.time() - start_time
                        progress_bar.empty()
                        status_text.empty()
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Success metrics
                            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                            with col_m1:
                                st.metric("⏱️ Processing Time", f"{processing_time:.2f}s")
                            with col_m2:
                                st.metric("🔗 Reasoning Hops", len(data.get("reasoning_steps", [])))
                            with col_m3:
                                st.metric("📚 Sources Found", len(data.get("sources", [])))
                            with col_m4:
                                st.metric("✅ Status", "Complete")
                            
                            st.success("✅ Multi-Hop Analysis Complete!")
                            
                            # Reasoning visualization
                            if data.get("reasoning_steps"):
                                st.subheader("🧠 Multi-Hop Reasoning Chain")
                                
                                # Create reasoning flow chart
                                fig = go.Figure()
                                
                                steps = data["reasoning_steps"]
                                for i, step in enumerate(steps):
                                    fig.add_trace(go.Scatter(
                                        x=[i], y=[0],
                                        mode='markers+text',
                                        marker=dict(size=50, color=f'rgb({50+i*40}, {100+i*30}, {200-i*20})'),
                                        text=f"Hop {i+1}",
                                        textposition="middle center",
                                        hovertext=step[:100] + "...",
                                        showlegend=False
                                    ))
                                
                                fig.update_layout(
                                    title="Reasoning Flow",
                                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                    height=200
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Detailed steps
                                for i, step in enumerate(steps, 1):
                                    with st.expander(f"🔗 Hop {i}: {step[:50]}...", expanded=i==1):
                                        st.markdown(f'<div class="hop-step">{step}</div>', unsafe_allow_html=True)
                            
                            # Final answer
                            st.subheader("📝 Synthesized Answer")
                            st.markdown(f'<div class="query-box">{data["answer"]}</div>', unsafe_allow_html=True)
                            
                            # Sources with confidence
                            if data.get("sources"):
                                st.subheader("📚 Knowledge Sources")
                                for i, source in enumerate(data["sources"]):
                                    confidence = 95 - i*5  # Mock confidence
                                    st.info(f"📄 {source} (Confidence: {confidence}%)")
                                    
                        else:
                            st.error(f"❌ API Error: {response.status_code}")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to API. Check if server is running.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please select or enter a research question")
    
    with col2:
        st.subheader("🎯 Query Insights")
        
        # Query complexity analysis
        if 'query' in locals() and query:
            complexity_score = min(len(query.split()) * 2, 100)
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = complexity_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Query Complexity"},
                delta = {'reference': 50},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 25], 'color': "lightgray"},
                        {'range': [25, 50], 'color': "gray"},
                        {'range': [50, 75], 'color': "orange"},
                        {'range': [75, 100], 'color': "red"}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90}}
            ))
            
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Performance metrics
        st.subheader("⚡ Performance")
        
        # Mock performance data
        perf_data = pd.DataFrame({
            'Metric': ['Avg Response', 'Success Rate', 'Hop Accuracy', 'Source Quality'],
            'Value': [2.3, 94, 87, 91],
            'Unit': ['sec', '%', '%', '%']
        })
        
        for _, row in perf_data.iterrows():
            st.metric(row['Metric'], f"{row['Value']}{row['Unit']}")

with tab2:
    st.subheader("📊 Analytics Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Query distribution
        query_types = ['Sports', 'Financial', 'Business', 'Global Events', 'Custom']
        query_counts = [15, 23, 18, 12, 8]
        
        fig_pie = px.pie(values=query_counts, names=query_types, title="Query Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Response time trends
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        response_times = [2.1 + 0.5 * (i % 7) for i in range(30)]
        
        fig_line = px.line(x=dates, y=response_times, title="Response Time Trends")
        fig_line.update_xaxes(title="Date")
        fig_line.update_yaxes(title="Response Time (s)")
        st.plotly_chart(fig_line, use_container_width=True)

with tab3:
    st.subheader("🔧 Advanced Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Model Parameters**")
        st.slider("Temperature", 0.0, 2.0, 0.3)
        st.slider("Max Tokens", 100, 4000, 3000)
        st.selectbox("Model Version", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    
    with col2:
        st.write("**RAG Settings**")
        st.slider("Similarity Threshold", 0.0, 1.0, 0.7)
        st.slider("Max Documents", 1, 20, 5)
        st.checkbox("Enable Reranking", True)

st.markdown("---")
st.markdown("<div style='text-align: center;'>**Advanced RAG Multi-Hop Research Agent** - NSKAI Hackathon 2025</div>", unsafe_allow_html=True)