

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import sys
import os

# Import classes from main.py
from main import (
    MedicalDiagnosisSystem,
    UserAuthSystem,
    DoctorProfile,
    AppointmentSystem,
    MedicineReminder,
    HealthMonitor,
    HospitalLocator,
    logger,
    SUPABASE_AVAILABLE,
    supabase
)

# Initialize FastAPI app
app = FastAPI(
    title="Medical Diagnosis System API",
    description="REST API for medical diagnosis, appointments, and health monitoring",
    version="1.0.0"
)

# CORS configuration - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory where api_server.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Serve static HTML files
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

# Initialize system components
medical_system = MedicalDiagnosisSystem()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)



class UserRegister(BaseModel):
    email: EmailStr
    name: str
    phone: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    email: str
    name: str
    phone: str
    user_type: str
    registered_on: str
    login_count: int

class DiagnosisRequest(BaseModel):
    symptoms: str

class DiagnosisResponse(BaseModel):
    timestamp: str
    symptoms: List[str]
    disease: str
    confidence: float
    info: Dict[str, Any]
    is_emergency: bool
    ai_analysis: Optional[str] = None
    alternative_diagnoses: Optional[List[Dict[str, Any]]] = None

class AppointmentCreate(BaseModel):
    age: str
    symptoms: str
    doctor_id: str
    appointment_date: str
    appointment_time: str
    is_emergency: bool = False

class AppointmentResponse(BaseModel):
    appointment_id: str
    patient_name: str
    patient_phone: str
    patient_age: str
    symptoms: str
    doctor_id: str
    appointment_date: str
    appointment_time: str
    is_emergency: bool
    status: str
    booked_on: str

class ReminderCreate(BaseModel):
    medicine_name: str
    dosage: str
    time: str
    start_date: str
    end_date: Optional[str] = None
    notes: Optional[str] = None

class HealthRecordCreate(BaseModel):
    date: str
    blood_pressure: Optional[str] = None
    heart_rate: Optional[int] = None
    sugar_level: Optional[float] = None
    weight: Optional[float] = None
    temperature: Optional[float] = None



