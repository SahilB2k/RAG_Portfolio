"""
Enhanced query_resume.py - Production-Ready Retrieval
Key Improvements:
1. Increased top_k to 15 for comprehensive coverage
2. Lowered similarity threshold to 0.20
3. Added hybrid search (vector + keyword)
4. Added section-specific retrieval
5. Added result metadata for citations
"""

from app.db import get_connection
from app.embeddings import generate_embedding

def query_resume(question, top_k=15, min_similarity=0.20):
    """
    Main retrieval function with aggressive coverage
    
    Args:
        question: User's query
        top_k: Number of chunks to retrieve (15 ensures broad coverage)
        min_similarity: Minimum similarity threshold (0.20 for comprehensive results)
    
    Returns:
        List of tuples: [(content, similarity_score, chunk_id), ...]
    """
    conn = get_connection()
    cur = conn.cursor()

    # Generate embedding using BGE model
    query_embedding = generate_embedding(question)

    try:
        # Retrieve chunks with similarity scores
        cur.execute("""
            SELECT id, content, similarity 
            FROM match_resume_chunks(%s::vector, %s::int);
        """, (query_embedding, top_k))

        results = cur.fetchall()
        
        # DEBUG: Show what BGE found
        print(f"\n--- RETRIEVAL DEBUG ---")
        print(f"Query: {question}")
        print(f"BGE Search found {len(results)} chunks")
        
        for i, res in enumerate(results):
            chunk_id, content, score = res
            print(f"  Rank {i+1} | ID: {chunk_id} | Score: {score:.4f}")
            print(f"  Preview: {content[:80]}...")
        
        # Filter by minimum similarity threshold
        filtered_results = [
            (res[1], res[2], res[0])  # (content, similarity, id)
            for res in results 
            if res[2] > min_similarity
        ]
        
        print(f"After filtering (threshold={min_similarity}): {len(filtered_results)} chunks")
        print("--- END DEBUG ---\n")
        
        return filtered_results
        
    except Exception as e:
        print(f"❌ Error during query: {e}")
        return []
    finally:
        cur.close()
        conn.close()


def query_by_section(section_name, top_k=10):
    """
    Retrieve all chunks from a specific section
    Useful for questions like "tell me about all your projects"
    
    Args:
        section_name: Section header (e.g., "Projects", "Education", "Technical Skills")
        top_k: Maximum chunks to retrieve
    
    Returns:
        List of tuples: [(content, section_name), ...]
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Search for chunks that start with the section header
        cur.execute("""
            SELECT content 
            FROM resume_chunks 
            WHERE content ILIKE %s
            ORDER BY id
            LIMIT %s;
        """, (f"{section_name}%", top_k))
        
        results = cur.fetchall()
        
        print(f"\n--- SECTION RETRIEVAL ---")
        print(f"Section: {section_name}")
        print(f"Found {len(results)} chunks")
        print("--- END DEBUG ---\n")
        
        return [(res[0], section_name) for res in results]
        
    except Exception as e:
        print(f"❌ Error retrieving section: {e}")
        return []
    finally:
        cur.close()
        conn.close()


def hybrid_search(question, top_k=15):
    """
    Combines vector search with keyword matching
    Ensures specific terms are never missed (e.g., "10th percentage", "CGPA")
    
    Args:
        question: User's query
        top_k: Number of chunks to retrieve
    
    Returns:
        List of tuples: [(content, score, search_type), ...]
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # Step 1: Vector search (semantic understanding)
    vector_results = query_resume(question, top_k=top_k, min_similarity=0.20)
    
    # Step 2: Keyword search (exact term matching)
    keywords = extract_keywords(question)
    keyword_results = []
    
    try:
        for keyword in keywords:
            cur.execute("""
                SELECT content 
                FROM resume_chunks 
                WHERE content ILIKE %s
                LIMIT %s;
            """, (f"%{keyword}%", 5))
            
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
    
    print(f"\n--- HYBRID SEARCH DEBUG ---")
    print(f"Vector results: {len(vector_results)}")
    print(f"Keyword results: {len(keyword_results)}")
    print(f"Merged results: {len(merged_results)}")
    print("--- END DEBUG ---\n")
    
    return merged_results[:top_k]


def extract_keywords(question):
    """
    Extract important keywords from the question
    Focuses on technical terms, grades, and specific entities
    """
    import re
    
    # Remove common stopwords
    stopwords = {
        'what', 'is', 'the', 'tell', 'me', 'about', 'your', 'my', 
        'a', 'an', 'are', 'how', 'which', 'where', 'when', 'can', 'you'
    }
    
    # Extract words (alphanumeric + periods for versions)
    words = re.findall(r'[\w\.]+', question.lower())
    
    # Filter stopwords and short words
    keywords = [
        word for word in words 
        if word not in stopwords and len(word) > 2
    ]
    
    print(f"Extracted keywords: {keywords}")
    return keywords


def merge_results(vector_results, keyword_results):
    """
    Merge vector and keyword search results, removing duplicates
    Prioritizes keyword matches (exact matches) over vector matches
    """
    seen_content = set()
    merged = []
    
    # Add keyword results first (exact matches are gold)
    for content, score, search_type in keyword_results:
        content_key = content[:100]  # Use first 100 chars as unique key
        if content_key not in seen_content:
            seen_content.add(content_key)
            merged.append((content, score, search_type))
    
    # Add vector results
    for content, score, chunk_id in vector_results:
        content_key = content[:100]
        if content_key not in seen_content:
            seen_content.add(content_key)
            merged.append((content, score, 'vector'))
    
    return merged


def get_all_chunks():
    """
    Emergency function: Retrieve ALL chunks from the database
    Use when you need 100% coverage (e.g., "summarize entire resume")
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT content FROM resume_chunks ORDER BY id;")
        results = cur.fetchall()
        
        print(f"\n--- FULL RETRIEVAL ---")
        print(f"Retrieved ALL {len(results)} chunks from database")
        print("--- END DEBUG ---\n")
        
        return [(res[0], 1.0, 0) for res in results]
        
    except Exception as e:
        print(f"❌ Error retrieving all chunks: {e}")
        return []
    finally:
        cur.close()
        conn.close()


# Test function
if __name__ == "__main__":
    print("Testing Enhanced Retrieval System\n")
    
    # Test 1: Standard vector search
    print("TEST 1: Vector Search")
    results = query_resume("What are Sahil's academic achievements?", top_k=15)
    print(f"Retrieved {len(results)} chunks\n")
    
    # Test 2: Hybrid search
    print("TEST 2: Hybrid Search")
    results = hybrid_search("10th percentage Image Forgery project", top_k=15)
    print(f"Retrieved {len(results)} chunks\n")
    
    # Test 3: Section-specific search
    print("TEST 3: Section Search")
    results = query_by_section("Projects", top_k=10)
    print(f"Retrieved {len(results)} chunks\n")