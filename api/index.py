"""
Minimal Vercel-compatible entry point
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

# Create a simple FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "MEDAI API is running on Vercel"}

@app.get("/api")
async def api_root():
    return {
        "message": "MEDAI API",
        "version": "2.0.0",
        "status": "healthy"
    }

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "supabase": os.getenv("SUPABASE_URL") is not None,
        "gemini": os.getenv("GOOGLE_API_KEY") is not None
    }

# Vercel handler
handler = app
