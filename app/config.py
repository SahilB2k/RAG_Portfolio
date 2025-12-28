import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_ENV = os.getenv('APP_ENV', 'dev')
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # CORS Settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # LLM API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Gunicorn / Production Settings
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = APP_ENV == 'dev'

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

def get_config():
    env = os.getenv('APP_ENV', 'dev')
    if env == 'prod':
        return ProductionConfig()
    return DevelopmentConfig()
