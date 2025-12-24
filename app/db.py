import psycopg2
import os
from dotenv import load_dotenv

# This looks for the .env file
load_dotenv() 

def get_connection():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL not found in environment variables")
    return psycopg2.connect(url)