# Sahil Jadhav: AI-Powered Digital Twin (RAG) 🤖💼

**A production-grade Retrieval-Augmented Generation (RAG) system acting as a professional "Digital Twin."**

---

## 🌟 Overview

This project is a high-performance **RAG** application designed to represent me professionally. It uses a hybrid search architecture to provide 100% accurate, source-cited information from my resume, ensuring recruiters and interviewers get the data they need instantly via **Web** and **Mobile**.

### 🎥 Key Features
*   **Hybrid Search**: Combines semantic vector search (BGE-Small) with keyword matching for zero-miss retrieval.
*   **Contextual Chunking**: Breaks down resume sections into atomic, context-enriched pieces.
*   **Real-time Streaming**: Chat responses stream token-by-token for a "ChatGPT-like" experience.
*   **Cross-Platform**: Modern **Streamlit Web Dashboard** + **Expo Mobile App**.

---

## 🛠️ Tech Stack

*   **LLM Engine:** Llama 3.2 (via Ollama)
*   **Vector Database:** Supabase (pgvector)
*   **Backend API:** Flask (Production-hardened with Gunicorn & Gevent)
*   **Frontend:** Streamlit (Web) & Expo/React Native (Mobile)
*   **Infrastucture:** Docker & Docker Compose

---

## 🚀 Quick Start (Development)

### 1. Prerequisites
*   [Ollama](https://ollama.ai/) installed and running (`ollama pull llama3.2`)
*   Python 3.10+
*   Node.js & npm (for Mobile)

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/resume-rag.git
cd resume-rag

# Install Python dependencies
pip install -r requirements.txt

# Start the Flask Backend
python -m app.api
```

### 3. Mobile App (Expo)
```bash
cd mobile
npm install
npx expo start --tunnel
```
*Note: Run `python update_tunnel.py` in the root folder whenever your ngrok URL changes.*

---

## 🏗️ Production Deployment (Docker)

To run the entire stack in a productionalized environment:

```bash
docker-compose up --build -d
```

| Service | Endpoint |
| :--- | :--- |
| **Backend API** | `http://localhost:5000` |
| **Streamlit UI** | `http://localhost:8501` |
| **Health Check** | `http://localhost:5000/health` |

---

## 📁 Project Structure

```bash
resume_rag/
├── app/                  # 🧠 Backend & RAG Logic
│   ├── api.py            # Flask API (Streaming capable)
│   ├── config.py         # Centralized environment config
│   ├── rag_answer.py     # Prompt engineering & LLM bridge
│   └── streamlit_app.py  # Web Interface
├── mobile/               # 📱 Expo Mobile App
│   ├── app/(tabs)/       # Chat UI Screens
│   └── services/api.ts   # Mobile-to-Backend service
├── data/                 # 📄 Source Artifacts (resume.md)
├── Dockerfile            # Production API image
├── Dockerfile.ui         # Production Streamlit image
└── update_tunnel.py      # Automated DX tool for mobile tunnels
```

---

## 📝 Configuration
Create a `.env` file in the root:
```env
DATABASE_URL=your_supabase_postgresql_url
APP_ENV=dev
CORS_ORIGINS=*
```

---

## 🙌 Author
**Sahil Jadhav**  
*AI/ML Engineer*
