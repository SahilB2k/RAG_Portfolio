# """
# Streamlit Web Interface for Resume RAG System
# Professional, interview-ready UI with source transparency
# """

# import streamlit as st
# import sys
# from pathlib import Path

# # Add PROJECT ROOT to Python path
# sys.path.append(str(Path(__file__).parent.parent))

# from app.rag_answer import generate_answer
# from app.query_resume import query_resume, hybrid_search


# # Page configuration
# st.set_page_config(
#     page_title="Sahil Jadhav - AI Resume Assistant",
#     page_icon="🤖",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS for professional appearance
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 2.5rem;
#         font-weight: bold;
#         color: #1f77b4;
#         text-align: center;
#         margin-bottom: 0.5rem;
#     }
#     .sub-header {
#         font-size: 1.2rem;
#         color: #666;
#         text-align: center;
#         margin-bottom: 2rem;
#     }
#     .source-box {
#         background-color: #f0f2f6;
#         border-left: 4px solid #1f77b4;
#         padding: 1rem;
#         margin: 0.5rem 0;
#         border-radius: 0.3rem;
#     }
#     .confidence-high {
#         color: #28a745;
#         font-weight: bold;
#     }
#     .confidence-medium {
#         color: #ffc107;
#         font-weight: bold;
#     }
#     .confidence-low {
#         color: #dc3545;
#         font-weight: bold;
#     }
# </style>
# """, unsafe_allow_html=True)

# # Initialize session state
# if 'chat_history' not in st.session_state:
#     st.session_state.chat_history = []
# if 'show_sources' not in st.session_state:
#     st.session_state.show_sources = True

# # Header
# st.markdown('<div class="main-header">🤖 Sahil Jadhav - AI Resume Assistant</div>', unsafe_allow_html=True)
# st.markdown('<div class="sub-header">Ask me anything about my background, skills, projects, and experience</div>', unsafe_allow_html=True)

# # Sidebar
# with st.sidebar:
#     st.header("⚙️ Settings")
    
#     search_mode = st.radio(
#         "Search Mode",
#         ["Hybrid (Recommended)", "Vector Only"],
#         help="Hybrid combines semantic and keyword search for better accuracy"
#     )
    
#     show_sources = st.checkbox(
#         "Show Sources",
#         value=True,
#         help="Display which resume sections were used to generate the answer"
#     )
#     st.session_state.show_sources = show_sources
    
#     show_debug = st.checkbox(
#         "Show Debug Info",
#         value=False,
#         help="Display technical details about retrieval process"
#     )
    
#     st.divider()
    
#     st.header("📋 Sample Questions")
#     sample_questions = [
#         "What are all of Sahil's projects?",
#         "What was Sahil's academic performance?",
#         "What technical skills does Sahil have?",
#         "Tell me about the Image Forgery Detection project",
#         "What certifications does Sahil have?",
#         "What programming languages does Sahil know?"
#     ]
    
#     for question in sample_questions:
#         if st.button(question, key=f"sample_{question}", use_container_width=True):
#             st.session_state.current_question = question
    
#     st.divider()
    
#     # Stats
#     st.header("📊 System Stats")
#     try:
#         from app.db import get_connection
#         conn = get_connection()
#         cur = conn.cursor()
#         cur.execute("SELECT COUNT(*) FROM resume_chunks;")
#         chunk_count = cur.fetchone()[0]
#         cur.close()
#         conn.close()
        
#         st.metric("Resume Chunks", chunk_count)
#         st.info("System Status: ✅ Online")
#     except Exception as e:
#         st.error("System Status: ❌ Database Error")
#         if show_debug:
#             st.error(f"Error: {e}")
    
#     # Clear chat button
#     if st.button("🗑️ Clear Chat History", use_container_width=True):
#         st.session_state.chat_history = []
#         st.rerun()

# # Main chat interface
# st.header("💬 Chat Interface")

# # Display chat history
# for message in st.session_state.chat_history:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])
        
#         # Show sources if available
#         if message["role"] == "assistant" and "sources" in message and st.session_state.show_sources:
#             with st.expander("📚 View Sources"):
#                 for idx, source in enumerate(message["sources"], 1):
#                     st.markdown(f"""
#                     <div class="source-box">
#                         <strong>Source {idx}: {source['section']}</strong><br>
#                         Relevance: {source['relevance']}<br>
#                         <em>{source['preview']}</em>
#                     </div>
#                     """, unsafe_allow_html=True)

# # Chat input
# question = st.chat_input("Ask me anything about Sahil's resume...")

