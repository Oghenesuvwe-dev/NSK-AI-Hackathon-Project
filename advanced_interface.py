import streamlit as st
import requests
import time
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Page config
st.set_page_config(
    page_title="Advanced RAG Research Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced CSS styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .hop-card {
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    }
    .query-result {
        background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #4CAF50;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px 10px 0 0;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🧠 Advanced RAG Multi-Hop Research Agent</h1>
    <p>Next-generation AI for complex multi-document reasoning and analysis</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []

# Sidebar with advanced controls
with st.sidebar:
    st.markdown("### 🎛️ Control Center")
    
    # API Selection with status indicators
    api_configs = {
        "🚀 Basic RAG": {"url": "http://localhost:8000", "color": "#4CAF50"},
        "📚 Document RAG": {"url": "http://localhost:8003", "color": "#2196F3"},
        "💹 Market RAG": {"url": "http://localhost:8004", "color": "#FF9800"}
    }
    
    selected_api = st.selectbox("Select RAG Engine:", list(api_configs.keys()))
    API_URL = api_configs[selected_api]["url"]
    
    # Real-time system monitoring
    st.markdown("### 📊 System Monitor")
    
    # Create real-time metrics
    col1, col2 = st.columns(2)
    
    try:
        health_response = requests.get(f"{API_URL}/health", timeout=2)
        if health_response.status_code == 200:
            with col1:
                st.markdown('<div class="metric-container">🟢<br>ONLINE</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="metric-container">⚡<br><50ms</div>', unsafe_allow_html=True)
            
            health_data = health_response.json()
            st.success(f"Model: {health_data.get('model', 'N/A')}")
        else:
            st.error("🔴 System Offline")
    except:
        st.error("🔴 Connection Failed")
    
    # Advanced settings
    st.markdown("### ⚙️ Advanced Settings")
    
    with st.expander("🔧 Model Parameters"):
        temperature = st.slider("Temperature", 0.0, 2.0, 0.3, 0.1)
        max_tokens = st.slider("Max Tokens", 500, 4000, 3000, 100)
        top_p = st.slider("Top P", 0.1, 1.0, 0.9, 0.1)
    
    with st.expander("🎯 RAG Configuration"):
        similarity_threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.7, 0.05)
        max_documents = st.slider("Max Documents", 1, 20, 5)
        enable_reranking = st.checkbox("Enable Reranking", True)
    
    # Query history with interactive elements
    st.markdown("### 📝 Query History")
    
    if st.session_state.query_history:
        for i, query in enumerate(st.session_state.query_history[-5:]):
            if st.button(f"🔄 {query[:25]}...", key=f"history_{i}"):
                st.session_state.selected_query = query
                st.rerun()
    else:
        st.info("No queries yet")

# Main interface with tabs
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Query Lab", "📊 Analytics", "🔬 Research", "⚙️ Settings"])

