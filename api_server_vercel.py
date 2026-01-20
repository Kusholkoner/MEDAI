"""
Vercel-optimized API server without heavy ML dependencies.
This version uses a lightweight disease database and relies on Gemini AI for diagnosis.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import os
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Supabase
SUPABASE_AVAILABLE = False
supabase = None

try:
    from supabase import create_client, Client
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    
    if supabase_url and supabase_key:
        supabase: Client = create_client(supabase_url, supabase_key)
        SUPABASE_AVAILABLE = True
        print("✅ Supabase connected")
except Exception as e:
    print(f"⚠️ Supabase not available: {e}")

# Initialize Gemini AI
GEMINI_AVAILABLE = False
model = None

try:
    import google.generativeai as genai
    google_api_key = os.getenv('GOOGLE_API_KEY', '')
    
    if google_api_key:
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel('gemini-pro')
        GEMINI_AVAILABLE = True
        print("✅ Gemini AI connected")
except Exception as e:
    print(f"⚠️ Gemini AI not available: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="MEDAI - Medical Diagnosis System",
    description="AI-powered medical diagnosis and healthcare management",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    name: str
    phone: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class DiagnosisRequest(BaseModel):
    symptoms: str

# Simple logger
class SimpleLogger:
    def __init__(self):
        self.metrics = {}
    
    def info(self, msg, **kwargs):
        print(f"INFO: {msg}", kwargs)
    
    def error(self, msg, **kwargs):
        print(f"ERROR: {msg}", kwargs)
    
    def warning(self, msg, **kwargs):
        print(f"WARNING: {msg}", kwargs)
    
    def incr(self, metric):
        self.metrics[metric] = self.metrics.get(metric, 0) + 1
    
    def dump(self):
        return {"metrics": self.metrics}

logger = SimpleLogger()

# In-memory user storage
users_cache = {}

# OAuth2 scheme
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """Get current user from token"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    if token not in users_cache:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return users_cache[token]

# Serve static files
@app.get("/", response_class=FileResponse)
async def serve_index():
    """Serve the login page"""
    return FileResponse(os.path.join(BASE_DIR, "frontend", "pages", "index.html"))

@app.get("/dashboard.html", response_class=FileResponse)
async def serve_dashboard():
    """Serve the dashboard page"""
    return FileResponse(os.path.join(BASE_DIR, "frontend", "pages", "dashboard.html"))

@app.get("/assets/js/script.js", response_class=FileResponse)
async def serve_script():
    """Serve JavaScript file"""
    return FileResponse(os.path.join(BASE_DIR, "frontend", "assets", "js", "script.js"))

@app.get("/assets/css/styles.css", response_class=FileResponse)
async def serve_styles():
    """Serve CSS file"""
    return FileResponse(os.path.join(BASE_DIR, "frontend", "assets", "css", "styles.css"))

# API Endpoints
@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "message": "MEDAI - Medical Diagnosis System API",
        "version": "2.0.0",
        "supabase_connected": SUPABASE_AVAILABLE,
        "gemini_connected": GEMINI_AVAILABLE
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "supabase": SUPABASE_AVAILABLE,
        "gemini": GEMINI_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