# # Handle sample question button clicks
# if 'current_question' in st.session_state:
#     question = st.session_state.current_question
#     del st.session_state.current_question

# # Process question
# if question:
#     # Add user message to chat
#     st.session_state.chat_history.append({
#         "role": "user",
#         "content": question
#     })
    
#     # Display user message
#     with st.chat_message("user"):
#         st.markdown(question)
    
#     # Generate answer with loading indicator
#     with st.chat_message("assistant"):
#         with st.spinner("🤔 Analyzing resume..."):
#             try:
#                 use_hybrid = (search_mode == "Hybrid (Recommended)")
                
#                 # Generate answer with sources
#                 result = generate_answer_with_sources(question)
                
#                 # Display answer
#                 st.markdown(result['answer'])
                
#                 # Display confidence badge
#                 confidence = result['confidence']
#                 confidence_class = f"confidence-{confidence}"
#                 st.markdown(f"""
#                 <div style="margin-top: 1rem;">
#                     <span class="{confidence_class}">Confidence: {confidence.upper()}</span>
#                     <span style="color: #666; margin-left: 1rem;">
#                         ({result['total_chunks']} sources analyzed)
#                     </span>
#                 </div>
#                 """, unsafe_allow_html=True)
                
#                 # Add to chat history with sources
#                 st.session_state.chat_history.append({
#                     "role": "assistant",
#                     "content": result['answer'],
#                     "sources": result['sources'],
#                     "confidence": confidence
#                 })
                
#                 # Show sources immediately if enabled
#                 if st.session_state.show_sources and result['sources']:
#                     with st.expander("📚 View Sources", expanded=False):
#                         for idx, source in enumerate(result['sources'], 1):
#                             st.markdown(f"""
#                             <div class="source-box">
#                                 <strong>Source {idx}: {source['section']}</strong><br>
#                                 Relevance: {source['relevance']}<br>
#                                 <em>{source['preview']}</em>
#                             </div>
#                             """, unsafe_allow_html=True)
                
#                 # Debug info
#                 if show_debug:
#                     with st.expander("🔧 Debug Information"):
#                         st.json({
#                             "search_mode": search_mode,
#                             "chunks_retrieved": result['total_chunks'],
#                             "confidence": confidence,
#                             "sources_used": len(result['sources'])
#                         })
                
#             except Exception as e:
#                 error_msg = f"❌ Error generating answer: {str(e)}"
#                 st.error(error_msg)
                
#                 st.session_state.chat_history.append({
#                     "role": "assistant",
#                     "content": error_msg
#                 })
                
#                 if show_debug:
#                     st.exception(e)

# # Footer
# st.divider()
# col1, col2, col3 = st.columns(3)

# with col1:
#     st.markdown("**💡 Tip:** Use specific questions for best results")

# with col2:
#     st.markdown("**🔍 Hybrid Search:** Enabled for comprehensive answers")

# with col3:
#     st.markdown("**📊 Model:** BGE-Small-v1.5 + Llama 3.2")

# # About section
# with st.expander("ℹ️ About This System"):
#     st.markdown("""
#     ### How It Works
    
#     This AI Resume Assistant uses **Retrieval-Augmented Generation (RAG)** to answer questions about Sahil Jadhav's resume:
    
#     1. **Embedding Generation**: Your question is converted to a vector using BGE-Small-v1.5
#     2. **Hybrid Search**: Combines semantic search (meaning) + keyword search (exact terms)
#     3. **Context Building**: Retrieves 15+ relevant resume sections
#     4. **Answer Generation**: Llama 3.2 analyzes all sections and provides a comprehensive answer
#     5. **Source Attribution**: Shows which resume sections were used
    
#     ### Technical Stack
#     - **Vector Database**: Supabase (pgvector)
#     - **Embedding Model**: BGE-Small-v1.5 (SOTA semantic search)
#     - **LLM**: Llama 3.2 via Ollama
#     - **Frontend**: Streamlit
#     - **Search**: Hybrid (Vector + Keyword BM25)
    
#     ### Features
#     - ✅ Comprehensive retrieval (15 chunks per query)
#     - ✅ Source transparency (shows where info came from)
#     - ✅ Confidence scoring (high/medium/low)
#     - ✅ Hybrid search (never misses specific terms)
#     - ✅ Chat history (conversational interface)
#     """)

# # Run instructions
# if __name__ == "__main__":
#     st.info("💡 **Running locally?** Start with: `streamlit run app/streamlit_app.py`")


"""
Streamlit Web Interface for Resume RAG System
Modern, AI-focused UI with sophisticated dark theme
"""

import streamlit as st
import sys
from pathlib import Path

