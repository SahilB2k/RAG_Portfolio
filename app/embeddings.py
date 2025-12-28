import requests
import os
import json

def generate_embedding(text: str):
    """
    Cloud-based alternative to local sentence-transformers.
    Uses Google Gemini embedding model to save ~500MB of RAM.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "model": "models/text-embedding-004",
        "content": {
            "parts": [{"text": text}]
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result['embedding']['values']
    except Exception as e:
        print(f"❌ [Embeddings] Cloud embedding failed: {e}")
        # Return a zero-vector if everything fails to avoid crashing
        # (Assuming the vector dimension is 768 for text-embedding-004)
        return [0.0] * 768