# Authentication Endpoints
@app.post("/api/auth/register")
async def register(user: UserRegister):
    """Register a new user"""
    try:
        # Check if user exists
        if SUPABASE_AVAILABLE and supabase:
            existing = supabase.table('users').select('email').eq('email', user.email).execute()
            if existing.data and len(existing.data) > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already exists"
                )
        
        # Hash password
        import bcrypt
        password_hash = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user data
        user_data = {
            'email': user.email,
            'name': user.name,
            'phone': user.phone,
            'password_hash': password_hash,
            'user_type': 'patient',
            'registered_on': datetime.now().isoformat(),
            'login_count': 1,
            'last_login': datetime.now().isoformat()
        }
        
        # Save to Supabase
        if SUPABASE_AVAILABLE and supabase:
            supabase.table('users').insert(user_data).execute()
            logger.info("User registered", email=user.email)
        
        # Cache user
        users_cache[user.email] = user_data
        
        # Return user data without password
        response_data = {k: v for k, v in user_data.items() if k != 'password_hash'}
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/api/auth/login")
async def login(user: UserLogin):
    """Login user and return token"""
    try:
        # Get user from Supabase
        if SUPABASE_AVAILABLE and supabase:
            response = supabase.table('users').select('*').eq('email', user.email).execute()
            if not response.data or len(response.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            user_data = response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not available"
            )
        
        # Verify password
        import bcrypt
        stored_hash = user_data.get('password_hash', '').encode('utf-8')
        if not bcrypt.checkpw(user.password.encode('utf-8'), stored_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
        
        # Update login count
        user_data['login_count'] = user_data.get('login_count', 0) + 1
        user_data['last_login'] = datetime.now().isoformat()
        
        if SUPABASE_AVAILABLE and supabase:
            supabase.table('users').update({
                'login_count': user_data['login_count'],
                'last_login': user_data['last_login']
            }).eq('email', user.email).execute()
        
        # Cache user
        users_cache[user.email] = user_data
        
        logger.info("User logged in", email=user.email)
        
        # Return user data and token
        response_data = {k: v for k, v in user_data.items() if k != 'password_hash'}
        return {
            "access_token": user.email,
            "token_type": "bearer",
            "user": response_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/auth/me")
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """Get current user information"""
    return {k: v for k, v in current_user.items() if k != 'password_hash'}

# Diagnosis Endpoint
@app.post("/api/diagnosis")
async def diagnose_symptoms(
    request: DiagnosisRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Diagnose symptoms using Gemini AI"""
    try:
        if not GEMINI_AVAILABLE or not model:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI diagnosis not available"
            )
        
        # Create AI prompt
        prompt = f"""As a medical AI assistant, analyze these symptoms and provide a preliminary diagnosis:

Symptoms: {request.symptoms}

Please provide:
1. Most likely condition/disease
2. Confidence level (0-100%)
3. Brief description
4. Recommended precautions
5. Whether this is an emergency (yes/no)
6. Alternative possible diagnoses

Format your response as JSON with keys: disease, confidence, description, precautions, is_emergency, alternatives"""

        # Get AI response
        response = model.generate_content(prompt)
        ai_analysis = response.text
        
        # Parse AI response (basic parsing)
        result = {
            'timestamp': datetime.now().isoformat(),
            'symptoms': request.symptoms.split(','),
            'ai_analysis': ai_analysis,
            'disease': 'See AI Analysis',
            'confidence': 0.85,
            'is_emergency': 'emergency' in ai_analysis.lower(),
            'info': {
                'description': 'AI-powered diagnosis',
                'precautions': 'Consult a healthcare professional',
                'severity': 'medium'
            }
        }
        
        # Save to Supabase
        if SUPABASE_AVAILABLE and supabase:
            try:
                diagnosis_record = {
                    'user_email': current_user['email'],
                    'timestamp': result['timestamp'],
                    'input_symptoms': request.symptoms,
                    'primary_diagnosis': result['disease'],
                    'ai_analysis': ai_analysis
                }
                supabase.table('diagnosis_history').insert(diagnosis_record).execute()
            except Exception as e:
                logger.error("Failed to save diagnosis", error=str(e))
        
        logger.incr("diagnoses")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Diagnosis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/diagnosis/history")
async def get_diagnosis_history(current_user: Dict = Depends(get_current_user)):
    """Get user's diagnosis history"""
    try:
        if not SUPABASE_AVAILABLE or not supabase:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not available"
            )
        
        response = supabase.table('diagnosis_history').select('*').eq('user_email', current_user['email']).order('timestamp', desc=True).execute()
        
        return response.data or []
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get history", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Doctors Endpoints
@app.get("/api/doctors")
async def get_doctors(specialization: Optional[str] = None):
    """Get doctors list"""
    try:
        if not SUPABASE_AVAILABLE or not supabase:
            return {"doctors": [], "count": 0}
        
        query = supabase.table('doctors').select('*')
        
        if specialization:
            query = query.ilike('specialization', f'%{specialization}%')
        
        response = query.execute()
        doctors = response.data or []
        
        return {"doctors": doctors, "count": len(doctors)}
        
    except Exception as e:
        logger.error("Failed to get doctors", error=str(e))
        return {"doctors": [], "count": 0}

@app.get("/api/doctors/{doctor_id}")
async def get_doctor(doctor_id: str):
    """Get specific doctor details"""
    try:
        if not SUPABASE_AVAILABLE or not supabase:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not available"
            )
        
        response = supabase.table('doctors').select('*').eq('id', doctor_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get doctor", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Statistics Endpoint
@app.get("/api/statistics")
async def get_statistics(current_user: Dict = Depends(get_current_user)):
    """Get system statistics"""
    try:
        stats = {
            "user": {
                "login_count": current_user.get('login_count', 0),
                "last_login": current_user.get('last_login'),
                "registered_on": current_user.get('registered_on')
            },
            "metrics": logger.dump()['metrics']
        }
        
        return stats
        
    except Exception as e:
        logger.error("Failed to get statistics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Vercel serverless function handler
app = app