# Add PROJECT ROOT to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.rag_answer import generate_answer
from app.query_resume import query_resume, hybrid_search
from app.rag_answer import generate_answer_with_sources


# Page configuration
st.set_page_config(
    page_title="Sahil Jadhav - AI Resume Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, sophisticated dark theme
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main Header - Premium dark theme */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }
    
    /* Chat Messages */
    .stChatMessage {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(100, 116, 139, 0.2);
        border-radius: 12px;
        padding: 1.5rem !important;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: rgba(59, 130, 246, 0.1) !important;
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    /* Source Box - Modern card style */
    .source-box {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-left: 4px solid #3b82f6;
        padding: 1.25rem;
        margin: 0.75rem 0;
        border-radius: 8px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .source-box:hover {
        border-color: rgba(59, 130, 246, 0.6);
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    }
    
    .source-box strong {
        color: #60a5fa;
        font-size: 0.95rem;
        font-weight: 600;
    }
    
    /* Confidence Badges */
    .confidence-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin-top: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .confidence-high {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .confidence-medium {
        background: rgba(251, 191, 36, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.3);
    }
    
    .confidence-low {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
        border-right: 1px solid rgba(100, 116, 139, 0.2);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #f1f5f9;
    }
    
    /* Buttons - Modern gradient style */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
    }
    
    /* Sample Questions Buttons */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(59, 130, 246, 0.1);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        font-size: 0.85rem;
        padding: 0.65rem 1rem;
        text-align: left;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(59, 130, 246, 0.2);
        border-color: rgba(59, 130, 246, 0.5);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #60a5fa;
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Info/Success/Error boxes */
    .stAlert {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(100, 116, 139, 0.3);
        border-radius: 8px;
        backdrop-filter: blur(10px);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(100, 116, 139, 0.2);
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
    }
    
    /* Chat Input */
    .stChatInput {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
    }
    
    /* Footer Stats */
    .footer-stat {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(100, 116, 139, 0.2);
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
    }
    
    .footer-stat strong {
        color: #60a5fa;
        display: block;
        margin-bottom: 0.25rem;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #3b82f6 !important;
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: #94a3b8;
    }
    
    /* Divider */
    hr {
        border-color: rgba(100, 116, 139, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'show_sources' not in st.session_state:
    st.session_state.show_sources = True

# Header
st.markdown('<div class="main-header">🤖 AI Resume Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Powered by RAG | Ask me anything about Sahil Jadhav\'s experience, skills & projects</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    search_mode = st.radio(
        "Search Mode",
        ["Hybrid (Recommended)", "Vector Only"],
        help="Hybrid combines semantic and keyword search for better accuracy"
    )
    
    show_sources = st.checkbox(
        "Show Sources",
        value=True,
        help="Display which resume sections were used to generate the answer"
    )
    st.session_state.show_sources = show_sources
    
    show_debug = st.checkbox(
        "Debug Mode",
        value=False,
        help="Display technical details about retrieval process"
    )
    
    st.divider()
    
    st.header("💡 Sample Questions")
    sample_questions = [
        "What are all of Sahil's projects?",
        "What was Sahil's academic performance?",
        "What technical skills does Sahil have?",
        "Tell me about the Image Forgery Detection project",
        "What certifications does Sahil have?",
        "What programming languages does Sahil know?"
    ]
    
    for question in sample_questions:
        if st.button(question, key=f"sample_{question}", use_container_width=True):
            st.session_state.current_question = question
    
    st.divider()
    
    # Stats
    st.header("📊 System Status")
    try:
        from app.db import get_connection
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM resume_chunks;")
        chunk_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        st.metric("Resume Chunks", chunk_count)
        st.success("✅ System Online")
    except Exception as e:
        st.error("❌ Database Error")
        if show_debug:
            st.error(f"Error: {e}")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# Main chat interface
st.header("💬 Conversation")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show sources if available
        if message["role"] == "assistant" and "sources" in message and st.session_state.show_sources:
            with st.expander("📚 View Sources", expanded=False):
                for idx, source in enumerate(message["sources"], 1):
                    st.markdown(f"""
                    <div class="source-box">
                        <strong>Source {idx}: {source['section']}</strong><br>
                        <span style="color: #94a3b8;">Relevance: {source['relevance']}</span><br>
                        <em style="color: #cbd5e1;">{source['preview']}</em>
                    </div>
                    """, unsafe_allow_html=True)

# Chat input
question = st.chat_input("Ask me anything about Sahil's resume...")

# Handle sample question button clicks
if 'current_question' in st.session_state:
    question = st.session_state.current_question
    del st.session_state.current_question

# Process question
if question:
    # Add user message to chat
    st.session_state.chat_history.append({
        "role": "user",
        "content": question
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(question)
    
    # Generate answer with loading indicator
    with st.chat_message("assistant"):
        with st.spinner("🤔 Analyzing resume data..."):
            try:
                use_hybrid = (search_mode == "Hybrid (Recommended)")
                
                # Generate answer with sources
                result = generate_answer_with_sources(question)
                
                # Display answer
                st.markdown(result['answer'])
                
                # Display confidence badge
                confidence = result['confidence']
                confidence_class = f"confidence-{confidence}"
                st.markdown(f"""
                <div class="confidence-badge {confidence_class}">
                    {confidence.upper()} CONFIDENCE
                </div>
                <span style="color: #64748b; margin-left: 1rem; font-size: 0.85rem;">
                    {result['total_chunks']} sources analyzed
                </span>
                """, unsafe_allow_html=True)
                
                # Add to chat history with sources
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": result['answer'],
                    "sources": result['sources'],
                    "confidence": confidence
                })
                
                # Show sources immediately if enabled
                if st.session_state.show_sources and result['sources']:
                    with st.expander("📚 View Sources", expanded=False):
                        for idx, source in enumerate(result['sources'], 1):
                            st.markdown(f"""
                            <div class="source-box">
                                <strong>Source {idx}: {source['section']}</strong><br>
                                <span style="color: #94a3b8;">Relevance: {source['relevance']}</span><br>
                                <em style="color: #cbd5e1;">{source['preview']}</em>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Debug info
                if show_debug:
                    with st.expander("🔧 Debug Information"):
                        st.json({
                            "search_mode": search_mode,
                            "chunks_retrieved": result['total_chunks'],
                            "confidence": confidence,
                            "sources_used": len(result['sources'])
                        })
                
            except Exception as e:
                error_msg = f"❌ Error generating answer: {str(e)}"
                st.error(error_msg)
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg
                })
                
                if show_debug:
                    st.exception(e)

# Footer
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="footer-stat">
        <strong>💡 Pro Tip</strong>
        Use specific questions for precise answers
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="footer-stat">
        <strong>🔍 Search Mode</strong>
        Hybrid (Semantic + Keyword)
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="footer-stat">
        <strong>🤖 AI Stack</strong>
        BGE-Small + Llama 3.2
    </div>
    """, unsafe_allow_html=True)

# About section
with st.expander("ℹ️ About This System"):
    st.markdown("""
    ### 🚀 How It Works
    
    This AI Resume Assistant uses **Retrieval-Augmented Generation (RAG)** for intelligent Q&A:
    
    **Architecture:**
    1. **Embedding Generation** - BGE-Small-v1.5 converts your query to semantic vectors
    2. **Hybrid Search** - Combines semantic similarity + keyword matching (BM25)
    3. **Context Retrieval** - Fetches 15+ most relevant resume sections
    4. **Answer Generation** - Llama 3.2 synthesizes comprehensive responses
    5. **Source Attribution** - Full transparency on information sources
    
    ### 🛠️ Technical Stack
    
    | Component | Technology |
    |-----------|-----------|
    | **Vector DB** | Supabase (pgvector) |
    | **Embeddings** | BGE-Small-v1.5 |
    | **LLM** | Llama 3.2 (Ollama) |
    | **Frontend** | Streamlit |
    | **Search** | Hybrid (Vector + BM25) |
    
    ### ✨ Key Features
    - ✅ Comprehensive retrieval (15 chunks per query)
    - ✅ Source transparency with preview
    - ✅ Confidence scoring (high/medium/low)
    - ✅ Hybrid search (never misses keywords)
    - ✅ Chat history & context
    - ✅ Real-time status monitoring
    """)

# Helper function placeholder
def generate_answer_with_sources(question):
    """
    Placeholder for the actual RAG function.
    Replace this with your actual implementation that returns:
    {
        'answer': str,
        'confidence': str,  # 'high', 'medium', or 'low'
        'total_chunks': int,
        'sources': [{'section': str, 'relevance': str, 'preview': str}]
    }
    """
    # This should call your actual RAG pipeline
    # For now, returning a dummy structure
    return {
        'answer': 'This is where your RAG answer would appear.',
        'confidence': 'high',
        'total_chunks': 15,
        'sources': [
            {
                'section': 'Skills Section',
                'relevance': '95%',
                'preview': 'Python, Machine Learning, NLP...'
            }
        ]
    }

# Run instructions
if __name__ == "__main__":
    st.info("💡 **Running locally?** Start with: `streamlit run app/streamlit_app.py`")
