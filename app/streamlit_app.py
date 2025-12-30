import streamlit as st
import sys
import time
from pathlib import Path

# =============================================================================
# ⚠️ STREAMLIT CONFIG
# =============================================================================
st.set_page_config(
    page_title="Sahil Jadhav - AI Resume Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add PROJECT ROOT to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.rag_answer import generate_answer_with_sources

# =============================================================================
# 🎨 GLOBAL CSS
# =============================================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0a0e27, #1a1f3a, #0f1419);
    font-family: 'Inter', sans-serif;
}
/* ... (Your existing CSS remains here, it was excellent) ... */

/* ADDED: Source Box Styling */
.source-box {
    background: rgba(30, 41, 59, 0.5);
    border-left: 3px solid #3b82f6;
    padding: 0.8rem;
    margin-top: 0.5rem;
    border-radius: 4px;
    font-size: 0.85rem;
}
.source-title {
    color: #60a5fa;
    font-weight: bold;
    margin-bottom: 0.2rem;
    display: block;
}
.source-text {
    color: #cbd5e1;
    font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE
# =============================================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Store selection in session state
    mode_selection = st.selectbox(
        "Response Mode",
        ["Auto", "Casual", "Recruiter"],
        index=0
    )
    
    show_sources = st.checkbox("Show Sources", value=True)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# =============================================================================
# MAIN CHAT
# =============================================================================
st.markdown('<div class="main-header">🤖 AI Resume Assistant</div>', unsafe_allow_html=True)
st.caption("Powered by RAG | Ask about Sahil Jadhav")

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # If this message has sources saved, display them (Optional feature)

question = st.chat_input("Ask about Sahil's resume...")

if question:
    st.session_state.chat_history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        final_metadata = None

        # 1. Pass the MODE to the backend function
        # 2. Pass a dummy IP or real request IP if available
        gen = generate_answer_with_sources(
            question=question, 
            user_ip="streamlit_user", 
            mode=mode_selection # <--- FIXED: Now passes "Recruiter"/"Casual"
        )

        for chunk in gen:
            # Accumulate text
            if chunk.get("answer_chunk"):
                full_response += chunk["answer_chunk"]
                placeholder.markdown(full_response + "▌")
            
            # Capture metadata when it arrives (usually in the last chunk)
            if chunk.get("metadata"):
                final_metadata = chunk["metadata"]

        # Final render without cursor
        placeholder.markdown(full_response)

        # =====================================================================
        # 🔌 WIRING FIX: Display Sources & Confidence
        # =====================================================================
        if final_metadata:
            confidence = final_metadata.get("confidence", "medium")
            
            # Display Confidence Badge
            st.markdown(f"""
                <div class="confidence-container">
                    <div class="confidence-badge confidence-{confidence}">
                        {confidence.upper()} CONFIDENCE
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Display Sources if toggle is ON
            if show_sources and final_metadata.get("sources"):
                with st.expander("📚 View Resume Sources", expanded=False):
                    for idx, source in enumerate(final_metadata["sources"]):
                        st.markdown(f"""
                        <div class="source-box">
                            <span class="source-title">{source.get('section', 'Section')} ({source.get('relevance', 'N/A')})</span>
                            <span class="source-text">{source.get('preview', '')}</span>
                        </div>
                        """, unsafe_allow_html=True)

    # Save complete interaction to history
    st.session_state.chat_history.append({"role": "assistant", "content": full_response})

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
    st.info("App is running")
