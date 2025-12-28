import psycopg2
import os
from dotenv import load_dotenv

# This looks for the .env file
load_dotenv() 

def get_connection():
    url = os.getenv("DATABASE_URL")
    if not url:
        print("❌ [DB] DATABASE_URL not found!")
        raise ValueError("DATABASE_URL not found in environment variables")
    try:
        conn = psycopg2.connect(url)
        return conn
    except Exception as e:
        print(f"❌ [DB] Connection failed: {e}")
        raise e