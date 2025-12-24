"""
Enhanced ingest_resume.py - Production-Ready Data Ingestion
Key Improvements:
1. Contextual chunking (adds Sahil's name to every chunk)
2. Smart section detection and labeling
3. Metadata extraction (section type, keywords)
4. Chunk quality validation
"""

import re
from app.db import get_connection
from app.embeddings import generate_embedding


def detect_section_type(chunk_text):
    """
    Detect what type of section this chunk belongs to
    Helps with section-specific queries
    """
    chunk_lower = chunk_text.lower()
    
    if any(keyword in chunk_lower for keyword in ['education', 'academic', 'cgpa', 'percentage', '10th', '12th']):
        return 'Education'
    elif any(keyword in chunk_lower for keyword in ['project', 'developed', 'implemented', 'built']):
        return 'Projects'
    elif any(keyword in chunk_lower for keyword in ['skill', 'language', 'framework', 'tool', 'python', 'tensorflow']):
        return 'Technical Skills'
    elif any(keyword in chunk_lower for keyword in ['certification', 'nptel', 'course', 'certificate']):
        return 'Certifications'
    elif any(keyword in chunk_lower for keyword in ['achievement', 'award', 'hackathon', 'competition']):
        return 'Achievements'
    else:
        return 'General'


def extract_keywords(chunk_text):
    """
    Extract important keywords from chunk for better searchability
    """
    # Technical terms to preserve
    keywords = []
    
    # Programming languages
    languages = ['python', 'java', 'javascript', 'c++', 'sql', 'r']
    keywords.extend([lang for lang in languages if lang in chunk_text.lower()])
    
    # Frameworks and tools
    frameworks = ['tensorflow', 'pytorch', 'keras', 'react', 'django', 'flask', 'opencv']
    keywords.extend([fw for fw in frameworks if fw in chunk_text.lower()])
    
    # Academic terms
    academic = ['cgpa', 'percentage', 'grade', 'marks']
    keywords.extend([term for term in academic if term in chunk_text.lower()])
    
    return ', '.join(keywords) if keywords else None


def create_contextual_chunk(chunk_text, section_type):
    """
    Add context to each chunk so it's never "orphaned"
    This ensures every chunk mentions Sahil and provides context
    """
    
    # Base context
    context_prefix = "Sahil Jadhav's Resume"
    
    # Add section-specific context
    if section_type == 'Education':
        context_prefix = "Sahil Jadhav's Educational Background"
    elif section_type == 'Projects':
        context_prefix = "Sahil Jadhav's Project Experience"
    elif section_type == 'Technical Skills':
        context_prefix = "Sahil Jadhav's Technical Skills"
    elif section_type == 'Certifications':
        context_prefix = "Sahil Jadhav's Certifications"
    elif section_type == 'Achievements':
        context_prefix = "Sahil Jadhav's Achievements"
    
    # Construct enriched chunk
    enriched_chunk = f"{context_prefix}:\n{chunk_text}"
    
    return enriched_chunk


def validate_chunk(chunk_text):
    """
    Ensure chunk has sufficient information and isn't just a header
    """
    # Minimum length requirement
    if len(chunk_text.strip()) < 20:
        return False, "Chunk too short"
    
    # Must have at least some alphanumeric content
    if not re.search(r'[a-zA-Z0-9]', chunk_text):
        return False, "No meaningful content"
    
    # Shouldn't be just a single header
    lines = chunk_text.strip().split('\n')
    if len(lines) == 1 and lines[0].startswith('#'):
        return False, "Header only"
    
    return True, "Valid"


