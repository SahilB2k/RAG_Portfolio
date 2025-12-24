from sentence_transformers import SentenceTransformer

# Load once (FAST)
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    device="cpu"  # Best for your system
)

def embed_text(text: str):
    """
    Convert text into pgvector-compatible embedding list
    """
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()
