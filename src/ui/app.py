import streamlit as st
import requests
import json
from datetime import datetime

# Configuration
API_URL = "http://127.0.0.1:8000"

# Page config
st.set_page_config(
    page_title="RAG Chat Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .doc-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .score-badge {
        display: inline-block;
        background-color: #1f77b4;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.9rem;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🤖 RAG Chat Interface</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Check API health
    try:
        health_response = requests.get(f"{API_URL}/health", timeout=2)
        if health_response.status_code == 200:
            health_data = health_response.json()
            st.success("✅ API Connected")
            st.metric("Documents Indexed", health_data["documents_indexed"])
            st.metric("Model", health_data["embedding_model"])
        else:
            st.error("❌ API Error")
    except requests.exceptions.RequestException:
        st.error("❌ Cannot connect to API")
        st.info("Make sure to run: `uvicorn src.api.main:app --reload`")
    
    # Settings
    top_k = st.slider("Number of results", 1, 10, 5)
    
    st.divider()
    
    # Upload section
    st.subheader("📤 Upload Document")
    uploaded_file = st.file_uploader("Choose a text file", type=["txt", "md"])
    
    if uploaded_file is not None:
        if st.button("Upload & Index"):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post(f"{API_URL}/upload", files=files, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ Uploaded '{uploaded_file.name}'")
                    st.info(f"Created {result['chunks_created']} chunks")
                else:
                    st.error(f"Upload failed: {response.text}")
            except Exception as e:
                st.error(f"Error uploading: {e}")
    
    st.divider()
    
    # Stats
    st.subheader("📊 Statistics")
    try:
        stats_response = requests.get(f"{API_URL}/stats", timeout=2)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Chunks", stats["total_chunks"])
            with col2:
                st.metric("Embedding Dim", stats["embedding_dimension"])
    except:
        pass

# Main content
st.subheader("💬 Ask Questions")

# Chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "metadata" in message:
            with st.expander("📚 Retrieved Documents"):
                for i, doc in enumerate(message["metadata"]["documents"], 1):
                    st.markdown(f"""
                    <div class="doc-box">
                        <span class="score-badge">Score: {doc['score']:.2f}</span>
                        <strong>Source:</strong> {doc['source']}<br>
                        <strong>Text:</strong> {doc['text'][:200]}...
                    </div>
                    """, unsafe_allow_html=True)

# Input
query = st.chat_input("Ask a question about your documents...")

if query:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": query
    })
    
    with st.chat_message("user"):
        st.markdown(query)
    
    # Get response from API
    with st.spinner("🔍 Searching and generating response..."):
        try:
            response = requests.post(
                f"{API_URL}/query",
                json={
                    "query": query,
                    "top_k": top_k
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Format answer
                answer = result.get("answer", "No relevant documents found.")
                processing_time = result.get("processing_time", 0)
                
                # Add assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "metadata": {
                        "documents": result.get("retrieved_documents", []),
                        "time": processing_time
                    }
                })
                
                # Display response
                with st.chat_message("assistant"):
                    st.markdown(answer)
                    st.caption(f"⏱️ Response time: {processing_time:.2f}s")
                    
                    # Show retrieved documents
                    if result.get("retrieved_documents"):
                        with st.expander("📚 Retrieved Documents"):
                            for i, doc in enumerate(result["retrieved_documents"], 1):
                                st.markdown(f"""
                                <div class="doc-box">
                                    <span class="score-badge">Score: {doc['score']:.2f}</span>
                                    <strong>Source:</strong> {doc['source']}<br>
                                    <strong>Text:</strong> {doc['text'][:200]}...
                                </div>
                                """, unsafe_allow_html=True)
            else:
                st.error(f"Error: {response.text}")
        
        except requests.exceptions.RequestException as e:
            st.error(f"Cannot connect to API. Make sure the server is running!")
            st.code("uvicorn src.api.main:app --reload", language="bash")
        except Exception as e:
            st.error(f"Error: {e}")

# Footer
st.divider()
st.markdown("""
---
**RAG Chat System** | Built with FastAPI + Streamlit  
*Retrieve documents using semantic search and BM25, then generate answers*
""")