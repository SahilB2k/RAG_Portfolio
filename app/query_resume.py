"""
Enhanced query_resume.py - Production-Ready Retrieval
Key Improvements:
1. Balanced top_k (12) for focused but comprehensive context
2. Tuned similarity threshold (0.25) to reduce noise
3. Robust keyword extraction and matching
4. Scoring-aware result merging
"""

from app.db import get_connection
from app.embeddings import generate_embedding
import re

def query_resume(question, top_k=12, min_similarity=0.25):
    """
    Retrieval function focused on high-quality semantic matches
    """
    conn = get_connection()
    cur = conn.cursor()

    # Generate embedding using BGE model
    query_embedding = generate_embedding(question)

    try:
        # Retrieve chunks with similarity scores
        cur.execute("""
            SELECT id, content, (1 - (embedding <=> %s::vector)) as similarity 
            FROM resume_chunks
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """, (query_embedding, query_embedding, top_k))

        results = cur.fetchall()
        
        # Filter by minimum similarity threshold
        filtered_results = [
            (res[1], res[2], res[0])  # (content, similarity, id)
            for res in results 
            if res[2] > min_similarity
        ]
        
        return filtered_results
        
    except Exception as e:
        print(f"❌ Error during query: {e}")
        return []
    finally:
        cur.close()
        conn.close()


def hybrid_search(question, top_k=12):
    """
    Combines vector search with keyword matching
    Ensures specific terms (CGPA, project names) are prioritized
    """
    # Step 1: Vector search (semantic understanding)
    vector_results = query_resume(question, top_k=top_k)
    
    # Step 2: Keyword search (exact term matching)
    keywords = extract_keywords(question)
    keyword_results = []
    
    if keywords:
        conn = get_connection()
        cur = conn.cursor()
        try:
            # Search for chunks containing any of the extracted keywords
            # We use ILIKE for robustness
            for keyword in keywords:
                cur.execute("""
                    SELECT content 
                    FROM resume_chunks 
                    WHERE content ILIKE %s
                    LIMIT 3;
                """, (f"%{keyword}%",))
                
                keyword_matches = cur.fetchall()
                keyword_results.extend([
                    (res[0], 1.0, 'keyword') for res in keyword_matches
                ])
        except Exception as e:
            print(f"⚠️ Keyword search error: {e}")
        finally:
            cur.close()
            conn.close()
    
    # Step 3: Merge and deduplicate
    merged_results = merge_results(vector_results, keyword_results)
    
    return merged_results[:top_k]


def extract_keywords(question):
    """
    Extract meaningful keywords, ignoring common filler words
    """
    # Remove common stopwords and focus on nouns/technical terms
    stopwords = {
        'what', 'is', 'the', 'tell', 'me', 'about', 'your', 'my', 
        'a', 'an', 'are', 'how', 'which', 'where', 'when', 'can', 'you',
        'of', 'for', 'with', 'and', 'was', 'were', 'had', 'has', 'have'
    }
    
    # Extract potential keywords (3+ chars)
    words = re.findall(r'[\w\.]+', question.lower())
    keywords = [
        word for word in words 
        if word not in stopwords and len(word) > 2
    ]
    
    # Add project-specific or grade-specific multi-word patterns if any
    # e.g., "image forgery", "cgpa"
    return list(set(keywords))


def merge_results(vector_results, keyword_results):
    """
    Merge results, prioritizing exact keyword matches while keeping semantic order
    """
    seen_content = {} # hash(content) -> score
    merged = []
    
    # 1. Process keyword results first (high priority)
    for content, score, search_type in keyword_results:
        content_hash = hash(content.strip())
        if content_hash not in seen_content:
            seen_content[content_hash] = score
            merged.append((content, score, 'keyword'))
    
    # 2. Add vector results
    for content, score, chunk_id in vector_results:
        content_hash = hash(content.strip())
        if content_hash not in seen_content:
            seen_content[content_hash] = score
            merged.append((content, score, 'vector'))
        else:
            # If already added via keyword, we keep it as a keyword match but maybe log it?
            pass
            
    # Sort by score (keywords already have 1.0)
    merged.sort(key=lambda x: x[1], reverse=True)
    
    return merged


if __name__ == "__main__":
    print("Testing Hybrid Retrieval...")
    q = "What is Sahil's academic performance?"
    results = hybrid_search(q)
    for i, (content, score, type) in enumerate(results):
        print(f"{i+1}. [{type}] {content[:100]}...")
