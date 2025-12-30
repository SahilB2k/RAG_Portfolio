import streamlit as st
import sys
import time
import requests
from pathlib import Path

# =============================================================================
# ⚠️ STREAMLIT CONFIG (Must be first)
# =============================================================================
st.set_page_config(
    page_title="Sahil Jadhav - AI Resume Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add PROJECT ROOT to Python path to import your RAG logic
sys.path.append(str(Path(__file__).parent.parent))
from app.rag_answer import generate_answer_with_sources

# =============================================================================
# 🕵️ SECRET IDENTITY TRACKING
# =============================================================================
# Captures hidden tags like ?ref=Google from the URL
query_params = st.query_params
source_ref = query_params.get("ref", "Direct/Organic")

# =============================================================================
# 🎨 PREMIUM UI CSS
# =============================================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0e27, #1a1f3a, #0f1419);
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa, #a78bfa, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    
    .sub-header {
        text-align: center;
        color: #94a3b8;
        margin-bottom: 2rem;
    }

    /* Chat Styling */
    .stChatMessage {
        background: rgba(30, 41, 59, 0.45) !important;
        border: 1px solid rgba(100,116,139,0.2);
        border-radius: 16px;
        backdrop-filter: blur(12px);
    }

    /* Source Box Styling */
    .source-box {
        background: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .source-title { color: #60a5fa; font-weight: 700; }
    .source-text { color: #cbd5e1; font-size: 0.85rem; font-family: monospace; }

    /* Confidence Badges */
    .confidence-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }
    .confidence-high { color: #4ade80; border: 1px solid #4ade80; }
    .confidence-medium { color: #fbbf24; border: 1px solid #fbbf24; }
    
    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a, #1e293b);
    }

    /* Hide Default Elements */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 📥 RESUME DOWNLOAD LOGIC (LOW FRICTION)
# =============================================================================
@st.dialog("Access Resume")
def download_dialog():
    # Initialize a state to track if the form was submitted successfully
    if "download_unlocked" not in st.session_state:
        st.session_state.download_unlocked = False

    # STEP 1: If not unlocked, show the form
    if not st.session_state.download_unlocked:
        st.write("Please provide your email to unlock the download.")
        with st.form("quick_download"):
            email = st.text_input("Work Email (Optional)", placeholder="recruiter@company.com")
            submit = st.form_submit_button("Unlock PDF", use_container_width=True)
            
            if submit:
                # Log the lead to your backend
                try:
                    backend_api = "https://rag-portfolio-mvjo.onrender.com/log_download" 
                    requests.post(backend_api, json={
                        "email": email if email else f"Anonymous_{source_ref}",
                        "source_ref": source_ref
                    }, timeout=5)
                except:
                    pass
                
                # Unlock the download and rerun to refresh the dialog UI
                st.session_state.download_unlocked = True
                st.rerun()

    # STEP 2: If unlocked, hide the form and show the actual download button
    else:
        st.success("✅ Access Granted!")
        try:
            with open("assets/Sahil_Jadhav_Resume.pdf", "rb") as f:
                st.download_button(
                    label="📥 Click to Download PDF Now",
                    data=f,
                    file_name="Sahil_Jadhav_Resume.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        except FileNotFoundError:
            st.error("Resume file not found in /assets")
        
        # Option to go back/reset
        if st.button("Cancel / Reset", type="secondary"):
            st.session_state.download_unlocked = False
            st.rerun()

# =============================================================================
# ⚙️ SIDEBAR
# =============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.header("Settings")
    
    mode_selection = st.selectbox("Response Mode", ["Auto", "Casual", "Recruiter"])
    show_sources = st.checkbox("Show Sources", value=True)

    st.divider()
    st.subheader("📄 Documents")
    if st.button("📥 Download Resume", use_container_width=True):
        download_dialog()
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# =============================================================================
# 💬 CHAT INTERFACE
# =============================================================================
st.markdown('<div class="main-header">🤖 AI Resume Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Chat with Sahil\'s Profile via RAG</div>', unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
question = st.chat_input("Ask me about Sahil's experience...")

if question:
    st.session_state.chat_history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        final_metadata = None

        # Call RAG generator
        with st.spinner("Analyzing Resume..."):
            gen = generate_answer_with_sources(
                question=question, 
                user_ip="streamlit_user", 
                mode=mode_selection.lower()
            )

            for chunk in gen:
                if chunk.get("answer_chunk"):
                    full_response += chunk["answer_chunk"]
                    placeholder.markdown(full_response + "▌")
                if chunk.get("metadata"):
                    final_metadata = chunk["metadata"]

        placeholder.markdown(full_response)

        # Confidence & Sources
        if final_metadata:
            conf = final_metadata.get("confidence", "medium")
            st.markdown(f'<div class="confidence-badge confidence-{conf}">{conf.upper()} CONFIDENCE</div>', unsafe_allow_html=True)

            if show_sources and final_metadata.get("sources"):
                with st.expander("📚 View Sources", expanded=False):
                    for src in final_metadata["sources"]:
                        st.markdown(f"""
                            <div class="source-box">
                                <div class="source-title">{src.get('section', 'Resume Section')}</div>
                                <div class="source-text">{src.get('preview', '')}</div>
                            </div>
                        """, unsafe_allow_html=True)

    st.session_state.chat_history.append({"role": "assistant", "content": full_response})

# =============================================================================
# ℹ️ FOOTER INFO
# =============================================================================
st.divider()
f_cols = st.columns(3)
f_cols[0].caption("🔍 Hybrid Search: BM25 + Vector")
f_cols[1].caption("🧠 Model: Llama 3.2 (Ollama)")
f_cols[2].caption(f"📍 Tracking Active: {source_ref}")

if __name__ == "__main__":
    pass