from dotenv import load_dotenv
from pathlib import Path

# Explicitly load .env from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from app.db import get_connection

try:
    conn = get_connection()
    print("✅ Database connected successfully")
    conn.close()
except Exception as e:
    print("❌ Database connection failed:", e)
