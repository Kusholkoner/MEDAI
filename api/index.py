"""
Vercel API endpoint - Entry point for serverless function
"""
import sys
import os

# Add parent directory to path to import api_server_vercel
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_server_vercel import app

# Export the FastAPI app for Vercel
handler = app
