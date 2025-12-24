from sentence_transformers import SentenceTransformer

# Load once
model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5",
    device="cpu"
)

def generate_embedding(text: str):
    """
    Convert text into pgvector-compatible embedding list.
    Using 'generate_embedding' name to match your ingest script.
    """
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()