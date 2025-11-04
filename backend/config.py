"""Configuration management"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Paths
    SAMPLE_PROJECTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'sample_projects')
    
    # Graph settings
    MAX_DEPTH = 5  # Max depth for graph traversal

config = Config()
