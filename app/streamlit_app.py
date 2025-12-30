"""
Streamlit Web Interface for Resume RAG System
Enhanced Modern AI Copilot UI with Premium Dark Theme
"""

import streamlit as st
import sys
from pathlib import Path

# Add PROJECT ROOT to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.rag_answer import generate_answer_with_sources


# Page configuration
st.set_page_config(
    page_title="Sahil Jadhav - AI Resume Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# UI IMPROVEMENT: Enhanced CSS with better visual hierarchy and glassmorphism
# ============================================================================
st.markdown("""
<style>
    /* ===== GLOBAL IMPROVEMENTS ===== */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ===== HEADER SECTION - Cleaner, more prominent ===== */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.3rem;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }
    
    .sub-header {
        font-size: 1rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 400;
        letter-spacing: 0.01em;
    }
    
    .baby-notice {
        text-align: center;
        color: #64748b;
        font-style: italic;
        font-size: 0.8rem;
        margin-bottom: 2rem;
        padding: 0.5rem;
        background: rgba(59, 130, 246, 0.05);
        border-radius: 6px;
        border: 1px solid rgba(59, 130, 246, 0.1);
    }
    
    /* ===== CHAT MESSAGES - ChatGPT-style bubbles ===== */
    .stChatMessage {
        background: rgba(30, 41, 59, 0.4) !important;
        border: 1px solid rgba(100, 116, 139, 0.15);
        border-radius: 16px !important;
        padding: 1.25rem 1.5rem !important;
        margin-bottom: 1rem;
        backdrop-filter: blur(12px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
    }
    
    .stChatMessage:hover {
        border-color: rgba(100, 116, 139, 0.25);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* User messages - distinct blue tint */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(99, 102, 241, 0.08) 100%) !important;
        border: 1px solid rgba(59, 130, 246, 0.25);
        margin-left: 10%;
    }
    
    /* Assistant messages - slightly different positioning */
    .stChatMessage[data-testid="assistant-message"] {
        margin-right: 10%;
    }
    
    /* ===== SOURCE CARDS - Improved hierarchy ===== */
    .source-box {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.6) 100%);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-left: 3px solid #3b82f6;
        padding: 1rem 1.25rem;
        margin: 0.6rem 0;
        border-radius: 10px;
        backdrop-filter: blur(8px);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .source-box:hover {
        border-left-width: 5px;
        border-color: rgba(59, 130, 246, 0.4);
        transform: translateX(6px);
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.15);
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%);
    }
    
    .source-box strong {
        color: #60a5fa;
        font-size: 0.9rem;
        font-weight: 600;
        display: block;
        margin-bottom: 0.4rem;
    }
    
    .source-relevance {
        color: #a78bfa;
        font-size: 0.8rem;
        font-weight: 500;
        display: block;
        margin-bottom: 0.4rem;
    }
    
    .source-preview {
        color: #cbd5e1;
        font-size: 0.85rem;
        line-height: 1.5;
        font-style: italic;
        opacity: 0.9;
    }
    
    /* ===== CONFIDENCE BADGES - Enhanced visual prominence ===== */
    .confidence-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-top: 1rem;
        padding: 0.75rem;
        background: rgba(15, 23, 42, 0.4);
        border-radius: 10px;
        border: 1px solid rgba(100, 116, 139, 0.1);
    }
    
    .confidence-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1.25rem;
        border-radius: 24px;
        font-weight: 700;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .confidence-high {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(34, 197, 94, 0.1) 100%);
        color: #4ade80;
        border: 1.5px solid rgba(34, 197, 94, 0.4);
    }
    
    .confidence-medium {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.2) 0%, rgba(251, 191, 36, 0.1) 100%);
        color: #fbbf24;
        border: 1.5px solid rgba(251, 191, 36, 0.4);
    }
    
    .confidence-low {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.1) 100%);
        color: #f87171;
        border: 1.5px solid rgba(239, 68, 68, 0.4);
    }
    
    .source-count-text {
        color: #64748b;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* ===== SIDEBAR - Cleaner grouping and spacing ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.98) 100%);
        border-right: 1px solid rgba(100, 116, 139, 0.15);
        backdrop-filter: blur(20px);
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f1f5f9;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    /* Sidebar section dividers */
    [data-testid="stSidebar"] hr {
        margin: 1.5rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(100, 116, 139, 0.3), transparent);
    }
    
    /* ===== BUTTONS - Enhanced with better visual feedback ===== */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
        letter-spacing: 0.02em;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.35);
        transform: translateY(-2px);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    }
    
    /* Sample question buttons in sidebar */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(59, 130, 246, 0.08);
        color: #93c5fd;
        border: 1px solid rgba(59, 130, 246, 0.25);
        font-size: 0.8rem;
        padding: 0.6rem 1rem;
        text-align: left;
        font-weight: 500;
        box-shadow: none;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.4);
        color: #bfdbfe;
        transform: translateX(4px);
    }
    
    /* ===== CHAT INPUT - Modern floating style ===== */
    .stChatInput {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(12px);
    }
    
    .stChatInput:focus-within {
        border-color: rgba(59, 130, 246, 0.5) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* ===== EXPANDERS - Cleaner, more subtle ===== */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.3);
        border: 1px solid rgba(100, 116, 139, 0.2);
        border-radius: 10px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.75rem 1rem;
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(30, 41, 59, 0.5);
        border-color: rgba(100, 116, 139, 0.3);
        color: #cbd5e1;
    }
    
    /* ===== METRICS - Enhanced visual appeal ===== */
    [data-testid="stMetricValue"] {
        color: #60a5fa;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* ===== ALERTS - Better integration ===== */
    .stAlert {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(100, 116, 139, 0.25);
        border-radius: 10px;
        backdrop-filter: blur(10px);
        padding: 1rem;
    }
    
    /* ===== FOOTER STATS - Card-style layout ===== */
    .footer-stat {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.5) 100%);
        border: 1px solid rgba(100, 116, 139, 0.2);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        text-align: center;
        color: #94a3b8;
        font-size: 0.85rem;
        backdrop-filter: blur(8px);
        transition: all 0.2s ease;
    }
    
    .footer-stat:hover {
        border-color: rgba(100, 116, 139, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .footer-stat strong {
        color: #60a5fa;
        display: block;
        margin-bottom: 0.4rem;
        font-size: 0.95rem;
        font-weight: 700;
    }
    
    /* ===== SPINNER - Branded color ===== */
    .stSpinner > div {
        border-top-color: #3b82f6 !important;
    }
    
    /* ===== FORM ELEMENTS - Consistent styling ===== */
    .stRadio > label,
    .stSelectbox > label,
    .stCheckbox > label {
        color: #94a3b8;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    .stRadio [role="radiogroup"] {
        gap: 0.5rem;
    }
    
    .stRadio [role="radio"] {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    
    .stRadio [role="radio"]:hover {
        background: rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.4);
    }
    
    /* ===== SECTION HEADERS - Better hierarchy ===== */
    h1, h2, h3 {
        color: #f1f5f9;
        font-weight: 700;
    }
    
    h2 {
        font-size: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(59, 130, 246, 0.2);
    }
    
    /* ===== SCROLLBAR - Subtle custom styling ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(100, 116, 139, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(100, 116, 139, 0.7);
    }
    
    /* ===== LINK BUTTONS - Special styling ===== */
    .stLinkButton > a {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        text-decoration: none;
        padding: 0.7rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        display: inline-block;
        transition: all 0.25s ease;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    .stLinkButton > a:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'show_sources' not in st.session_state:
    st.session_state.show_sources = True

# ============================================================================
# UI IMPROVEMENT: Cleaner header with better spacing
# ============================================================================
st.markdown('<div class="main-header">🤖 AI Resume Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Powered by RAG | Ask me anything about Sahil Jadhav\'s experience, skills & projects</div>', unsafe_allow_html=True)
st.markdown('<div class="baby-notice">⚡ My brain is warming up... Responses may take a moment! 👶</div>', unsafe_allow_html=True)

# ============================================================================
# UI IMPROVEMENT: Better organized sidebar with clear sections
# ============================================================================
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Configuration section
    search_mode = st.radio(
        "Search Mode",
        ["Hybrid (Recommended)", "Vector Only"],
        help="Hybrid combines semantic and keyword search for better accuracy"
    )
    
    response_mode = st.selectbox(
        "Response Mode",
        ["Auto", "Casual", "Recruiter"],
        help="Auto: Smart mode switching | Casual: Friendly tone | Recruiter: Professional format"
    )
    st.session_state.response_mode = response_mode.lower()

    show_sources = st.checkbox(
        "Show Sources",
        value=True,
        help="Display which resume sections were used"
    )
    st.session_state.show_sources = show_sources
    
    show_debug = st.checkbox(
        "Debug Mode",
        value=False,
        help="Show technical retrieval details"
    )
    
    st.divider()
    
    # Sample questions section
    st.header("💡 Quick Questions")
    sample_questions = [
        "What are Sahil's key projects?",
        "Tell me about his academic background",
        "What technical skills does he have?",
        "Describe the Image Forgery project",
        "List his certifications",
        "What programming languages does he know?"
    ]
    
    for question in sample_questions:
        if st.button(question, key=f"sample_{question}", use_container_width=True):
            st.session_state.current_question = question
    
    st.divider()
    
    # Resume access control section
    st.header("🛡️ Resume Access")
    
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'access_status' not in st.session_state:
        st.session_state.access_status = None

    if st.session_state.access_token is None:
        email_inp = st.text_input("Professional Email:", placeholder="recruiter@company.com", key="resume_email_input")
        if st.button("Request Access", use_container_width=True):
            if email_inp and "@" in email_inp:
                try:
                    import uuid
                    import hashlib
                    import threading
                    from datetime import datetime, timedelta
                    from app.db import get_connection
                    from app.email_service import send_gate_notification
                    
                    user_ip = "streamlit_user"
                    hashed_ip = hashlib.sha256(user_ip.encode()).hexdigest()
                    
                    conn = get_connection()
                    cur = conn.cursor()
                    
                    # Rate limiting check
                    one_hour_ago = datetime.now() - timedelta(hours=1)
                    cur.execute(
                        "SELECT count(*) FROM resume_requests WHERE hashed_ip = %s AND created_at > %s",
                        (hashed_ip, one_hour_ago)
                    )
                    request_count = cur.fetchone()[0]
                    
                    if request_count >= 3:
                        st.error("Rate limit exceeded. Please wait an hour.")
                        cur.close()
                        conn.close()
                    else:
                        token = str(uuid.uuid4())
                        expires_at = datetime.now() + timedelta(hours=24)
                        
                        cur.execute(
                            """INSERT INTO resume_requests (email, token, status, expires_at, hashed_ip) 
                               VALUES (%s, %s, 'pending', %s, %s)""",
                            (email_inp, token, expires_at, hashed_ip)
                        )
                        conn.commit()
                        cur.close()
                        conn.close()
                        
                        # Notify admin
                        thread = threading.Thread(target=send_gate_notification, args=(email_inp, token))
                        thread.start()
                        
                        st.session_state.access_token = token
                        st.session_state.access_status = 'pending'
                        st.rerun()
                except Exception as e:
                    st.error(f"System error: {e}")
            else:
                st.error("Valid email required!")
    
    else:
        # Access status polling
        try:
            from app.db import get_connection
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT status FROM resume_requests WHERE token = %s", (st.session_state.access_token,))
            res = cur.fetchone()
            cur.close()
            conn.close()
            
            status = res[0] if res else 'not_found'
            
            if status == 'pending':
                st.info("⏳ Request pending approval")
                with st.spinner("Processing..."):
                    st.caption("_This helps prevent misuse and ensures quality engagement._")
                if st.button("Refresh Status", use_container_width=True):
                    st.rerun()
            
            elif status == 'approved':
                st.success("✅ Access Granted!")
                base_url = "https://rag-portfolio-mvjo.onrender.com"
                download_url = f"{base_url}/download_resume?token={st.session_state.access_token}"
                st.link_button("📥 Download Resume", download_url, use_container_width=True)
                if st.button("New Request", use_container_width=True):
                    st.session_state.access_token = None
                    st.rerun()
            
            else:
                st.warning(f"Status: {status}")
                if st.button("Try Again", use_container_width=True):
                    st.session_state.access_token = None
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Status check failed: {e}")
            if st.button("Reset", use_container_width=True):
                st.session_state.access_token = None
                st.rerun()
    
    st.divider()
    
    # System status section
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
        st.success("✅ All Systems Online")
    except Exception as e:
        st.error("❌ Database Offline")
        if show_debug:
            st.error(f"Error: {e}")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# ============================================================================
# MAIN CHAT INTERFACE - Enhanced message display
# ============================================================================
st.header("💬 Chat")

# Display chat history with improved rendering
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # ===== UI IMPROVEMENT: Better source card rendering =====
        if message["role"] == "assistant" and "sources" in message and st.session_state.show_sources:
            with st.expander("📚 View Sources", expanded=False):
                sources_html = ""
                for idx, source in enumerate(message["sources"], 1):
                    sources_html += f"""
                    <div class="source-box">
                        <strong>Source {idx}: {source['section']}</strong>
                        <span class="source-relevance">Relevance: {source['relevance']}</span>
                        <span class="source-preview">{source['preview']}</span>
                    </div>
                    """
                st.markdown(sources_html, unsafe_allow_html=True)

# Chat input
question = st.chat_input("Ask me anything about Sahil's resume...")

# Handle sample question button clicks
if 'current_question' in st.session_state:
    question = st.session_state.current_question
    del st.session_state.current_question

# ============================================================================
# PROCESS QUESTION - No logic changes, only UI improvements
# ============================================================================
if question:
    # Add user message to chat
    st.session_state.chat_history.append({"role": "user", "content": question})
    
    with st.chat_message("user"):
        st.markdown(question)
    
    with st.chat_message("assistant"):
        with st.spinner("🤔 Processing your question..."):
            # Create placeholder for streaming
            answer_placeholder = st.empty()
            full_answer = ""
            metadata = None
            
            try:
                stream_gen = generate_answer_with_sources(
                    question, 
                    user_ip="streamlit-frontend",
                    mode=st.session_state.get('response_mode', 'auto')
                )
                
                # Process stream
                for result in stream_gen:
                    chunk = result.get("answer_chunk", "")
                    full_answer += chunk
                    answer_placeholder.markdown(full_answer + "▌")
                    
                    if result.get("metadata"):
                        metadata = result["metadata"]
                
                # Final render without cursor
                answer_placeholder.markdown(full_answer)
                
                # ===== UI IMPROVEMENT: Enhanced confidence and source display =====
                if metadata:
                    confidence = metadata['confidence']
                    
                    # Confidence container with better visual hierarchy
                    st.markdown(f"""
                    <div class="confidence-container">
                        <div class="confidence-badge confidence-{confidence}">
                            {confidence.upper()} Confidence
                        </div>
                        <span class="source-count-text">
                            {metadata['total_chunks']} sources analyzed
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.session_state.show_sources and metadata['sources']:
                        with st.expander("📚 View Sources", expanded=False):
                            sources_html = ""
                            for idx, source in enumerate(metadata['sources'], 1):
                                sources_html += f"""
                                <div class="source-box">
                                    <strong>Source {idx}: {source['section']}</strong>
                                    <span class="source-relevance">Relevance: {source['relevance']}</span>
                                    <span class="source-preview">{source['preview']}</span>
                                </div>
                                """
                            st.markdown(sources_html, unsafe_allow_html=True)
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": full_answer,
                        "sources": metadata['sources'],
                        "confidence": confidence
                    })

                if show_debug and metadata:
                    with st.expander("🔧 Debug Info"):
                        st.json(metadata)
                        
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.chat_history.append({"role": "assistant", "content": f"Error: {str(e)}"})

# ============================================================================
# FOOTER - Enhanced card-style stats
# ============================================================================
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="footer-stat">
        <strong>💡 Pro Tip</strong>
        Ask specific questions for precise answers
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

# ============================================================================
# ABOUT SECTION - Enhanced information architecture
# ============================================================================
with st.expander("ℹ️ About This System"):
    st.markdown("""
    ### 🚀 How It Works
    
    This AI Resume Assistant uses **Retrieval-Augmented Generation (RAG)** for intelligent Q&A:
    
    **Architecture:**
    1. **Embedding Generation** - BGE-Small-v1.5 converts your query to semantic vectors
    2. **Hybrid Search** - Combines semantic similarity + keyword matching (BM25)
    3. **Context Retrieval** - Fetches most relevant resume sections
    4. **Answer Generation** - Llama 3.2 via Ollama API synthesizes comprehensive responses
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
    - ✅ High-impact retrieval
    - ✅ Source transparency with preview
    - ✅ Confidence scoring (high/medium/low)
    - ✅ Hybrid search (never misses keywords)
    - ✅ Modern, premium dark theme UI
    """)

# Run instructions
if __name__ == "__main__":
    st.info("💡 **Running locally?** Start with: `streamlit run app/streamlit_app.py`")