def ingest(verbose=True):
    """
    Production-ready ingestion with contextual chunking and validation
    
    Args:
        verbose: Whether to print detailed progress
    """
    
    # Load resume
    try:
        with open("data/resume.md", "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print("❌ Error: resume.md not found in data/ directory")
        return
    except Exception as e:
        print(f"❌ Error reading resume: {e}")
        return
    
    if verbose:
        print("\n" + "="*60)
        print("📥 Starting Enhanced Resume Ingestion")
        print("="*60 + "\n")
    
    # Split by headers (supports #, ##, ###)
    # This keeps each section and sub-section separate
    chunks = re.split(r'\n(?=#+ )', text)
    chunks = [c.strip() for c in chunks if len(c.strip()) > 5]
    
    if verbose:
        print(f"📄 Found {len(chunks)} raw chunks from resume.md\n")
    
    # Process chunks with validation
    processed_chunks = []
    skipped_chunks = []
    
    for idx, chunk in enumerate(chunks, 1):
        # Validate chunk quality
        is_valid, reason = validate_chunk(chunk)
        
        if not is_valid:
            skipped_chunks.append((idx, chunk[:50], reason))
            continue
        
        # Detect section type
        section_type = detect_section_type(chunk)
        
        # Extract keywords
        keywords = extract_keywords(chunk)
        
        # Create contextual chunk
        enriched_chunk = create_contextual_chunk(chunk, section_type)
        
        # Generate embedding
        try:
            embedding = generate_embedding(enriched_chunk)
        except Exception as e:
            print(f"⚠️ Warning: Failed to generate embedding for chunk {idx}: {e}")
            continue
        
        processed_chunks.append({
            'original': chunk,
            'enriched': enriched_chunk,
            'embedding': embedding,
            'section_type': section_type,
            'keywords': keywords,
            'chunk_index': idx
        })
        
        if verbose:
            print(f"✅ Chunk {idx:2d} | Section: {section_type:20s} | Length: {len(chunk):4d} chars")
            if keywords:
                print(f"           Keywords: {keywords}")
            print(f"           Preview: {chunk[:60]}...")
            print()
    
    # Display skipped chunks
    if skipped_chunks and verbose:
        print(f"\n⚠️ Skipped {len(skipped_chunks)} invalid chunks:")
        for idx, preview, reason in skipped_chunks:
            print(f"   Chunk {idx}: {reason} - '{preview}...'")
        print()
    
    # Insert into database
    if not processed_chunks:
        print("❌ Error: No valid chunks to insert!")
        return
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Clear existing data
        cur.execute("TRUNCATE TABLE resume_chunks;")
        if verbose:
            print("🗑️ Cleared existing resume data\n")
        
        # Insert new chunks
        for chunk_data in processed_chunks:
            cur.execute(
                """
                INSERT INTO resume_chunks (content, embedding) 
                VALUES (%s, %s::vector)
                """,
                (chunk_data['original'], chunk_data['embedding'])
            )
        
        conn.commit()
        
        if verbose:
            print("="*60)
            print(f"✅ SUCCESS!")
            print(f"   • Processed: {len(processed_chunks)} chunks")
            print(f"   • Skipped: {len(skipped_chunks)} invalid chunks")
            print(f"   • Database: Updated with fresh embeddings")
            print("="*60 + "\n")
        
        # Display section distribution
        section_counts = {}
        for chunk in processed_chunks:
            section = chunk['section_type']
            section_counts[section] = section_counts.get(section, 0) + 1
        
        if verbose:
            print("📊 Section Distribution:")
            for section, count in sorted(section_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {section}: {count} chunks")
            print()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        
    finally:
        cur.close()
        conn.close()


def verify_ingestion():
    """
    Verify that ingestion was successful
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Count total chunks
        cur.execute("SELECT COUNT(*) FROM resume_chunks;")
        total = cur.fetchone()[0]
        
        # Sample a few chunks
        cur.execute("SELECT content FROM resume_chunks LIMIT 3;")
        samples = cur.fetchall()
        
        print("\n" + "="*60)
        print("🔍 Ingestion Verification")
        print("="*60)
        print(f"Total chunks in database: {total}")
        print("\nSample chunks:")
        for idx, (content,) in enumerate(samples, 1):
            print(f"\n{idx}. {content[:100]}...")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    print("\n🚀 Enhanced Resume Ingestion System\n")
    
    # Run ingestion
    ingest(verbose=True)
    
    # Verify results
    verify_ingestion()
    
    print("✨ Ingestion complete! Your resume is now fully searchable.\n")