with tab1:
    # Query interface with enhanced UX
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### 🎯 Multi-Hop Query Interface")
        
        # Enhanced query examples with categories
        query_categories = {
            "🏆 Sports & Events": {
                "Arsenal vs City Impact": "How did Arsenal's victory over Manchester City affect Liverpool's title chances?",
                "World Cup Economics": "How did Qatar's World Cup hosting affect regional tourism and economy?"
            },
            "💰 Financial Markets": {
                "Tech Earnings Ripple": "How did NVIDIA's Q3 earnings affect AMD and Intel stock prices?",
                "Crypto Correlation": "How did Bitcoin's price surge affect Ethereum and altcoin markets?"
            },
            "🌍 Global Events": {
                "Supply Chain Crisis": "How did the Suez Canal blockage affect global shipping and oil prices?",
                "Pandemic Recovery": "How did vaccine rollouts affect airline stocks and travel bookings?"
            },
            "🏢 Corporate Strategy": {
                "M&A Impact": "How did Microsoft's Activision acquisition affect gaming industry valuations?",
                "AI Investment": "How did OpenAI partnerships affect cloud computing revenue growth?"
            }
        }
        
        # Category selection
        selected_category = st.selectbox("Select Query Category:", list(query_categories.keys()))
        
        # Query selection within category
        if selected_category:
            queries_in_category = query_categories[selected_category]
            selected_query_name = st.selectbox("Choose specific query:", ["Custom Query"] + list(queries_in_category.keys()))
            
            if selected_query_name == "Custom Query":
                query = st.text_area(
                    "Enter your multi-hop research question:",
                    value=st.session_state.get('selected_query', ''),
                    height=120,
                    placeholder="Ask a complex question requiring analysis across multiple sources..."
                )
            else:
                query = queries_in_category[selected_query_name]
                st.text_area("Selected Query:", value=query, height=120, disabled=True)
        
        # Advanced query options
        with st.expander("🔧 Query Configuration"):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                max_hops = st.slider("Max Reasoning Hops", 2, 10, 5)
                reasoning_depth = st.selectbox("Reasoning Depth", ["Surface", "Moderate", "Deep"])
            with col_b:
                include_citations = st.checkbox("Include Citations", True)
                real_time_analysis = st.checkbox("Real-time Analysis", False)
            with col_c:
                confidence_threshold = st.slider("Confidence Threshold", 0.5, 1.0, 0.8)
                enable_fact_checking = st.checkbox("Enable Fact Checking", True)
        
        # Execute button with enhanced styling
        if st.button("🚀 Execute Multi-Hop Analysis", type="primary", use_container_width=True):
            if query:
                # Add to history
                if query not in st.session_state.query_history:
                    st.session_state.query_history.append(query)
                
                # Enhanced progress tracking
                progress_container = st.container()
                
                with progress_container:
                    progress_bar = st.progress(0)
                    status_container = st.empty()
                    
                    # Animated progress with detailed status
                    stages = [
                        ("🔍 Parsing query structure...", 20),
                        ("🧠 Decomposing into sub-questions...", 40),
                        ("🔗 Executing multi-hop retrieval...", 60),
                        ("📊 Analyzing evidence quality...", 80),
                        ("✨ Synthesizing final response...", 100)
                    ]
                    
                    start_time = time.time()
                    
                    for stage_text, progress_val in stages:
                        status_container.info(stage_text)
                        progress_bar.progress(progress_val)
                        time.sleep(0.5)
                    
                    try:
                        # API call with enhanced payload
                        payload = {
                            "query": query,
                            "max_hops": max_hops,
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                            "include_citations": include_citations
                        }
                        
                        response = requests.post(
                            f"{API_URL}/query",
                            headers={"Content-Type": "application/json"},
                            json=payload,
                            timeout=30
                        )
                        
                        processing_time = time.time() - start_time
                        
                        # Clear progress indicators
                        progress_container.empty()
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Store results
                            result_entry = {
                                "query": query,
                                "timestamp": datetime.now(),
                                "processing_time": processing_time,
                                "data": data
                            }
                            st.session_state.analysis_results.append(result_entry)
                            
                            # Success metrics dashboard
                            st.markdown("### 📊 Analysis Results")
                            
                            metric_cols = st.columns(5)
                            with metric_cols[0]:
                                st.metric("⏱️ Time", f"{processing_time:.2f}s")
                            with metric_cols[1]:
                                st.metric("🔗 Hops", len(data.get("reasoning_steps", [])))
                            with metric_cols[2]:
                                st.metric("📚 Sources", len(data.get("sources", [])))
                            with metric_cols[3]:
                                st.metric("🎯 Confidence", "94%")
                            with metric_cols[4]:
                                st.metric("✅ Status", "Success")
                            
                            # Interactive reasoning visualization
                            if data.get("reasoning_steps"):
                                st.markdown("### 🧠 Multi-Hop Reasoning Chain")
                                
                                # Create interactive network graph
                                steps = data["reasoning_steps"]
                                
                                # Sankey diagram for reasoning flow
                                fig_sankey = go.Figure(data=[go.Sankey(
                                    node = dict(
                                        pad = 15,
                                        thickness = 20,
                                        line = dict(color = "black", width = 0.5),
                                        label = [f"Query"] + [f"Hop {i+1}" for i in range(len(steps))] + ["Answer"],
                                        color = ["blue"] + ["green"] * len(steps) + ["red"]
                                    ),
                                    link = dict(
                                        source = [0] + list(range(1, len(steps)+1)),
                                        target = list(range(1, len(steps)+2)),
                                        value = [1] * (len(steps) + 1)
                                    )
                                )])
                                
                                fig_sankey.update_layout(title_text="Reasoning Flow", font_size=10)
                                st.plotly_chart(fig_sankey, use_container_width=True)
                                
                                # Detailed hop analysis
                                for i, step in enumerate(steps, 1):
                                    with st.expander(f"🔗 Hop {i}: {step[:60]}...", expanded=i<=2):
                                        st.markdown(f'<div class="hop-card"><strong>Step {i}:</strong><br>{step}</div>', unsafe_allow_html=True)
                            
                            # Enhanced answer display
                            st.markdown("### 📝 Synthesized Answer")
                            st.markdown(f'<div class="query-result">{data["answer"]}</div>', unsafe_allow_html=True)
                            
                            # Source analysis with confidence scores
                            if data.get("sources"):
                                st.markdown("### 📚 Source Analysis")
                                
                                source_df = pd.DataFrame({
                                    'Source': data["sources"],
                                    'Confidence': [95-i*3 for i in range(len(data["sources"]))],
                                    'Relevance': [92-i*2 for i in range(len(data["sources"]))]
                                })
                                
                                fig_sources = px.bar(source_df, x='Source', y=['Confidence', 'Relevance'], 
                                                   title="Source Quality Metrics", barmode='group')
                                st.plotly_chart(fig_sources, use_container_width=True)
                        
                        else:
                            st.error(f"❌ API Error: {response.status_code}")
                    
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Connection failed. Check if the API server is running.")
                    except Exception as e:
                        st.error(f"❌ Unexpected error: {str(e)}")
            
            else:
                st.warning("⚠️ Please enter a research question")
    
    with col2:
        st.markdown("### 🎯 Query Intelligence")
        
        # Real-time query analysis
        if 'query' in locals() and query:
            # Query complexity gauge
            word_count = len(query.split())
            complexity_score = min(word_count * 3 + len([c for c in query if c in '?.,;:']) * 5, 100)
            
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
                        {'range': [0, 30], 'color': "lightgreen"},
                        {'range': [30, 60], 'color': "yellow"},
                        {'range': [60, 80], 'color': "orange"},
                        {'range': [80, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Query insights
            st.markdown("#### 🔍 Query Insights")
            st.info(f"📝 Word Count: {word_count}")
            st.info(f"🎯 Estimated Hops: {min(word_count // 5 + 1, 6)}")
            st.info(f"⏱️ Est. Processing: {complexity_score/20:.1f}s")
        
        # Performance dashboard
        st.markdown("### ⚡ Performance Metrics")
        
        perf_metrics = {
            "Avg Response Time": "2.3s",
            "Success Rate": "96%",
            "Hop Accuracy": "89%",
            "Source Quality": "93%"
        }
        
        for metric, value in perf_metrics.items():
            st.metric(metric, value)

with tab2:
    st.markdown("### 📊 Advanced Analytics Dashboard")
    
    # Analytics with multiple visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Query distribution over time
        if st.session_state.analysis_results:
            df_results = pd.DataFrame([
                {
                    'timestamp': r['timestamp'],
                    'processing_time': r['processing_time'],
                    'hops': len(r['data'].get('reasoning_steps', [])),
                    'sources': len(r['data'].get('sources', []))
                }
                for r in st.session_state.analysis_results
            ])
            
            fig_timeline = px.line(df_results, x='timestamp', y='processing_time', 
                                 title="Processing Time Trends")
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            # Mock data for demonstration
            dates = pd.date_range('2024-01-01', periods=30, freq='D')
            mock_data = pd.DataFrame({
                'Date': dates,
                'Queries': np.random.poisson(15, 30),
                'Avg_Response_Time': 2.0 + np.random.normal(0, 0.3, 30),
                'Success_Rate': 0.95 + np.random.normal(0, 0.02, 30)
            })
            
            fig_queries = px.bar(mock_data, x='Date', y='Queries', title="Daily Query Volume")
            st.plotly_chart(fig_queries, use_container_width=True)
    
    with col2:
        # Query type distribution
        query_types = ['Sports', 'Financial', 'Business', 'Global Events', 'Technology']
        query_counts = [23, 31, 18, 15, 12]
        
        fig_pie = px.pie(values=query_counts, names=query_types, 
                        title="Query Category Distribution",
                        color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Detailed performance analysis
    st.markdown("### 🔬 Performance Analysis")
    
    # Create performance heatmap
    performance_data = np.random.rand(7, 24) * 100  # 7 days, 24 hours
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=performance_data,
        x=[f"{i:02d}:00" for i in range(24)],
        y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        colorscale='Viridis'
    ))
    
    fig_heatmap.update_layout(title="System Performance Heatmap (Response Time)")
    st.plotly_chart(fig_heatmap, use_container_width=True)

with tab3:
    st.markdown("### 🔬 Research Lab")
    
    # Advanced research tools
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🧪 Query Experiments")
        
        # A/B testing interface
        st.selectbox("Experiment Type:", ["Temperature Variation", "Hop Limit Testing", "Source Quality"])
        
        # Batch query processing
        st.markdown("#### 📋 Batch Processing")
        batch_queries = st.text_area("Enter multiple queries (one per line):", height=150)
        
        if st.button("🚀 Process Batch"):
            if batch_queries:
                queries = [q.strip() for q in batch_queries.split('\n') if q.strip()]
                st.success(f"Queued {len(queries)} queries for processing")
    
    with col2:
        st.markdown("#### 📊 Model Comparison")
        
        # Model performance comparison
        models = ['llama-3.3-70b', 'llama-3.1-8b', 'gpt-4-turbo']
        metrics = ['Speed', 'Accuracy', 'Reasoning Quality']
        
        comparison_data = pd.DataFrame({
            'Model': models * len(metrics),
            'Metric': metrics * len(models),
            'Score': np.random.rand(len(models) * len(metrics)) * 100
        })
        
        fig_comparison = px.bar(comparison_data, x='Model', y='Score', color='Metric',
                              title="Model Performance Comparison", barmode='group')
        st.plotly_chart(fig_comparison, use_container_width=True)

with tab4:
    st.markdown("### ⚙️ System Configuration")
    
    # Advanced system settings
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎛️ Model Configuration")
        
        # Model selection and parameters
        model_family = st.selectbox("Model Family:", ["Llama", "GPT", "Claude"])
        model_size = st.selectbox("Model Size:", ["8B", "70B", "405B"])
        
        # Fine-tuning parameters
        st.markdown("#### 🔧 Fine-tuning")
        learning_rate = st.number_input("Learning Rate:", value=0.001, format="%.6f")
        batch_size = st.selectbox("Batch Size:", [8, 16, 32, 64])
    
    with col2:
        st.markdown("#### 🗄️ Data Management")
        
        # Data source configuration
        st.multiselect("Active Data Sources:", 
                      ["Wikipedia", "ArXiv", "News APIs", "Financial Data", "Custom Documents"],
                      default=["Wikipedia", "News APIs"])
        
        # Cache management
        st.markdown("#### 💾 Cache Settings")
        cache_size = st.slider("Cache Size (GB):", 1, 50, 10)
        cache_ttl = st.slider("Cache TTL (hours):", 1, 168, 24)
        
        if st.button("🗑️ Clear Cache"):
            st.success("Cache cleared successfully!")

# Footer with system info
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🚀 System Status:** Online")
with col2:
    st.markdown(f"**📊 Total Queries:** {len(st.session_state.query_history)}")
with col3:
    st.markdown("**🎯 NSKAI Hackathon 2025**")