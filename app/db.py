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

def log_resume_download(email, purpose, note, source_ref=None, browser=None):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO resume_downloads (email, purpose, note, source_ref, browser_info) VALUES (%s, %s, %s, %s, %s)",
            (email, purpose, note, source_ref, browser)
        )
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"❌ [DB] Error: {e}")
        return False
    finally:
        if conn: conn.close()