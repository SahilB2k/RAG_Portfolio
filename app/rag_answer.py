"""
rag_answer.py - Multi-Provider RAG (Groq -> Gemini -> Ollama)
This implementation ensures 24/7 availability by falling back to cloud providers
when local Ollama is offline.
"""

import requests
import json
import os
import time
from app.query_resume import hybrid_search
from app.config import Config
from app.db import get_connection

def log_query(question: str, provider: str, confidence: str, user_ip: str = "unknown"):
    """Saves the user query metadata to Supabase for observability"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO query_logs (question, provider, confidence, user_ip) VALUES (%s, %s, %s, %s)",
            (question, provider, confidence, user_ip)
        )
        conn.commit()
        cur.close()
        conn.close()
        print(f"📝 [Log] Query recorded in Supabase (Provider: {provider})")
    except Exception as e:
        print(f"⚠️ [Log] Failed to log query: {e}")

def generate_with_groq(prompt):
    """Primary provider: Groq (Llama 3.2 70B or 3B)"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Missing Groq API Key")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.2-3b-preview", # or llama-3.1-70b-versatile
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 500,
        "stream": True
    }
    
    response = requests.post(url, headers=headers, json=payload, stream=True, timeout=30)
    response.raise_for_status()
    
    for line in response.iter_lines():
        if line:
            line_text = line.decode('utf-8')
            if line_text.startswith("data: "):
                data = line_text[6:]
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    content = chunk['choices'][0]['delta'].get('content', "")
                    if content:
                        yield content
                except:
                    continue

def generate_with_gemini(prompt):
    """Secondary provider: Google Gemini 1.5 Flash"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing Gemini API Key")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 500
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, stream=True, timeout=30)
    response.raise_for_status()
    
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line.decode('utf-8'))
            if 'candidates' in chunk and len(chunk['candidates']) > 0:
                text = chunk['candidates'][0]['content']['parts'][0]['text']
                yield text

def generate_with_ollama(prompt):
    """Local fallback / Development provider: Ollama"""
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    url = f"{ollama_url}/api/generate"
    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "stream": True,
        "options": {"num_ctx": 1024, "temperature": 0.2}
    }
    headers = {"ngrok-skip-browser-warning": "any"}
    
    response = requests.post(url, json=payload, headers=headers, stream=True, timeout=10)
    response.raise_for_status()
    
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line)
            yield chunk.get("response", "")
            if chunk.get("done"):
                break

def generate_answer_with_sources(question: str, user_ip: str = "unknown"):
    """
    RAG generator with multi-provider fallback strategy: Groq -> Gemini -> Ollama
    """
    print(f"\n🔍 [RAG] Processing Question: {question}")
    retrieved_chunks = hybrid_search(question, top_k=6)
    relevant_chunks = [c for c in retrieved_chunks if c[1] > 0.22]
    
    if not relevant_chunks:
        yield {"answer_chunk": "I couldn't find specific information in Sahil's resume to answer that precisely.", "metadata": None}
        return

    top_chunks = relevant_chunks[:5]
    context_text = "\n---\n".join([c[0] for c in top_chunks])
    
    # Sources metadata
    sources = []
    for content, score, search_type in top_chunks:
        section = content.split(":")[0] if ":" in content and len(content.split(":")[0]) < 50 else "Resume Section"
        sources.append({
            "section": section,
            "relevance": f"{int(score * 100)}%" if search_type == 'vector' else "100%",
            "preview": content[:120].strip() + "..."
        })

    avg_score = sum(c[1] for rc in top_chunks if rc[2] == 'vector') / len([rc for rc in top_chunks if rc[2] == 'vector']) if [rc for rc in top_chunks if rc[2] == 'vector'] else 0
    confidence = "high" if (any(rc[2] == 'keyword' for rc in top_chunks) or avg_score > 0.5) else "medium" if avg_score > 0.3 else "low"

    prompt = f"""You are Sahil's professional assistant. Answer briefly and professionally using the resume context below.
Resume Context:
{context_text}

Question: {question}
Answer (use **bold** for key terms, keep under 150 words):"""

    providers = [
        ("Groq", generate_with_groq),
        ("Gemini", generate_with_gemini),
        ("Ollama", generate_with_ollama)
    ]

    success = False
    for name, func in providers:
        print(f"🤖 [RAG] Attempting to generate with {name}...")
        try:
            for text_chunk in func(prompt):
                yield {"answer_chunk": text_chunk, "metadata": None}
            success = True
            # Log the successful query
            log_query(question, name, confidence, user_ip)
            break
        except Exception as e:
            print(f"⚠️ [RAG] {name} failed: {e}")
            continue

    if not success:
        yield {"answer_chunk": "❌ All AI providers are currently unavailable. Please try again later.", "metadata": None}
    else:
        yield {
            "answer_chunk": "", 
            "metadata": {
                "sources": sources,
                "confidence": confidence,
                "total_chunks": len(sources)
            }
        }
    print(f"✨ [RAG] Generation complete.")

def generate_answer(question: str) -> str:
    full_text = ""
    for chunk in generate_answer_with_sources(question):
        full_text += chunk.get("answer_chunk", "")
    return full_text