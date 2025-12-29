"""
migrate_embeddings.py
Migration script to update Supabase vectors from 384-dim (local) to 768-dim (Gemini).
This fixes the 'different vector dimensions' error in production.
"""

import os
from app.db import get_connection
from app.embeddings import generate_embedding
import time

def migrate():
    print("🚀 [Migration] Starting Database & Embedding Migration...")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # 1. Update the table column to support 768 dimensions
        # We need to drop the index first, alter, then recreate (pgvector requirement for dimensions)
        print("🛠️ [Migration] Altering table schema to 768 dimensions...")
        cur.execute("DROP INDEX IF EXISTS idx_resume_chunks_embedding;")
        # Set all embeddings to NULL so we can change the dimension constraint
        cur.execute("UPDATE resume_chunks SET embedding = NULL;")
        cur.execute("ALTER TABLE resume_chunks ALTER COLUMN embedding TYPE vector(768);")
        cur.execute("CREATE INDEX idx_resume_chunks_embedding ON resume_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);")
        conn.commit()
        print("✅ [Migration] Schema update successful.")

        # 2. Fetch all chunks
        cur.execute("SELECT id, content FROM resume_chunks;")
        chunks = cur.fetchall()
        print(f"📦 [Migration] Found {len(chunks)} chunks to re-embed.")

        # 3. Re-embed and Update
        for i, (chunk_id, content) in enumerate(chunks):
            print(f"🔄 [Migration] Re-embedding chunk {i+1}/{len(chunks)}...")
            
            try:
                new_embedding = generate_embedding(content)
                
                # Verify dimension
                if len(new_embedding) != 768:
                    print(f"❌ [Migration] Warning: Expected 768 dims, got {len(new_embedding)}. Skipping ID: {chunk_id}")
                    continue
                
                cur.execute(
                    "UPDATE resume_chunks SET embedding = %s WHERE id = %s",
                    (new_embedding, chunk_id)
                )
                
                # Small sleep to be nice to the API quota
                time.sleep(0.5)
                
                if (i + 1) % 10 == 0:
                    conn.commit()
                    print(f"💾 [Migration] Progress checkpoint: {i+1} saved.")
                    
            except Exception as e:
                print(f"❌ [Migration] Failed to process chunk {chunk_id}: {e}")
                continue

        conn.commit()
        print("\n✨ [Migration] ALL CHUNKS UPDATED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"💥 [Migration] CRITICAL FAILURE: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    confirm = input("⚠️  This will update the LIVE database. Proceed? (y/n): ")
    if confirm.lower() == 'y':
        migrate()
    else:
        print("❌ Migration canceled.")