async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """Get current user from token (email-based for simplicity)"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Simple token = email for now (in production, use JWT)
    email = token
    
    # Get user from system
    if email not in medical_system.auth_system.users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return medical_system.auth_system.users[email]



@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Medical Diagnosis System API",
        "version": "1.0.0",
        "supabase_connected": SUPABASE_AVAILABLE
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "supabase": SUPABASE_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

# ============================================
# Authentication Endpoints
# ============================================

@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserRegister):
    """Register a new user"""
    try:
        # Check if user already exists in memory
        if user.email in medical_system.auth_system.users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        
        # Check if user exists in Supabase
        if SUPABASE_AVAILABLE and supabase:
            try:
                existing = supabase.table('users').select('email').eq('email', user.email).execute()
                if existing.data and len(existing.data) > 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User already exists in database"
                    )
            except Exception as e:
                logger.warning("Could not check existing user in Supabase", error=str(e))
        
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
        
        # Save to memory first
        medical_system.auth_system.users[user.email] = user_data
        
        # Persist to Supabase if available
        if SUPABASE_AVAILABLE and supabase:
            try:
                logger.info("Attempting to save user to Supabase", email=user.email)
                result = supabase.table('users').insert(user_data).execute()
                logger.info("User saved to Supabase successfully", email=user.email, result=str(result))
            except Exception as e:
                logger.error("Failed to save user to Supabase", error=str(e), error_type=type(e).__name__)
                # Don't fail registration if Supabase save fails - user is still in memory
                print(f"⚠️ Warning: User registered in memory but failed to save to Supabase: {str(e)}")
        else:
            logger.warning("Supabase not available - user saved to memory only")
        
        logger.info("User registered successfully", email=user.email)
        
        # Return user data without password hash
        response_data = {k: v for k, v in user_data.items() if k != 'password_hash'}
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration failed", error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/api/auth/login")
async def login(user: UserLogin):
    """Login user and return token"""
    try:
        # Check if user exists
        if user.email not in medical_system.auth_system.users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. Please register first."
            )
        
        # Get user data
        user_data = medical_system.auth_system.users[user.email]
        
        # Verify password
        import bcrypt
        stored_hash = user_data.get('password_hash', '').encode('utf-8')
        if not stored_hash or not bcrypt.checkpw(user.password.encode('utf-8'), stored_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
        
        # Update login count
        user_data['login_count'] = user_data.get('login_count', 0) + 1
        user_data['last_login'] = datetime.now().isoformat()
        # Persist update to Supabase if available
        if SUPABASE_AVAILABLE and supabase:
            try:
                medical_system.auth_system.save_user(user_data)
            except Exception as e:
                logger.error("Failed to save user to database on login", error=str(e))
        else:
            # In-memory only
            medical_system.auth_system.users[user.email] = user_data
        
        logger.info("User logged in", email=user.email)
        
        # Return user data and token (token = email for simplicity)
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

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.put("/api/auth/profile", response_model=UserResponse)
async def update_profile(
    name: Optional[str] = None,
    phone: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Update user profile"""
    try:
        if name:
            current_user['name'] = name
        if phone:
            current_user['phone'] = phone
        
        medical_system.auth_system.users[current_user['email']] = current_user
        medical_system.auth_system.save_users()
        
        logger.info("Profile updated", email=current_user['email'])
        
        return current_user
        
    except Exception as e:
        logger.error("Profile update failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================
# Diagnosis Endpoints
# ============================================

@app.post("/api/diagnosis", response_model=DiagnosisResponse)
async def diagnose_symptoms(
    request: DiagnosisRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Diagnose symptoms using AI"""
    try:
        # Set current user for diagnosis
        medical_system.auth_system.current_user = current_user
        
        # Perform diagnosis
        result = medical_system.diagnose(request.symptoms, 'patient')
        
        if 'error' in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )
        
        # Save diagnosis to Supabase
        if SUPABASE_AVAILABLE and supabase:
            try:
                diagnosis_record = {
                    'user_email': current_user['email'],
                    'timestamp': result['timestamp'],
                    'input_symptoms': result['input_symptoms'],
                    'primary_diagnosis': result['primary_diagnosis'],
                    'ai_analysis': result.get('ai_analysis')
                }
                supabase.table('diagnosis_history').insert(diagnosis_record).execute()
                logger.info("Diagnosis saved to database", user_email=current_user['email'])
            except Exception as e:
                logger.error("Failed to save diagnosis to Supabase", error=str(e))
                # Don't fail the request if saving fails, just log it
        
        logger.incr("api_diagnoses")
        
        # Prepare alternative diagnoses with full disease info
        alternative_diagnoses = []
        for alt in result.get('alternative_diagnoses', []):
            alt_disease_info = medical_system.db.get_disease_info(alt['disease'])
            alternative_diagnoses.append({
                'disease': alt['disease'],
                'confidence': alt['confidence'],
                'info': alt_disease_info,
                'is_emergency': medical_system.db.is_emergency(alt['disease'])
            })
        
        return {
            'timestamp': result['timestamp'],
            'symptoms': result['input_symptoms'],
            'disease': result['primary_diagnosis']['disease'],
            'confidence': result['primary_diagnosis']['confidence'],
            'info': result['primary_diagnosis']['info'],
            'is_emergency': result['primary_diagnosis']['is_emergency'],
            'ai_analysis': result.get('ai_analysis'),
            'alternative_diagnoses': alternative_diagnoses
        }
        
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
    """Get user's diagnosis history from Supabase"""
    try:
        if not SUPABASE_AVAILABLE or not supabase:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not available"
            )
        
        # Fetch from Supabase
        response = supabase.table('diagnosis_history').select('*').eq('user_email', current_user['email']).order('timestamp', desc=True).execute()
        
        # Transform data to match expected format
        history = []
        for record in (response.data or []):
            history.append({
                'timestamp': record['timestamp'],
                'input_symptoms': record['input_symptoms'],
                'primary_diagnosis': record['primary_diagnosis'],
                'ai_analysis': record.get('ai_analysis')
            })
        
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get history", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/symptoms")
async def get_all_symptoms():
    """Get all available symptoms"""
    return {
        "symptoms": medical_system.db.all_symptoms,
        "count": len(medical_system.db.all_symptoms)
    }

# ============================================
# Doctor Endpoints
# ============================================

@app.get("/api/doctors")
async def get_doctors(
    specialization: Optional[str] = None,
    emergency: Optional[bool] = None
):
    """Search doctors by criteria"""
    try:
        doctors = medical_system.doctor_profiles.search_doctors(
            specialization=specialization,
            emergency=emergency
        )
        
        return {
            "doctors": doctors,
            "count": len(doctors)
        }
        
    except Exception as e:
        logger.error("Failed to get doctors", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/doctors/{doctor_id}")
async def get_doctor(doctor_id: str):
    """Get specific doctor details"""
    try:
        doctor = medical_system.doctor_profiles.get_doctor(doctor_id)
        
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )
        
        return doctor
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get doctor", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================
# Appointment Endpoints
# ============================================

