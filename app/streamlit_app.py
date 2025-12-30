"""
Streamlit Web Interface for Resume RAG System
Enhanced Modern AI Copilot UI with Premium Dark Theme
"""

# =============================================================================
# ⚠️ STREAMLIT CONFIG MUST BE FIRST
# =============================================================================
import streamlit as st

st.set_page_config(
    page_title="Sahil Jadhav - AI Resume Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# IMPORTS
# =============================================================================
import sys
import time
from pathlib import Path

# Add PROJECT ROOT to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.rag_answer import generate_answer_with_sources

# =============================================================================
# 🔥 FORCE CACHE BUSTING (STREAMLIT CLOUD SAFE)
# =============================================================================
st.markdown(
    f"""
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <!-- UI_VERSION_{int(time.time())} -->
    """,
    unsafe_allow_html=True
)

st.caption("build: 30-dec-2025 | ui-v3 | streamlit-cloud")

# =============================================================================
# 🎨 GLOBAL CSS (SAFE + FUTURE PROOF)
# =============================================================================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #0a0e27, #1a1f3a, #0f1419);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Hide Streamlit Branding */
#MainMenu, footer, header { visibility: hidden; }

/* ================= HEADER ================= */
.main-header {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #60a5fa, #a78bfa, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
}

.sub-header {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 1rem;
}

.baby-notice {
    text-align: center;
    font-size: 0.8rem;
    color: #64748b;
    background: rgba(59,130,246,0.08);
    padding: 0.5rem;
    border-radius: 6px;
}

/* ================= CHAT ================= */
.stChatMessage {
    background: rgba(30,41,59,0.45) !important;
    border: 1px solid rgba(100,116,139,0.2);
    border-radius: 16px;
    padding: 1.2rem;
    backdrop-filter: blur(12px);
    margin-bottom: 1rem;
}

.stChatMessage.user {
    background: linear-gradient(
        135deg,
        rgba(59,130,246,0.12),
        rgba(99,102,241,0.12)
    ) !important;
    margin-left: 10%;
}

.stChatMessage.assistant {
    margin-right: 10%;
}

/* ================= SOURCES ================= */
.source-box {
    background: rgba(15,23,42,0.6);
    border-left: 4px solid #3b82f6;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.6rem 0;
}

.source-box strong { color: #60a5fa; }
.source-preview { color: #cbd5e1; font-size: 0.85rem; }

/* ================= CONFIDENCE ================= */
.confidence-container {
    display: flex;
    gap: 1rem;
    align-items: center;
    margin-top: 1rem;
}

.confidence-badge {
    padding: 0.4rem 1.2rem;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.75rem;
}

.confidence-high {
    color: #4ade80;
    border: 1px solid #4ade80;
}

.confidence-medium {
    color: #fbbf24;
    border: 1px solid #fbbf24;
}

.confidence-low {
    color: #f87171;
    border: 1px solid #f87171;
}

/* ================= SIDEBAR ================= */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e293b);
}

/* ================= BUTTONS ================= */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 600;
}

/* ================= EXPANDER ================= */
div[data-testid="stExpander"] summary {
    background: rgba(30,41,59,0.4);
    border-radius: 10px;
    padding: 0.7rem 1rem;
    border: 1px solid rgba(100,116,139,0.25);
    color: #94a3b8;
}

/* ================= FOOTER ================= */
.footer-stat {
    background: rgba(30,41,59,0.5);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    color: #94a3b8;
}

.footer-stat strong {
    color: #60a5fa;
}

</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE
# =============================================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "show_sources" not in st.session_state:
    st.session_state.show_sources = True

# =============================================================================
# HEADER
# =============================================================================
st.markdown('<div class="main-header">🤖 AI Resume Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Powered by RAG | Ask about Sahil Jadhav</div>', unsafe_allow_html=True)
st.markdown('<div class="baby-notice">⚡ First response may take a moment</div>', unsafe_allow_html=True)

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.header("⚙️ Settings")

    st.session_state.response_mode = st.selectbox(
        "Response Mode",
        ["Auto", "Casual", "Recruiter"]
    ).lower()

    st.session_state.show_sources = st.checkbox("Show Sources", True)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# =============================================================================
# CHAT UI
# =============================================================================
st.header("💬 Chat")

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask about Sahil's resume...")

if question:
    st.session_state.chat_history.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("assistant"):
        placeholder = st.empty()

        with st.spinner("Thinking..."):
            answer = ""
            metadata = {}

            for chunk in generate_answer_with_sources(question):
                answer += chunk.get("answer_chunk", "")
                metadata = chunk.get("metadata") or metadata
                placeholder.markdown(answer + "▌")

            placeholder.markdown(answer)

            confidence = metadata.get("confidence", "medium")

            st.markdown(
                f"""
                <div class="confidence-container">
                    <div class="confidence-badge confidence-{confidence}">
                        {confidence.upper()} CONFIDENCE
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.session_state.chat_history.append(
        {"role": "assistant", "content": answer}
    )

# =============================================================================
# FOOTER
# =============================================================================
st.divider()
cols = st.columns(3)

cols[0].markdown(
    '<div class="footer-stat"><strong>RAG</strong> Hybrid Search</div>',
    unsafe_allow_html=True
)
cols[1].markdown(
    '<div class="footer-stat"><strong>LLM</strong> Llama 3.2</div>',
    unsafe_allow_html=True
)
cols[2].markdown(
    '<div class="footer-stat"><strong>Embeddings</strong> BGE-Small</div>',
    unsafe_allow_html=True
)

# =============================================================================
# ABOUT SECTION
# =============================================================================
with st.expander("ℹ️ About This System"):
    st.markdown("""
    ### 🚀 How It Works

    This AI Resume Assistant uses **Retrieval-Augmented Generation (RAG)**:

    1. **Embedding Generation** – BGE-Small-v1.5
    2. **Hybrid Search** – Vector + BM25
    3. **Context Retrieval** – Relevant resume sections
    4. **Answer Generation** – Llama 3.2 via Ollama
    5. **Confidence Scoring** – Transparent reliability

    ### 🛠️ Tech Stack

    | Component | Technology |
    |---------|------------|
    | Vector DB | Supabase (pgvector) |
    | Embeddings | BGE-Small |
    | LLM | Llama 3.2 |
    | Frontend | Streamlit |
    | Search | Hybrid |
    """)

# =============================================================================
# LOCAL RUN INFO
# =============================================================================
if __name__ == "__main__":
    st.info()
