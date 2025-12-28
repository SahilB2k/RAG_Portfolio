"""
Optimized rag_answer.py - Faster Response on CPU
Key Optimizations:
1. Reverted to llama3.2 (3B) for accuracy
2. Reduced num_ctx to 1024 (faster evaluation)
3. Set num_predict to 150 (prevent over-generation)
4. Streamlined prompt
5. Reduced top_k to 6 for faster retrieval
"""

import requests
import json
import os
from app.query_resume import hybrid_search

def generate_answer_with_sources(question: str):
    """
    Optimized RAG generator: Streams the answer for low-latency hardware.
    Yields dicts with either 'answer_chunk' (text) or 'metadata' (sources/confidence).
    """
    # 1. OPTIMIZED: Reduced top_k from 7 to 6 for even faster retrieval
    print(f"\n🔍 [RAG] Received Question: {question}")
    retrieved_chunks = hybrid_search(question, top_k=6)
    
    # 2. Filter and prepare context
    relevant_chunks = [c for c in retrieved_chunks if c[1] > 0.22]
    print(f"✅ [RAG] Found {len(relevant_chunks)} relevant chunks")
    
    if not relevant_chunks:
        yield {
            "answer_chunk": "I couldn't find specific information in Sahil's resume to answer that precisely. Is there something else I can help you with?", 
            "metadata": None
        }
        return

    # Prepare context (limit to top 5 chunks for faster processing)
    top_chunks = relevant_chunks[:5]
    context_text = "\n---\n".join([c[0] for c in top_chunks])
    
    # Build sources metadata
    sources = []
    for content, score, search_type in top_chunks:
        section = "Resume Section"
        if ":" in content and len(content.split(":")[0]) < 50:
            section = content.split(":")[0]
        sources.append({
            "section": section,
            "relevance": f"{int(score * 100)}%" if search_type == 'vector' else "100%",
            "preview": content[:120].strip() + "..."
        })

    # Confidence calculation
    vector_chunks = [rc for rc in top_chunks if rc[2] == 'vector']
    avg_score = sum(c[1] for c in vector_chunks) / len(vector_chunks) if vector_chunks else 0
    has_keyword_match = any(rc[2] == 'keyword' for rc in top_chunks)
    confidence = "high" if (has_keyword_match or avg_score > 0.5) else "medium" if avg_score > 0.3 else "low"

    # 3. OPTIMIZED: Streamlined prompt and faster generation settings
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    prompt = f"""You are Sahil's professional assistant. Answer briefly and professionally using the resume context below.

Resume Context:
{context_text}

Question: {question}

Answer (use **bold** for key terms, keep under 150 words):"""

    print(f"🤖 [RAG] Streaming from Ollama ({ollama_url})...")
    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": "llama3.2",  # REVERTED to 3B for accuracy
                "prompt": prompt,
                "stream": True,
                "options": {
                    "num_ctx": 1024,      # REDUCED from 2048 (faster evaluation)
                    "num_predict": 150,   # LIMIT generation length
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            },
            headers={
                "Content-Type": "application/json",
                "ngrok-skip-browser-warning": "any"
            },
            stream=True,
            timeout=120
        )
        response.raise_for_status()
        
        full_answer = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                text_chunk = chunk.get("response", "")
                full_answer += text_chunk
                yield {"answer_chunk": text_chunk, "metadata": None}
                
                if chunk.get("done"):
                    break
        
        # Yield metadata at the end
        yield {
            "answer_chunk": "", 
            "metadata": {
                "sources": sources,
                "confidence": confidence,
                "total_chunks": len(sources)
            }
        }
        print(f"✨ [RAG] Stream complete ({len(full_answer)} chars)")
        
    except requests.exceptions.Timeout:
        print(f"⏱️ [RAG] Timeout - Consider reducing context further")
        yield {"answer_chunk": "Request timed out. Please try asking a more specific question.", "metadata": None}
    except Exception as e:
        print(f"❌ [RAG] Error: {e}")
        yield {"answer_chunk": f"An error occurred while generating the answer. Please try again.", "metadata": None}


def generate_answer(question: str) -> str:
    """
    Legacy wrapper (Non-streaming) - returns full answer as string
    """
    full_text = ""
    for chunk in generate_answer_with_sources(question):
        full_text += chunk.get("answer_chunk", "")
    return full_text


if __name__ == "__main__":
    print("Testing Optimized Streaming RAG...")
    print("-" * 60)
    
    test_questions = [
        "Tell me about Sahil's projects",
        "What is Sahil's CGPA?",
        "What technologies does Sahil know?"
    ]
    
    for question in test_questions:
        print(f"\nQ: {question}")
        print("A: ", end="", flush=True)
        for chunk in generate_answer_with_sources(question):
            if chunk.get("answer_chunk"):
                print(chunk["answer_chunk"], end="", flush=True)
            if chunk.get("metadata"):
                print(f"\n[Confidence: {chunk['metadata']['confidence']} | Sources: {chunk['metadata']['total_chunks']}]")
        print("\n" + "-" * 60)