@app.post("/api/appointments", response_model=AppointmentResponse)
async def create_appointment(
    appointment: AppointmentCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Book a new appointment"""
    try:
        patient_info = {
            'name': current_user['name'],
            'phone': current_user['phone'],
            'age': appointment.age,
            'symptoms': appointment.symptoms
        }
        
        result = medical_system.appointment_system.book_appointment(
            patient_info=patient_info,
            doctor_id=appointment.doctor_id,
            appointment_date=appointment.appointment_date,
            appointment_time=appointment.appointment_time,
            is_emergency=appointment.is_emergency
        )
        
        # Add user email to result
        result['user_email'] = current_user['email']
        
        # Save to Supabase if available
        if SUPABASE_AVAILABLE and supabase:
            try:
                supabase.table('appointments').insert(result).execute()
            except Exception as e:
                logger.error("Failed to save appointment to Supabase", error=str(e))
        
        logger.incr("api_appointments")
        
        return result
        
    except Exception as e:
        logger.error("Failed to create appointment", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/appointments")
async def get_appointments(current_user: Dict = Depends(get_current_user)):
    """Get user's appointments"""
    try:
        # Filter appointments for current user
        user_appointments = [
            apt for apt in medical_system.appointment_system.appointments
            if apt.get('patient_phone') == current_user['phone']
        ]
        
        return {
            "appointments": user_appointments,
            "count": len(user_appointments)
        }
        
    except Exception as e:
        logger.error("Failed to get appointments", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================
# Medicine Reminder Endpoints
# ============================================

@app.post("/api/reminders")
async def create_reminder(
    reminder: ReminderCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Create a medicine reminder"""
    try:
        reminder_data = {
            'medicine_name': reminder.medicine_name,
            'dosage': reminder.dosage,
            'time': reminder.time,
            'start_date': reminder.start_date,
            'end_date': reminder.end_date,
            'notes': reminder.notes
        }
        
        success = medical_system.reminder.add_reminder(
            user_email=current_user['email'],
            reminder=reminder_data
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create reminder"
            )
        
        logger.incr("api_reminders")
        
        return {
            "message": "Reminder created successfully",
            "reminder": reminder_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create reminder", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/reminders")
async def get_reminders(current_user: Dict = Depends(get_current_user)):
    """Get user's medicine reminders"""
    try:
        reminders = medical_system.reminder.get_reminders(current_user['email'])
        
        return {
            "reminders": reminders,
            "count": len(reminders)
        }
        
    except Exception as e:
        logger.error("Failed to get reminders", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================
# Health Monitoring Endpoints
# ============================================

@app.post("/api/health-records")
async def create_health_record(
    record: HealthRecordCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Create a health record"""
    try:
        record_data = {
            'date': record.date,
            'blood_pressure': record.blood_pressure,
            'heart_rate': record.heart_rate,
            'sugar_level': record.sugar_level,
            'weight': record.weight,
            'temperature': record.temperature
        }
        
        success = medical_system.health_monitor.add_record(
            user_email=current_user['email'],
            record=record_data
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create health record"
            )
        
        logger.incr("api_health_records")
        
        return {
            "message": "Health record created successfully",
            "record": record_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create health record", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/health-records")
async def get_health_records(current_user: Dict = Depends(get_current_user)):
    """Get user's health records"""
    try:
        records = medical_system.health_monitor.get_history(current_user['email'])
        
        return {
            "records": records,
            "count": len(records)
        }
        
    except Exception as e:
        logger.error("Failed to get health records", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================
# Statistics Endpoint
# ============================================

@app.get("/api/statistics")
async def get_statistics(current_user: Dict = Depends(get_current_user)):
    """Get system statistics"""
    try:
        stats = logger.dump()
        
        return {
            "database": {
                "total_diseases": len(medical_system.db.disease_data),
                "total_symptoms": len(medical_system.db.all_symptoms),
                "emergency_conditions": sum(1 for d in medical_system.db.disease_data.values() if d.get('emergency', False))
            },
            "doctors": {
                "total_doctors": len(medical_system.doctor_profiles.doctors),
                "emergency_available": len(medical_system.doctor_profiles.search_doctors(emergency=True))
            },
            "user": {
                "total_users": len(medical_system.auth_system.users),
                "login_count": current_user.get('login_count', 0),
                "last_login": current_user.get('last_login'),
                "registered_on": current_user.get('registered_on')
            },
            "metrics": stats['metrics']
        }
        
    except Exception as e:
        logger.error("Failed to get statistics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================
# Run Server
# ============================================

if __name__ == "__main__":
    import uvicorn
    print("=" * 80)
    print("MEDICAL DIAGNOSIS SYSTEM - API SERVER")
    print("=" * 80)
    print(f"Supabase Connected: {SUPABASE_AVAILABLE}")
    print("Starting server on http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("=" * 80)
    
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
