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
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO query_logs (question, provider, confidence, user_ip) VALUES (%s, %s, %s, %s)",
            (question, provider, confidence, user_ip)
        )
        conn.commit()
        cur.close()
        print(f"📝 [Log] Query recorded in Supabase (Provider: {provider})")
    except Exception as e:
        print(f"⚠️ [Log] Failed to log query: {e}")
    finally:
        if conn:
            conn.close()

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
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 800, # Increased for detailed project descriptions
        "stream": True
    }
    
    response = requests.post(url, headers=headers, json=payload, stream=True, timeout=30)
    if response.status_code != 200:
        print(f"❌ [Groq] Error {response.status_code}: {response.text}")
    response.raise_for_status()
    
    for line in response.iter_lines():
        if line:
            # Robust SSE parsing
            line_text = line.decode('utf-8').strip()
            if line_text.startswith("data:"):
                data_str = line_text[5:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    content = chunk['choices'][0]['delta'].get('content', "")
                    if content:
                        yield content
                except json.JSONDecodeError:
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
            "maxOutputTokens": 800
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, stream=True, timeout=30)
    if response.status_code != 200:
        print(f"❌ [Gemini] Error {response.status_code}: {response.text}")
    response.raise_for_status()
    
    for line in response.iter_lines():
        if line:
            try:
                chunk = json.loads(line.decode('utf-8'))
                # Safety check: ensure candidates and content exist
                if chunk.get('candidates') and chunk['candidates'][0].get('content'):
                    parts = chunk['candidates'][0]['content'].get('parts', [])
                    if parts:
                        yield parts[0]['text']
            except (KeyError, IndexError, json.JSONDecodeError):
                continue

def generate_with_ollama(prompt):
    """Local fallback / Development provider: Ollama"""
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    url = f"{ollama_url}/api/generate"
    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "stream": True,
        "options": {"num_ctx": 2048, "temperature": 0.2} # Increased context window
    }
    headers = {"ngrok-skip-browser-warning": "any"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, stream=True, timeout=10)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                yield chunk.get("response", "")
                if chunk.get("done"):
                    break
    except Exception as e:
        print(f"❌ [Ollama] Connection failed: {e}")
        raise e

def is_greeting_or_casual(question: str) -> bool:
    """
    Detect if the query is strictly a greeting. 
    If it contains substantive keywords (resume, project, skills), return False.
    """
    cleaned_q = question.lower().strip()
    
    # If the user asks about specific topics, it is NOT just a greeting
    substantive_keywords = ["resume", "project", "work", "job", "skill", "experience", "education", "hired", "contact", "detail"]
    if any(kw in cleaned_q for kw in substantive_keywords):
        return False
        
    casual_patterns = [
        "hello", "hi", "hey", "greetings", "good morning", "good evening", 
        "how are you", "what's up", "yo", "thanks", "thank you", "bye"
    ]
    
    # Exact match or very short greeting
    if cleaned_q in casual_patterns:
        return True
    
    # If it's a short sentence starting with a greeting but no substantive keywords
    if len(cleaned_q.split()) < 4 and any(cleaned_q.startswith(p) for p in casual_patterns):
        return True
        
    return False

def generate_answer_with_sources(question: str, user_ip: str = "unknown", mode: str = "auto"):
    """
    RAG generator with multi-provider fallback strategy.
    """
    print(f"\n🔍 [RAG] Processing Question: {question} (Mode: {mode})")
    
    # 1. Handle Greetings
    if is_greeting_or_casual(question):
        yield {"answer_chunk": "Hello! I am Sahil's AI assistant. I can answer detailed questions about his projects, experience, and skills. What would you like to know?", "metadata": None}
        return

    # 2. Determine Style
    recruiter_keywords = ["experience", "skills", "resume", "projects", "hire", "role", "internship", "work", "education", "tech stack"]
    
    if mode == "auto":
        detected_mode = "recruiter" if any(kw in question.lower() for kw in recruiter_keywords) else "casual"
    else:
        detected_mode = mode.lower()

    # 3. Retrieve Context
    # Increased top_k to ensure we capture multiple projects if asked
    retrieved_chunks = hybrid_search(question, top_k=7) 
    
    # Lowered threshold slightly to avoid missing context on specific queries
    relevant_chunks = [c for c in retrieved_chunks if c[1] > 0.12] 
    
    if not relevant_chunks:
        yield {"answer_chunk": "I checked Sahil's resume, but I couldn't find specific details regarding that. However, I can tell you about his main projects and technical skills. Would you like to hear about those?", "metadata": None}
        return

    top_chunks = relevant_chunks[:6]
    context_text = "\n---\n".join([c[0] for c in top_chunks])
    
    # Build Metadata
    sources = []
    for content, score, search_type in top_chunks:
        section = content.split(":")[0] if ":" in content and len(content.split(":")[0]) < 50 else "Resume Detail"
        sources.append({
            "section": section,
            "relevance": f"{int(score * 100)}%" if search_type == 'vector' else "100%",
            "preview": content[:100].strip() + "..."
        })

    avg_score = sum(rc[1] for rc in top_chunks if rc[2] == 'vector') / len([rc for rc in top_chunks if rc[2] == 'vector']) if [rc for rc in top_chunks if rc[2] == 'vector'] else 0
    confidence = "high" if avg_score > 0.45 else "medium"

    # 4. Construct System Prompt (FIXED FOR PROFESSIONALISM)
    if detected_mode == "recruiter":
        tone_instruction = (
            "You are a professional hiring assistant. Answer with high information density. "
            "Use bullet points for projects and metrics. "
            "Do NOT use filler words. Focus on technologies, outcomes, and specific contributions."
        )
    else:
        tone_instruction = (
            "You are a helpful and professional assistant. Answer naturally but stay focused on Sahil's professional achievements. "
            "Use clear, easy-to-read formatting."
        )

    prompt = f"""You are an AI assistant answering questions about Sahil based ONLY on his resume.

CONTEXT FROM RESUME:
{context_text}

USER QUESTION:
{question}

CRITICAL RULES:
1. **Direct Answer:** You must extract the answer from the context.
2. **Never Deflect:** NEVER say "You can check the resume" or "It is detailed in the resume." YOU are the resume reader.
3. **Completeness:** If the user asks about projects, list the specific projects found in the context, including the tech stack used for each.
4. **Honesty:** If the specific detail isn't there, say "The resume doesn't mention that specific detail, but..." and pivot to what IS known.
5. {tone_instruction}

Start your answer immediately:"""

    # 5. Call Providers
    providers = [
        ("Groq", generate_with_groq),
        ("Gemini", generate_with_gemini),
        ("Ollama", generate_with_ollama)
    ]

    success = False
    for name, func in providers:
        print(f"🤖 [RAG] Attempting generation with {name}...")
        try:
            for text_chunk in func(prompt):
                yield {"answer_chunk": text_chunk, "metadata": None}
            
            success = True
            log_query(question, name, confidence, user_ip)
            break
        except Exception as e:
            print(f"⚠️ [RAG] {name} failed: {e}")
            continue

    if not success:
        yield {"answer_chunk": "❌ Service is currently experiencing high load. Please try asking again in a moment.", "metadata": None}
    else:
        yield {
            "answer_chunk": "", 
            "metadata": {
                "sources": sources,
                "confidence": confidence,
                "mode": detected_mode
            }
        }
    print(f"✨ [RAG] Generation complete.")

def generate_answer(question: str) -> str:
    full_text = ""
    for chunk in generate_answer_with_sources(question):
        full_text += chunk.get("answer_chunk", "")
    return full_text