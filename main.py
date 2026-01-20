import numpy as np 
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
import datetime
import webbrowser
from typing import List, Dict, Any
import json
import os
import sys

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        # Python < 3.7 or reconfigure failed, use alternative
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Ensure .cursor directory exists for logging
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.cursor')
LOG_FILE = os.path.join(LOG_DIR, 'debug.log')
os.makedirs(LOG_DIR, exist_ok=True)

# Configuration
GOOGLE_API_KEY = 'GOOGLE_API_KEY'
SUPABASE_URL = 'YOUR_SUPABASE_URL'
# If you scaffolded API:
SUPABASE_KEY = 'YOUR_SUPABASE_KEY'

# Initialize Supabase
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize Supabase Client
SUPABASE_AVAILABLE = False
supabase = None

try:
    # #region agent log
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        import json
        import time
        f.write(json.dumps({"sessionId":"debug-session","runId":"init","hypothesisId":"A","location":"main.py:67","message":"Attempting Supabase import","data":{"supabase_url_set":SUPABASE_URL!='YOUR_SUPABASE_URL',"supabase_key_set":SUPABASE_KEY!='YOUR_SUPABASE_KEY'},"timestamp":int(time.time()*1000)})+'\n')
    # #endregion
    from supabase import create_client, Client
    # #region agent log
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"init","hypothesisId":"A","location":"main.py:72","message":"Supabase library imported successfully","data":{},"timestamp":int(time.time()*1000)})+'\n')
    # #endregion
    
    # Get Supabase credentials from environment or use config
    supabase_url = os.getenv("SUPABASE_URL", SUPABASE_URL)
    supabase_key = os.getenv("SUPABASE_KEY", SUPABASE_KEY)
    
    # #region agent log
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"init","hypothesisId":"B","location":"main.py:78","message":"Supabase credentials check","data":{"url_from_env":os.getenv("SUPABASE_URL") is not None,"key_from_env":os.getenv("SUPABASE_KEY") is not None,"url_is_placeholder":supabase_url=='YOUR_SUPABASE_URL',"key_is_placeholder":supabase_key=='YOUR_SUPABASE_KEY'},"timestamp":int(time.time()*1000)})+'\n')
    # #endregion
    
    if supabase_url and supabase_key and supabase_url != 'YOUR_SUPABASE_URL' and supabase_key != 'YOUR_SUPABASE_KEY' and supabase_url.strip() and supabase_key.strip():
        supabase: Client = create_client(supabase_url, supabase_key)
        # #region agent log
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"init","hypothesisId":"C","location":"main.py:85","message":"Supabase client created","data":{"url_length":len(supabase_url),"key_length":len(supabase_key)},"timestamp":int(time.time()*1000)})+'\n')
        # #endregion
        
        # Test connection by querying a table (this will fail gracefully if tables don't exist)
        try:
            # #region agent log
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"init","hypothesisId":"D","location":"main.py:90","message":"Testing Supabase connection","data":{},"timestamp":int(time.time()*1000)})+'\n')
            # #endregion
            # Try to access a table to verify connection
            test_response = supabase.table('doctors').select("id").limit(1).execute()
            # #region agent log
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"init","hypothesisId":"D","location":"main.py:95","message":"Supabase connection test successful","data":{"has_data":test_response.data is not None},"timestamp":int(time.time()*1000)})+'\n')
            # #endregion
            SUPABASE_AVAILABLE = True
            print("✅ Supabase connected successfully")
        except Exception as test_error:
            # #region agent log
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"init","hypothesisId":"D","location":"main.py:100","message":"Supabase connection test failed","data":{"error":str(test_error),"error_type":type(test_error).__name__},"timestamp":int(time.time()*1000)})+'\n')
            # #endregion
            print(f"⚠️ Supabase client created but connection test failed: {test_error}")
            print("⚠️ Continuing with fallback data. Make sure your Supabase tables exist.")
            SUPABASE_AVAILABLE = False
    else:
        # #region agent log
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"init","hypothesisId":"B","location":"main.py:106","message":"Supabase credentials not configured","data":{},"timestamp":int(time.time()*1000)})+'\n')
        # #endregion
        print("⚠️ Supabase credentials not configured. Using fallback data.")
        print("💡 To enable Supabase, set SUPABASE_URL and SUPABASE_KEY in .env file or update the config.")
except ImportError as import_error:
    # #region agent log
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        import json
        import time
        f.write(json.dumps({"sessionId":"debug-session","runId":"init","hypothesisId":"A","location":"main.py:111","message":"Supabase library import failed","data":{"error":str(import_error),"error_type":type(import_error).__name__},"timestamp":int(time.time()*1000)})+'\n')
    # #endregion
    print(f"⚠️ Supabase library not installed: {import_error}")
    print("💡 Install it with: pip install supabase")
    SUPABASE_AVAILABLE = False
    supabase = None
except Exception as e:
    # #region agent log
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        import json
        import time
        f.write(json.dumps({"sessionId":"debug-session","runId":"init","hypothesisId":"E","location":"main.py:118","message":"Unexpected error initializing Supabase","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":int(time.time()*1000)})+'\n')
    # #endregion
    print(f"⚠️ Failed to initialize Supabase: {e}")
    SUPABASE_AVAILABLE = False
    supabase = None

# Initialize Gemini / Generative AI Client (robust with fallbacks)
GEMINI_AVAILABLE = False
model = None
try:
    import google.generativeai as genai
    
    # Get API key from environment variable
    google_api_key = os.getenv('GOOGLE_API_KEY', '')
    
    if not google_api_key:
        print("⚠️ GOOGLE_API_KEY not found in environment variables")
        print("💡 AI-powered diagnosis will not be available")
        raise ValueError("GOOGLE_API_KEY not configured")
    
    genai.configure(api_key=google_api_key)

    # Try a list of likely-supported model identifiers until one works
    candidate_models = [
        'gemini-pro',
        'gemini-1.5-pro',
        'gemini-1.5',
        'models/gemini-1.5',
        'text-bison-001',
        'chat-bison'
    ]

    last_error = None
    for mname in candidate_models:
        try:
            model = genai.GenerativeModel(mname)
            GEMINI_AVAILABLE = True
            print(f"✅ Generative AI connected successfully (model={mname})")
            break
        except Exception as e:
            last_error = e

    # If none of the candidates worked, try to list available models (if supported)
    if not GEMINI_AVAILABLE:
        list_models_fn = getattr(genai, 'list_models', None) or getattr(genai, 'get_models', None)
        try:
            if callable(list_models_fn):
                available = list_models_fn()
                # print a compact list of model ids if possible
                try:
                    model_ids = [m['name'] if isinstance(m, dict) and 'name' in m else str(m) for m in (available or [])]
                except Exception:
                    model_ids = list(available or [])
                print("⚠️ Requested models not found. Available models:", model_ids)
            else:
                print("⚠️ Requested models not found. Call to list models is not available in this client.")
        except Exception as e:
            print("⚠️ Failed to list available models:", e)

        # Final informative message
        print("⚠️ Generative AI models not initialized. Update the model name or the client library (google.genai).")

except Exception as e:
    print(f"⚠️ Generative AI client not available: {e}")
    GEMINI_AVAILABLE = False
    model = None

# User Authentication System
class UserAuthSystem:
    def __init__(self):
        self.current_user = None
        self.users = {}
        self.load_users()
        
    def load_users(self):
        """Load users from Supabase database only"""
        if not SUPABASE_AVAILABLE or not supabase:
            logger.error("Supabase is required for production deployment")
            print("❌ Supabase database connection is required!")
            print("💡 Please configure SUPABASE_URL and SUPABASE_KEY in .env file")
            return
        
        try:
            response = supabase.table('users').select('*').execute()
            self.users = {}
            for user in (response.data or []):
                self.users[user['email']] = user
            logger.info("Users loaded from Supabase", count=len(self.users))
        except Exception as e:
            logger.error("Failed to load users from Supabase", error=str(e))
            print(f"⚠️ Failed to load users from database: {e}")
    
    def save_users(self):
        """Save/update user to Supabase database only - no JSON files"""
        if not SUPABASE_AVAILABLE or not supabase:
            logger.error("Supabase is required for saving users")
            raise Exception("Database connection required")
        
        # Note: Individual user updates should use upsert directly
        # This method is kept for compatibility but shouldn't be used for bulk saves
        pass
    
    def save_user(self, user_data):
        """Save or update a single user to Supabase"""
        if not SUPABASE_AVAILABLE or not supabase:
            raise Exception("Database connection required")
        
        try:
            supabase.table('users').upsert(user_data).execute()
            self.users[user_data['email']] = user_data
            logger.info("User saved to Supabase", email=user_data['email'])
            return True
        except Exception as e:
            logger.error("Failed to save user to Supabase", error=str(e))
            raise
    
    def google_login_simulation(self):
        """Simulate Google OAuth login"""
        print("\n" + "="*60)
        print("🔐 GOOGLE LOGIN")
        print("="*60)
        print("\nNote: This is a simulation of Google OAuth login")
        print("In production, this would redirect to Google's OAuth page\n")
        
        email = input("Enter your Google email: ").strip()
        if not email:
            print("❌ Email cannot be empty!")
            return None
        
        # Check if user exists
        if email in self.users:
            user_data = self.users[email]
            print(f"\n✅ Welcome back, {user_data['name']}!")
        else:
            # New user registration
            print("\n📝 First time login - Please complete your profile")
            name = input("Enter your full name: ").strip()
            phone = input("Enter your phone number: ").strip()
            
            user_data = {
                'email': email,
                'name': name,
                'phone': phone,
                'user_type': 'patient',  # default
                'registered_on': datetime.datetime.now().isoformat(),
                'login_count': 0
            }
            
            self.users[email] = user_data
            self.save_user(user_data)  # Save to Supabase
            print(f"\n✅ Account created successfully! Welcome, {name}!")
        
        # Update login count
        self.users[email]['login_count'] = self.users[email].get('login_count', 0) + 1
        self.users[email]['last_login'] = datetime.datetime.now().isoformat()
        self.save_user(self.users[email])  # Save to Supabase
        
        self.current_user = self.users[email]
        return self.current_user
        
        self.current_user = self.users[email]
        return self.current_user
    
    def switch_account(self):
        """Switch to different account"""
        print("\n" + "="*60)
        print("🔄 SWITCH ACCOUNT")
        print("="*60)
        
        if self.users:
            print("\nAvailable accounts:")
            accounts = list(self.users.keys())
            for i, email in enumerate(accounts, 1):
                user = self.users[email]
                print(f"{i}. {user['name']} ({email})")
            
            print(f"{len(accounts) + 1}. Login with different account")
            
            choice = input(f"\nSelect account (1-{len(accounts) + 1}): ").strip()
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(accounts):
                    email = accounts[choice_num - 1]
                    self.current_user = self.users[email]
                    print(f"\n✅ Switched to {self.current_user['name']}'s account")
                    return self.current_user
                elif choice_num == len(accounts) + 1:
                    return self.google_login_simulation()
            except ValueError:
                pass
        
        return self.google_login_simulation()
    
    def logout(self):
        """Logout current user"""
        if self.current_user:
            print(f"\n👋 Goodbye, {self.current_user['name']}!")
            self.current_user = None
        else:
            print("\n⚠️ No user is currently logged in")
    
    def get_current_user(self):
        """Get current logged in user"""
        return self.current_user
    
    def update_profile(self):
        """Update user profile"""
        if not self.current_user:
            print("\n❌ Please login first!")
            return
        
        print("\n" + "="*60)
        print("✏️ UPDATE PROFILE")
        print("="*60)
        print(f"\nCurrent Name: {self.current_user['name']}")
        print(f"Current Phone: {self.current_user['phone']}")
        # Only allow basic profile updates for patients (no role switching)
        print("\nWhat would you like to update?")
        print("1. Name")
        print("2. Phone")
        print("3. Back")

        choice = input("\nSelect option (1-3): ").strip()

        if choice == '1':
            new_name = input("Enter new name: ").strip()
            if new_name:
                self.current_user['name'] = new_name
                self.users[self.current_user['email']]['name'] = new_name
                self.save_user(self.current_user)  # Save to Supabase
                print("✅ Name updated successfully!")

        elif choice == '2':
            new_phone = input("Enter new phone: ").strip()
            if new_phone:
                self.current_user['phone'] = new_phone
                self.users[self.current_user['email']]['phone'] = new_phone
                self.save_user(self.current_user)  # Save to Supabase
                print("✅ Phone updated successfully!")

# Events Logger
class EventsLogger:
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        self.metrics: Dict[str, int] = {}

    def log(self, level: str, message: str, details: Dict[str, Any] = None):
        entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "level": level,
            "message": message,
            "details": details or {},
        }
        self.logs.append(entry)

    def info(self, message: str, **kwargs):
        self.log("INFO", message, kwargs)

    def error(self, message: str, **kwargs):
        self.log("ERROR", message, kwargs)

    def warning(self, message: str, **kwargs):
        self.log("WARNING", message, kwargs)

    def incr(self, metric_name: str, amount: int = 1):
        self.metrics[metric_name] = self.metrics.get(metric_name, 0) + amount

    def dump(self):
        return {
            "logs": self.logs[-50:],
            "metrics": self.metrics,
        }

logger = EventsLogger()

class DoctorProfile:
    def __init__(self):
        self.doctors = {}
        self.load_doctors()
        logger.info("Doctor profile system initialized")
    
    def load_doctors(self):
        """Load doctors from Supabase only. Doctors are read-only in-app.

        If Supabase is not configured, the doctors list will be empty and
        doctors must be managed from Supabase dashboard.
        """
        self.doctors = {}
        if not SUPABASE_AVAILABLE:
            print("❌ Supabase required for doctor listings. Doctors are managed via Supabase dashboard.")
            logger.info("Supabase unavailable - doctor listings disabled")
            return

        try:
            response = supabase.table('doctors').select('*').execute()
            for doc in (response.data or []):
                # Ensure we index by id
                doc_id = doc.get('id') or doc.get('uid') or doc.get('uuid')
                if not doc_id:
                    continue
                self.doctors[doc_id] = doc
            logger.info("Doctors loaded from Supabase", count=len(self.doctors))
        except Exception as e:
            logger.error("Failed to load doctors from Supabase", error=str(e))
    
    def add_doctor(self, doctor_info: Dict) -> str:
        """Add new doctor profile"""
        doctor_id = f"DR{str(len(self.doctors) + 1).zfill(3)}"
        doctor_info['id'] = doctor_id
        
        try:
            if SUPABASE_AVAILABLE:
                # #region agent log
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    import json
                    import time
                    f.write(json.dumps({"sessionId":"debug-session","runId":"add_doctor","hypothesisId":"I","location":"main.py:320","message":"Inserting doctor to Supabase","data":{"doctor_id":doctor_id},"timestamp":int(time.time()*1000)})+'\n')
                # #endregion
                supabase.table('doctors').insert(doctor_info).execute()
                # #region agent log
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"add_doctor","hypothesisId":"I","location":"main.py:323","message":"Doctor inserted to Supabase successfully","data":{"doctor_id":doctor_id},"timestamp":int(time.time()*1000)})+'\n')
                # #endregion
            
            self.doctors[doctor_id] = doctor_info
            logger.info("New doctor added", doctor_id=doctor_id)
            return doctor_id
        except Exception as e:
            # #region agent log
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                import json
                import time
                f.write(json.dumps({"sessionId":"debug-session","runId":"add_doctor","hypothesisId":"I","location":"main.py:331","message":"Failed to save doctor to Supabase","data":{"error":str(e),"error_type":type(e).__name__,"doctor_id":doctor_id},"timestamp":int(time.time()*1000)})+'\n')
            # #endregion
            logger.error("Failed to save doctor info", error=str(e))
            # Still save locally
            self.doctors[doctor_id] = doctor_info
            return doctor_id
    
    def get_doctor(self, doctor_id: str) -> Dict:
        """Get doctor details"""
        return self.doctors.get(doctor_id, {})
    
    def search_doctors(self, specialization: str = None, emergency: bool = False) -> List[Dict]:
        """Search doctors by specialization or emergency availability"""
        results = []
        for doctor in self.doctors.values():
            if specialization and specialization.lower() not in doctor['specialization'].lower():
                continue
            if emergency and not doctor['emergency_available']:
                continue
            results.append(doctor)
        return results
    
    def display_doctor(self, doctor: Dict):
        """Display doctor information"""
        print(f"\n{'='*60}")
        print(f"👨‍⚕️ {doctor['name']} ({doctor['id']})")
        print(f"{'='*60}")
        print(f"Specialization: {doctor['specialization']}")
        print(f"Qualifications: {doctor['qualifications']}")
        print(f"Experience: {doctor['experience']}")
        print(f"Hospital: {doctor['hospital']}")
        print(f"Phone: {doctor['phone']}")
        print(f"Email: {doctor['email']}")
        print(f"Available Days: {', '.join(doctor['available_days'])}")
        print(f"Available Times: {', '.join(doctor['available_times'])}")
        print(f"Consultation Fee: ₹{doctor['consultation_fee']}")
        print(f"Emergency Available: {'Yes ✓' if doctor['emergency_available'] else 'No ✗'}")
        print(f"Rating: {'⭐' * int(doctor['rating'])} ({doctor['rating']}/5)")
        print(f"{'='*60}\n")

# Appointment Management
class AppointmentSystem:
    def __init__(self):
        self.appointments = []
        self.appointment_counter = 1
        logger.info("Appointment system initialized")
    
    def book_appointment(self, patient_info: Dict, doctor_id: str, 
                        appointment_date: str, appointment_time: str, 
                        is_emergency: bool = False) -> Dict:
        """Book an appointment"""
        appointment = {
            'appointment_id': f"APT{str(self.appointment_counter).zfill(4)}",
            'patient_name': patient_info['name'],
            'patient_phone': patient_info['phone'],
            'patient_age': patient_info.get('age', 'N/A'),
            'symptoms': patient_info.get('symptoms', 'N/A'),
            'doctor_id': doctor_id,
            'appointment_date': appointment_date,
            'appointment_time': appointment_time,
            'is_emergency': is_emergency,
            'status': 'Emergency - Priority' if is_emergency else 'Scheduled',
            'booked_on': datetime.datetime.now().isoformat()
        }
        
        self.appointments.append(appointment)
        self.appointment_counter += 1
        logger.incr("appointments_booked")
        logger.info("Appointment booked", appointment_id=appointment['appointment_id'])
        # Persist appointment to Supabase if available
        if SUPABASE_AVAILABLE and supabase:
            try:
                supabase.table('appointments').insert(appointment).execute()
            except Exception as e:
                logger.error("Failed to persist appointment to Supabase", error=str(e))
        
        return appointment
    
    def display_appointment(self, appointment: Dict, doctor: Dict):
        """Display appointment confirmation"""
        print(f"\n{'='*60}")
        print("✅ APPOINTMENT CONFIRMED")
        print(f"{'='*60}")
        print(f"Appointment ID: {appointment['appointment_id']}")
        print(f"Patient: {appointment['patient_name']}")
        print(f"Phone: {appointment['patient_phone']}")
        print(f"Age: {appointment['patient_age']}")
        print(f"Symptoms: {appointment['symptoms']}")
        print(f"\nDoctor: {doctor['name']}")
        print(f"Specialization: {doctor['specialization']}")
        print(f"Hospital: {doctor['hospital']}")
        print(f"\nDate: {appointment['appointment_date']}")
        print(f"Time: {appointment['appointment_time']}")
        print(f"Status: {appointment['status']}")
        print(f"Consultation Fee: ₹{doctor['consultation_fee']}")
        
        if appointment['is_emergency']:
            print(f"\n⚠️ EMERGENCY APPOINTMENT - PRIORITY HANDLING")
        
        print(f"{'='*60}\n")


class MedicineReminder:
    def __init__(self):
        if not SUPABASE_AVAILABLE or not supabase:
            logger.error("Supabase is required for medicine reminders")
            raise Exception("Database connection required for medicine reminders")
        self.supabase = supabase

    def add_reminder(self, user_email: str, reminder: Dict):
        """Add medicine reminder to Supabase database"""
        try:
            # First, ensure the user exists (auto-create if needed)
            self._ensure_user_exists(user_email)
            
            # Now insert the reminder
            self.supabase.table('medicine_reminders').insert({
                'user_email': user_email,
                **reminder
            }).execute()
            logger.info("Reminder added", user_email=user_email, medicine=reminder.get('medicine_name'))
            return True
        except Exception as e:
            logger.error("Failed to add reminder", error=str(e))
            raise
    
    def _ensure_user_exists(self, user_email: str):
        """Ensure user exists in database, create if not"""
        try:
            # Check if user exists
            response = self.supabase.table('users').select('email').eq('email', user_email).execute()
            
            if not response.data or len(response.data) == 0:
                # User doesn't exist, create them
                import datetime
                username = user_email.split('@')[0]
                user_data = {
                    'email': user_email,
                    'name': f'User {username.capitalize()}',
                    'phone': f'98765{hash(user_email) % 100000:05d}',
                    'user_type': 'patient',
                    'registered_on': datetime.datetime.now().isoformat(),
                    'login_count': 0
                }
                self.supabase.table('users').insert(user_data).execute()
                logger.info("Auto-created user", email=user_email)
        except Exception as e:
            logger.error("Failed to ensure user exists", error=str(e))
            # Don't raise - let the original insert attempt proceed

    def get_reminders(self, user_email: str) -> List[Dict]:
        """Get medicine reminders from Supabase database"""
        try:
            resp = self.supabase.table('medicine_reminders').select('*').eq('user_email', user_email).execute()
            return resp.data or []
        except Exception as e:
            logger.error("Failed to get reminders", error=str(e))
            raise

    def add_reminder_console(self, user_email: str):
        print("\n➕ ADD MEDICINE REMINDER")
        name = input("Medicine name: ").strip()
        dosage = input("Dosage (e.g., 1 tablet): ").strip()
        time_str = input("Time (HH:MM, 24h): ").strip()
        start_date = input("Start date (YYYY-MM-DD): ").strip()
        end_date = input("End date (YYYY-MM-DD) or leave blank: ").strip()
        notes = input("Notes (optional): ").strip()

        reminder = {
            'medicine_name': name,
            'dosage': dosage,
            'time': time_str,
            'start_date': start_date,
            'end_date': end_date or None,
            'notes': notes
        }
        ok = self.add_reminder(user_email, reminder)
        if ok:
            print("✅ Reminder saved")
        else:
            print("❌ Failed to save reminder")

    def view_reminders_console(self, user_email: str):
        rems = self.get_reminders(user_email)
        if not rems:
            print("\nNo reminders found.")
            return
        print(f"\n📋 Reminders for {user_email} ({len(rems)}):")
        for i, r in enumerate(rems, 1):
            print(f"{i}. {r.get('medicine_name')} - {r.get('dosage')} at {r.get('time')} ({r.get('start_date')})")


class HealthMonitor:
    def __init__(self):
        if not SUPABASE_AVAILABLE or not supabase:
            logger.error("Supabase is required for health monitoring")
            raise Exception("Database connection required for health monitoring")
        self.supabase = supabase

    def add_record(self, user_email: str, record: Dict):
        """Add health record to Supabase database"""
        try:
            # First, ensure the user exists (auto-create if needed)
            self._ensure_user_exists(user_email)
            
            # Now insert the health record
            self.supabase.table('health_records').insert({
                'user_email': user_email,
                **record
            }).execute()
            logger.info("Health record added", user_email=user_email, date=record.get('date'))
            return True
        except Exception as e:
            logger.error("Failed to add health record", error=str(e))
            raise
    
    def _ensure_user_exists(self, user_email: str):
        """Ensure user exists in database, create if not"""
        try:
            # Check if user exists
            response = self.supabase.table('users').select('email').eq('email', user_email).execute()
            
            if not response.data or len(response.data) == 0:
                # User doesn't exist, create them
                import datetime
                username = user_email.split('@')[0]
                user_data = {
                    'email': user_email,
                    'name': f'User {username.capitalize()}',
                    'phone': f'98765{hash(user_email) % 100000:05d}',
                    'user_type': 'patient',
                    'registered_on': datetime.datetime.now().isoformat(),
                    'login_count': 0
                }
                self.supabase.table('users').insert(user_data).execute()
                logger.info("Auto-created user", email=user_email)
        except Exception as e:
            logger.error("Failed to ensure user exists", error=str(e))
            # Don't raise - let the original insert attempt proceed

    def get_history(self, user_email: str) -> List[Dict]:
        """Get health records from Supabase database"""
        try:
            resp = self.supabase.table('health_records').select('*').eq('user_email', user_email).order('date').execute()
            return resp.data or []
        except Exception as e:
            logger.error("Failed to get health records", error=str(e))
            raise

    def add_record_console(self, user_email: str):
        print("\n➕ ADD HEALTH RECORD")
        date = input("Date (YYYY-MM-DD) or leave blank for today: ").strip() or datetime.datetime.now().strftime('%Y-%m-%d')
        bp = input("Blood pressure (e.g., 120/80): ").strip()
        hr = input("Heart rate (bpm): ").strip()
        sugar = input("Sugar level (mg/dL): ").strip()
        weight = input("Weight (kg): ").strip()
        temp = input("Temperature (°C): ").strip()

        record = {
            'date': date,
            'blood_pressure': bp,
            'heart_rate': int(hr) if hr else None,
            'sugar_level': float(sugar) if sugar else None,
            'weight': float(weight) if weight else None,
            'temperature': float(temp) if temp else None
        }
        ok = self.add_record(user_email, record)
        if ok:
            print("✅ Health record saved")
        else:
            print("❌ Failed to save record")

    def view_history_console(self, user_email: str):
        records = self.get_history(user_email)
        if not records:
            print("\nNo health records found.")
            return
        print(f"\n📊 Health History for {user_email} ({len(records)} records):")
        for r in records[-20:]:
            print(f" - {r.get('date')}: HR={r.get('heart_rate')} BP={r.get('blood_pressure')} Sugar={r.get('sugar_level')}")

    def plot_heart_rate(self, user_email: str):
        records = self.get_history(user_email)
        if not records:
            print("No records to plot")
            return
        try:
            import matplotlib.pyplot as plt
        except Exception:
            print("matplotlib not available. Install it to see charts.")
            return

        dates = [r['date'] for r in records if r.get('heart_rate') is not None]
        rates = [r['heart_rate'] for r in records if r.get('heart_rate') is not None]
        if not dates:
            print("No heart rate data to plot")
            return
        plt.plot(dates, rates, marker='o')
        plt.title('Heart Rate Over Time')
        plt.xlabel('Date')
        plt.ylabel('BPM')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

# Hospital Locator
class HospitalLocator:
    def __init__(self):
        self.user_location = "Nanded, Maharashtra, India"
        logger.info("Hospital locator initialized")
    
    def set_location(self, location: str):
        """Set user location"""
        self.user_location = location
        logger.info("User location updated", location=location)
    
    def find_nearby_hospitals(self, emergency_type: str = None):
        """Find nearby hospitals and open in Google Maps"""
        search_query = f"hospitals near {self.user_location}"
        
        if emergency_type:
            if 'heart' in emergency_type.lower() or 'cardiac' in emergency_type.lower():
                search_query = f"cardiac hospitals near {self.user_location}"
            elif 'trauma' in emergency_type.lower() or 'accident' in emergency_type.lower():
                search_query = f"trauma centers near {self.user_location}"
            elif 'emergency' in emergency_type.lower():
                search_query = f"emergency hospitals near {self.user_location}"
        
        maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
        
        print(f"\n{'='*60}")
        print("🏥 FINDING NEARBY HOSPITALS")
        print(f"{'='*60}")
        print(f"Location: {self.user_location}")
        print(f"Search: {search_query}")
        print(f"\nOpening Google Maps in your browser...")
        print(f"Map URL: {maps_url}")
        print(f"{'='*60}\n")
        
        try:
            webbrowser.open(maps_url)
            logger.incr("maps_opened")
            return maps_url
        except Exception as e:
            logger.error("Failed to open maps", error=str(e))
            print(f"❌ Could not open browser. Please visit: {maps_url}")
            return maps_url
    
    def get_emergency_contacts(self):
        """Display emergency contact numbers"""
        print(f"\n{'='*60}")
        print("🚨 EMERGENCY CONTACTS")
        print(f"{'='*60}")
        print("Emergency (General): 112")
        print("Ambulance: 108 / 102")
        print("Police: 100")
        print("Fire: 101")
        print("Women Helpline: 1091")
        print("Child Helpline: 1098")
        print("National Emergency Number: 112")
        print(f"{'='*60}\n")

class MedicalDatabase:
    def __init__(self):
        self.disease_data = {}
        self.load_disease_data()
        
        if self.disease_data:
            self.create_training_data()
            logger.info("Medical database initialized", disease_count=len(self.disease_data))
        else:
            logger.error("Medical database empty - using fallback data")
            self.load_fallback_data()
            self.create_training_data()

    def load_disease_data(self):
        """Fetch disease data from Supabase"""
        # #region agent log
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            import json
            import time
            f.write(json.dumps({"sessionId":"debug-session","runId":"init","hypothesisId":"H","location":"main.py:492","message":"load_disease_data called","data":{"supabase_available":SUPABASE_AVAILABLE},"timestamp":int(time.time()*1000)})+'\n')
        # #endregion
        if not SUPABASE_AVAILABLE:
            return
        
        try:
            # #region agent log
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"init","hypothesisId":"H","location":"main.py:498","message":"Querying Supabase diseases table","data":{},"timestamp":int(time.time()*1000)})+'\n')
            # #endregion
            response = supabase.table('diseases').select("*").execute()
            # #region agent log
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"init","hypothesisId":"H","location":"main.py:501","message":"Supabase diseases query successful","data":{"disease_count":len(response.data) if response.data else 0},"timestamp":int(time.time()*1000)})+'\n')
            # #endregion
            for item in response.data:
                name = item.get('name')
                if name:
                    self.disease_data[name] = item
            logger.info("Diseases loaded from Supabase", count=len(self.disease_data))
        except Exception as e:
            # #region agent log
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"init","hypothesisId":"H","location":"main.py:509","message":"Failed to load diseases from Supabase","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":int(time.time()*1000)})+'\n')
            # #endregion
            logger.error("Failed to load diseases from Supabase", error=str(e))
    
    def load_fallback_data(self):
        """Load fallback disease data when database is unavailable"""
        self.disease_data = {
            'Common Cold': {
                'symptoms': ['runny nose', 'sneezing', 'sore throat', 'cough', 'mild fever'],
                'description': 'A viral infection of the upper respiratory tract',
                'treatment': 'Rest, fluids, over-the-counter cold medications',
                'severity': 'Mild',
                'duration': '7-10 days',
                'emergency': False
            },
            'Influenza': {
                'symptoms': ['high fever', 'severe body aches', 'headache', 'fatigue', 'dry cough'],
                'description': 'A contagious respiratory illness caused by influenza viruses',
                'treatment': 'Antiviral medications, rest, fluids',
                'severity': 'Moderate',
                'duration': '1-2 weeks',
                'emergency': False
            },
            'Dengue Fever': {
                'symptoms': ['high fever', 'severe headache', 'pain behind eyes', 'joint pain', 'rash'],
                'description': 'A mosquito-borne viral infection',
                'treatment': 'Supportive care, pain relief, hydration',
                'severity': 'Moderate to Severe',
                'duration': '5-7 days',
                'emergency': True
            },
            'Heart Attack': {
                'symptoms': ['chest pain', 'shortness of breath', 'nausea', 'cold sweat', 'arm pain'],
                'description': 'A medical emergency when blood flow to heart is blocked',
                'treatment': 'IMMEDIATE MEDICAL ATTENTION - Call 108',
                'severity': 'Critical',
                'duration': 'Emergency',
                'emergency': True
            },
            'Gastroenteritis': {
                'symptoms': ['diarrhea', 'nausea', 'vomiting', 'stomach cramps', 'mild fever'],
                'description': 'Inflammation of the digestive tract',
                'treatment': 'Oral rehydration, rest, bland diet',
                'severity': 'Mild to Moderate',
                'duration': '1-3 days',
                'emergency': False
            },
            'Migraine': {
                'symptoms': ['severe headache', 'nausea', 'sensitivity to light', 'visual disturbances'],
                'description': 'A neurological condition causing intense headaches',
                'treatment': 'Pain relief medications, rest in dark room',
                'severity': 'Moderate',
                'duration': '4-72 hours',
                'emergency': False
            },
            'Pneumonia': {
                'symptoms': ['cough with phlegm', 'fever', 'chest pain', 'difficulty breathing', 'fatigue'],
                'description': 'Infection that inflames air sacs in lungs',
                'treatment': 'Antibiotics, rest, fluids',
                'severity': 'Moderate to Severe',
                'duration': '1-3 weeks',
                'emergency': True
            }
        }
        logger.info("Loaded fallback disease data", count=len(self.disease_data))
       
    def create_training_data(self):
        """Create training dataset for KNN classifier"""
        all_symptoms = set()
        for disease_info in self.disease_data.values():
            all_symptoms.update(disease_info['symptoms'])
        
        self.all_symptoms = sorted(list(all_symptoms))
        
        X = []
        y = []
        
        for disease, info in self.disease_data.items():
            symptom_vector = [1 if symptom in info['symptoms'] else 0 
                            for symptom in self.all_symptoms]
            X.append(symptom_vector)
            y.append(disease)
        
        self.X_train = np.array(X)
        self.y_train = np.array(y)
        
        self.knn_model = KNeighborsClassifier(n_neighbors=min(3, len(self.y_train)))
        self.knn_model.fit(self.X_train, self.y_train)
        logger.info("KNN model trained", total_symptoms=len(self.all_symptoms))
    
    def get_disease_info(self, disease_name: str) -> Dict:
        """Get detailed information about a disease"""
        return self.disease_data.get(disease_name, {})
    
    def is_emergency(self, disease_name: str) -> bool:
        """Check if disease requires emergency care"""
        disease_info = self.disease_data.get(disease_name, {})
        return disease_info.get('emergency', False)

# Medical Diagnosis System
class MedicalDiagnosisSystem:
    def __init__(self):
        self.db = MedicalDatabase()
        self.doctor_profiles = DoctorProfile()
        self.appointment_system = AppointmentSystem()
        self.hospital_locator = HospitalLocator()
        self.auth_system = UserAuthSystem()
        # New services
        self.reminder = MedicineReminder()
        self.health_monitor = HealthMonitor()
        self.patient_history = []
        logger.info("Medical Diagnosis System initialized")
    
    def parse_symptoms(self, symptom_input: str) -> List[str]:
        """Parse symptom input from user"""
        # Remove quotation marks (both single and double) that users might accidentally include
        symptom_input = symptom_input.replace('"', '').replace("'", '')
        
        # Split by comma and clean up each symptom
        symptoms = [s.strip().lower() for s in symptom_input.split(',') if s.strip()]
        
        return symptoms
    
    def match_symptom(self, user_symptom: str, db_symptom: str) -> bool:
        """Check if user symptom matches database symptom (flexible matching)"""
        user_symptom = user_symptom.lower().strip()
        db_symptom = db_symptom.lower().strip()
        
        # Exact match
        if user_symptom == db_symptom:
            return True
        
        # Check if user symptom contains database symptom or vice versa
        if user_symptom in db_symptom or db_symptom in user_symptom:
            return True
        
        # Remove common modifiers for better matching
        modifiers = ['severe', 'mild', 'high', 'low', 'acute', 'chronic', 'dry', 'wet', 'with', 'without']
        user_clean = user_symptom
        db_clean = db_symptom
        
        for mod in modifiers:
            user_clean = user_clean.replace(mod, '').strip()
            db_clean = db_clean.replace(mod, '').strip()
        
        # Check if cleaned versions match
        if user_clean == db_clean:
            return True
        
        # Check if cleaned versions contain each other
        if user_clean in db_clean or db_clean in user_clean:
            return True
        
        return False
    
    def predict_disease(self, symptoms: List[str]) -> Dict:
        """Predict disease based on symptoms using KNN"""
        logger.info("Starting disease prediction", symptom_count=len(symptoms))
        
        # Create symptom vector with flexible matching
        symptom_vector = []
        matched_symptoms = []
        
        for db_symptom in self.db.all_symptoms:
            matched = False
            for user_symptom in symptoms:
                if self.match_symptom(user_symptom, db_symptom):
                    matched = True
                    if db_symptom not in matched_symptoms:
                        matched_symptoms.append(db_symptom)
                    break
            symptom_vector.append(1 if matched else 0)
        
        # If no symptoms matched, return error
        if sum(symptom_vector) == 0:
            logger.warning("No symptoms matched", user_symptoms=symptoms, available_symptoms=self.db.all_symptoms[:10])
            # Try to find best match using word overlap
            best_match_score = 0
            best_match_disease = None
            
            for disease, info in self.db.disease_data.items():
                disease_symptoms = [s.lower() for s in info['symptoms']]
                user_symptoms_lower = [s.lower() for s in symptoms]
                
                # Count word overlaps
                score = 0
                for user_sym in user_symptoms_lower:
                    for db_sym in disease_symptoms:
                        # Check for word-level matches
                        user_words = set(user_sym.split())
                        db_words = set(db_sym.split())
                        common_words = user_words.intersection(db_words)
                        if common_words:
                            score += len(common_words)
                
                if score > best_match_score:
                    best_match_score = score
                    best_match_disease = disease
            
            if best_match_disease:
                disease_info = self.db.get_disease_info(best_match_disease)
                return {
                    'primary_prediction': best_match_disease,
                    'confidence': 0.3,  # Low confidence due to poor match
                    'all_predictions': [{'disease': best_match_disease, 'confidence': 0.3}],
                    'matched_symptoms': [],
                    'is_emergency': self.db.is_emergency(best_match_disease)
                }
            else:
                # Default to first disease if nothing matches (shouldn't happen)
                first_disease = list(self.db.disease_data.keys())[0]
                disease_info = self.db.get_disease_info(first_disease)
                return {
                    'primary_prediction': first_disease,
                    'confidence': 0.1,
                    'all_predictions': [{'disease': first_disease, 'confidence': 0.1}],
                    'matched_symptoms': [],
                    'is_emergency': self.db.is_emergency(first_disease)
                }
        
        symptom_array = np.array(symptom_vector).reshape(1, -1)
        
        # Log the symptom vector for debugging
        logger.info("Symptom vector created", 
                   matched_count=sum(symptom_vector), 
                   total_symptoms=len(symptom_vector),
                   matched_symptoms=matched_symptoms[:5])
        
        prediction = self.db.knn_model.predict(symptom_array)[0]
        
        distances, indices = self.db.knn_model.kneighbors(symptom_array)
        confidence = 1 / (1 + distances[0][0]) if distances[0][0] > 0 else 1.0
        
        # Log prediction details
        logger.info("Disease predicted", 
                   disease=prediction, 
                   confidence=confidence,
                   distance=distances[0][0] if len(distances[0]) > 0 else 0)
        
        predictions_proba = []
        for idx in indices[0]:
            disease = self.db.y_train[idx]
            if disease not in [p['disease'] for p in predictions_proba]:
                dist_idx = list(indices[0]).index(idx)
                conf = 1 / (1 + distances[0][dist_idx]) if distances[0][dist_idx] > 0 else 1.0
                predictions_proba.append({
                    'disease': disease,
                    'confidence': round(conf, 2)
                })
        
        logger.incr("predictions_made")
        return {
            'primary_prediction': prediction,
            'confidence': round(confidence, 2),
            'all_predictions': predictions_proba[:3],
            'matched_symptoms': matched_symptoms,
            'is_emergency': self.db.is_emergency(prediction)
        }
    
    def get_gemini_analysis(self, symptoms: List[str], prediction: Dict) -> str:
        """Get AI-powered analysis from Gemini"""
        if not GEMINI_AVAILABLE or not model:
            return "AI analysis unavailable. Gemini API not configured."
        
        logger.info("Requesting Gemini analysis")
        
        disease_info = self.db.get_disease_info(prediction['primary_prediction'])
        
        prompt = f"""You are a medical AI assistant. Analyze the following patient case:

Patient Symptoms: {', '.join(symptoms)}

Predicted Diagnosis: {prediction['primary_prediction']}
Confidence: {prediction['confidence']*100}%
Emergency Status: {'YES - REQUIRES IMMEDIATE ATTENTION' if prediction['is_emergency'] else 'No'}

Disease Information from Database:
- Description: {disease_info.get('description', 'N/A')}
- Known Symptoms: {', '.join(disease_info.get('symptoms', []))}
- Treatment: {disease_info.get('treatment', 'N/A')}
- Severity: {disease_info.get('severity', 'N/A')}
- Duration: {disease_info.get('duration', 'N/A')}

Alternative Possibilities: {', '.join([p['disease'] for p in prediction['all_predictions'][1:]])}

Please provide:
1. Analysis of symptom match
2. Likelihood assessment
3. Additional symptoms to watch for
4. Recommended next steps
5. When to seek immediate medical attention

Keep the response concise and professional."""

        try:
            response = model.generate_content(prompt)
            logger.incr("gemini_calls_success")
            return response.text
        except Exception as e:
            logger.error("Gemini API error", error=str(e))
            logger.incr("gemini_calls_failed")
            return f"AI analysis unavailable: {str(e)}"
    
    def diagnose(self, symptom_input: str, user_type: str = "patient") -> Dict:
        """Main diagnosis function"""
        logger.info("New diagnosis request", user_type=user_type)
        # Require user login for AI diagnosis
        if not self.auth_system.current_user:
            return {"error": "Login required to access AI diagnosis"}

        symptoms = self.parse_symptoms(symptom_input)
        
        if not symptoms:
            return {"error": "No symptoms provided"}
        
        prediction = self.predict_disease(symptoms)
        disease_info = self.db.get_disease_info(prediction['primary_prediction'])
        ai_analysis = self.get_gemini_analysis(symptoms, prediction)
        
        result = {
            'timestamp': datetime.datetime.now().isoformat(),
            'user_type': user_type,
            'user_email': self.auth_system.current_user['email'] if self.auth_system.current_user else 'guest',
            'input_symptoms': symptoms,
            'matched_symptoms': prediction['matched_symptoms'],
            'unmatched_symptoms': [s for s in symptoms if s not in prediction['matched_symptoms']],
            'primary_diagnosis': {
                'disease': prediction['primary_prediction'],
                'confidence': prediction['confidence'],
                'info': disease_info,
                'is_emergency': prediction['is_emergency']
            },
            'alternative_diagnoses': prediction['all_predictions'][1:],
            'ai_analysis': ai_analysis
        }
        
        self.patient_history.append(result)
        
        return result
    
    def display_result(self, result: Dict):
        """Display diagnosis result in formatted way"""
        print("\n" + "="*80)
        print("MEDICAL DIAGNOSIS REPORT")
        print("="*80)
        print(f"\nTimestamp: {result['timestamp']}")
        print(f"User: {result.get('user_email', 'guest')}")
        print(f"User Type: {result['user_type']}")
        
        print(f"\n📋 INPUT SYMPTOMS:")
        for symptom in result['input_symptoms']:
            status = "✓" if symptom in result['matched_symptoms'] else "✗"
            print(f"  {status} {symptom}")
        
        diagnosis = result['primary_diagnosis']
        
        if diagnosis['is_emergency']:
            print(f"\n{'🚨'*30}")
            print("⚠️ EMERGENCY - IMMEDIATE MEDICAL ATTENTION REQUIRED!")
            print(f"{'🚨'*30}")
        
        print(f"\n🏥 PRIMARY DIAGNOSIS:")
        print(f"  Disease: {diagnosis['disease']}")
        print(f"  Confidence: {diagnosis['confidence']*100:.1f}%")
        
        if diagnosis['info']:
            print(f"\n  Description: {diagnosis['info'].get('description', 'N/A')}")
            print(f"  Severity: {diagnosis['info'].get('severity', 'N/A')}")
            print(f"  Duration: {diagnosis['info'].get('duration', 'N/A')}")
            print(f"  Treatment: {diagnosis['info'].get('treatment', 'N/A')}")
        
        if result['alternative_diagnoses']:
            print(f"\n🔍 ALTERNATIVE POSSIBILITIES:")
            for alt in result['alternative_diagnoses']:
                print(f"  • {alt['disease']} (Confidence: {alt['confidence']*100:.1f}%)")
        
        print(f"\n🤖 AI ANALYSIS:")
        print(result['ai_analysis'])
        
        print("\n" + "="*80)
        print("⚠️ DISCLAIMER: This is an AI-assisted diagnostic tool.")
        print("Always consult with a qualified healthcare professional for medical advice.")
        print("="*80 + "\n")

# Helper Functions
def handle_emergency(system, diagnosis_result=None):
    """Handle emergency situation"""
    print("\n" + "🚨"*30)
    print("EMERGENCY PROTOCOL ACTIVATED")
    print("🚨"*30)
    
    print("\n1. 📞 Call emergency services (112/108)")
    print("2. 🏥 Find nearest hospital")
    print("3. 👨‍⚕️ Book emergency appointment")
    print("4. ℹ️ View emergency contacts")
    
    choice = input("\nWhat would you like to do? (1-4): ").strip()
    
    if choice == '1':
        system.hospital_locator.get_emergency_contacts()
    elif choice == '2':
        system.hospital_locator.find_nearby_hospitals('emergency')
    elif choice == '3':
        book_emergency_appointment(system, diagnosis_result)
    elif choice == '4':
        system.hospital_locator.get_emergency_contacts()


def require_login(system) -> bool:
    """Simple guard used to require user login for sensitive actions."""
    if not system.auth_system.current_user:
        print("\n❌ Login required. Please login from Account Management.")
        return False
    return True

def search_doctors_menu(system):
    """Search doctors by criteria"""
    print("\n🔍 SEARCH DOCTORS")
    print("1. Search by specialization")
    print("2. Search emergency available doctors")
    print("3. View all doctors")
    
    choice = input("\nSelect (1-3): ").strip()
    
    if choice == '1':
        spec = input("Enter specialization: ").strip()
        doctors = system.doctor_profiles.search_doctors(specialization=spec)
        if doctors:
            print(f"\n✅ Found {len(doctors)} doctor(s):")
            for doctor in doctors:
                system.doctor_profiles.display_doctor(doctor)
        else:
            print("\n❌ No doctors found with that specialization.")
    
    elif choice == '2':
        doctors = system.doctor_profiles.search_doctors(emergency=True)
        if doctors:
            print(f"\n✅ Found {len(doctors)} emergency available doctor(s):")
            for doctor in doctors:
                system.doctor_profiles.display_doctor(doctor)
        else:
            print("\n❌ No emergency doctors available.")
    
    elif choice == '3':
        for doctor in system.doctor_profiles.doctors.values():
            system.doctor_profiles.display_doctor(doctor)

def book_appointment_menu(system):
    """Book appointment with doctor"""
    if not system.auth_system.current_user:
        print("\n❌ Please login first to book appointment!")
        return
    
    print("\n📅 BOOK APPOINTMENT")
    
    patient_info = {
        'name': system.auth_system.current_user['name'],
        'phone': system.auth_system.current_user['phone']
    }
    
    patient_info['age'] = input("Age: ").strip()
    patient_info['symptoms'] = input("Symptoms (brief): ").strip()
    
    print("\n👨‍⚕️ AVAILABLE DOCTORS:")
    doctors = list(system.doctor_profiles.doctors.values())
    for i, doctor in enumerate(doctors, 1):
        print(f"{i}. {doctor['name']} - {doctor['specialization']}")
        print(f"   Available: {', '.join(doctor['available_days'])}")
        print(f"   Fee: ₹{doctor['consultation_fee']}")
        print()
    
    doc_choice = input("Select doctor number: ").strip()
    try:
        doctor_idx = int(doc_choice) - 1
        if 0 <= doctor_idx < len(doctors):
            doctor = doctors[doctor_idx]
            
            appointment_date = input("Appointment Date (DD/MM/YYYY): ").strip()
            appointment_time = input("Preferred Time: ").strip()
            
            appointment = system.appointment_system.book_appointment(
                patient_info, doctor['id'], appointment_date, appointment_time, False
            )
            
            system.appointment_system.display_appointment(appointment, doctor)
        else:
            print("\n❌ Invalid doctor selection!")
    except ValueError:
        print("\n❌ Invalid input!")

def book_emergency_appointment(system, diagnosis_result=None):
    """Book emergency appointment"""
    if not system.auth_system.current_user:
        print("\n❌ Please login first!")
        return
    
    print("\n🚨 EMERGENCY APPOINTMENT BOOKING")
    
    patient_info = {
        'name': system.auth_system.current_user['name'],
        'phone': system.auth_system.current_user['phone']
    }
    
    patient_info['age'] = input("Age: ").strip()
    
    if diagnosis_result:
        patient_info['symptoms'] = ', '.join(diagnosis_result['input_symptoms'])
    else:
        patient_info['symptoms'] = input("Emergency Symptoms: ").strip()
    
    emergency_doctors = system.doctor_profiles.search_doctors(emergency=True)
    
    if not emergency_doctors:
        print("\n❌ No emergency doctors available. Please call 108 for ambulance!")
        system.hospital_locator.get_emergency_contacts()
        return
    
    print(f"\n🚨 EMERGENCY DOCTORS AVAILABLE ({len(emergency_doctors)}):")
    for i, doctor in enumerate(emergency_doctors, 1):
        print(f"{i}. {doctor['name']} - {doctor['specialization']}")
        print(f"   Hospital: {doctor['hospital']}")
        print(f"   Phone: {doctor['phone']}")
        print()
    
    doc_choice = input("Select doctor number (or press Enter for first available): ").strip()
    
    try:
        if doc_choice:
            doctor_idx = int(doc_choice) - 1
        else:
            doctor_idx = 0
        
        if 0 <= doctor_idx < len(emergency_doctors):
            doctor = emergency_doctors[doctor_idx]
            
            today = datetime.datetime.now().strftime("%d/%m/%Y")
            
            appointment = system.appointment_system.book_appointment(
                patient_info, doctor['id'], today, "ASAP", True
            )
            
            system.appointment_system.display_appointment(appointment, doctor)
            
            print("\n⚠️ IMPORTANT:")
            print("1. If symptoms worsen, call 108 immediately")
            print("2. Keep patient comfortable and monitor vitals")
            print("3. Have medical records ready")
            
            show_map = input("\nShow nearest hospital location? (yes/no): ").strip().lower()
            if show_map == 'yes':
                system.hospital_locator.find_nearby_hospitals('emergency')
        else:
            print("\n❌ Invalid selection!")
    except ValueError:
        print("\n❌ Invalid input!")

# Doctor registration removed: doctors are managed via Supabase dashboard (read-only in app)

def display_statistics(system):
    """Display system statistics"""
    print("\n" + "="*60)
    print("📊 SYSTEM STATISTICS")
    print("="*60)
    
    stats = logger.dump()
    
    print(f"\nMetrics:")
    for metric, count in stats['metrics'].items():
        print(f"  • {metric}: {count}")
    
    print(f"\nDatabase Stats:")
    print(f"  • Total Diseases: {len(system.db.disease_data)}")
    print(f"  • Total Symptoms: {len(system.db.all_symptoms)}")
    print(f"  • Emergency Conditions: {sum(1 for d in system.db.disease_data.values() if d['emergency'])}")
    
    print(f"\nDoctor Stats:")
    print(f"  • Total Doctors: {len(system.doctor_profiles.doctors)}")
    print(f"  • Emergency Available: {len(system.doctor_profiles.search_doctors(emergency=True))}")
    
    print(f"\nAppointment Stats:")
    print(f"  • Total Appointments: {len(system.appointment_system.appointments)}")
    emergency_apts = sum(1 for a in system.appointment_system.appointments if a['is_emergency'])
    print(f"  • Emergency Appointments: {emergency_apts}")
    
    print(f"\nPatient Stats:")
    print(f"  • Total Diagnoses: {len(system.patient_history)}")
    emergency_diagnoses = sum(1 for d in system.patient_history if d['primary_diagnosis']['is_emergency'])
    print(f"  • Emergency Diagnoses: {emergency_diagnoses}")
    
    print(f"\nUser Stats:")
    print(f"  • Total Registered Users: {len(system.auth_system.users)}")
    if system.auth_system.current_user:
        print(f"  • Current User: {system.auth_system.current_user['name']}")
        print(f"  • Login Count: {system.auth_system.current_user.get('login_count', 0)}")
    
    print("="*60)

def patient_menu(system):
    """Patient services menu"""
    while True:
        print("\n" + "="*60)
        print("PATIENT SERVICES")
        print("="*60)
        if system.auth_system.current_user:
            print(f"Logged in as: {system.auth_system.current_user['name']}")
        print("="*60)
        print("1. Enter symptoms for diagnosis")
        print("2. View available symptoms")
        print("3. Search doctors")
        print("4. Book appointment")
        print("5. Medicine Reminders")
        print("6. Health Monitoring")
        print("7. View my diagnosis history")
        print("8. Back to main menu")
        print("="*60)

        choice = input("\nSelect option (1-8): ").strip()

        if choice == '1':
            print("\nEnter symptoms separated by commas:")
            print("Example: fever, cough, headache, fatigue")
            symptoms = input("Symptoms: ").strip()

            if symptoms:
                result = system.diagnose(symptoms, 'patient')
                if 'error' in result:
                    print(f"\n❌ Error: {result['error']}")
                else:
                    system.display_result(result)

                    if result['primary_diagnosis']['is_emergency']:
                        print("\n🚨 THIS IS A MEDICAL EMERGENCY!")
                        emergency_response = input("\nDo you want to access emergency services? (yes/no): ").strip().lower()
                        if emergency_response == 'yes':
                            handle_emergency(system, result)
            else:
                print("\n❌ No symptoms entered!")

        elif choice == '2':
            print("\n📊 AVAILABLE SYMPTOMS IN DATABASE:")
            for i, symptom in enumerate(system.db.all_symptoms, 1):
                print(f"  {i}. {symptom}")
                if i % 20 == 0:
                    cont = input("\nPress Enter to continue or 'q' to quit: ")
                    if cont.lower() == 'q':
                        break

        elif choice == '3':
            search_doctors_menu(system)

        elif choice == '4':
            if not require_login(system):
                continue
            book_appointment_menu(system)

        elif choice == '5':
            if not require_login(system):
                continue
            print("\nMedicine Reminders")
            print("1. Add reminder")
            print("2. View reminders")
            mr_choice = input("Choose (1-2): ").strip()
            if mr_choice == '1':
                system.reminder.add_reminder_console(system.auth_system.current_user['email'])
            elif mr_choice == '2':
                system.reminder.view_reminders_console(system.auth_system.current_user['email'])

        elif choice == '6':
            if not require_login(system):
                continue
            print("\nHealth Monitoring")
            print("1. Add health record")
            print("2. View history")
            print("3. Plot heart rate")
            hm_choice = input("Choose (1-3): ").strip()
            if hm_choice == '1':
                system.health_monitor.add_record_console(system.auth_system.current_user['email'])
            elif hm_choice == '2':
                system.health_monitor.view_history_console(system.auth_system.current_user['email'])
            elif hm_choice == '3':
                system.health_monitor.plot_heart_rate(system.auth_system.current_user['email'])

        elif choice == '7':
            if system.patient_history:
                user_history = [r for r in system.patient_history 
                              if r.get('user_email') == system.auth_system.current_user['email']] if system.auth_system.current_user else system.patient_history
                
                if user_history:
                    print(f"\n📚 DIAGNOSIS HISTORY ({len(user_history)} records):")
                    for i, record in enumerate(user_history[-10:], 1):
                        print(f"\n  {i}. {record['timestamp']}")
                        print(f"     Diagnosis: {record['primary_diagnosis']['disease']}")
                        print(f"     Confidence: {record['primary_diagnosis']['confidence']*100:.1f}%")
                        print(f"     Emergency: {'Yes ⚠️' if record['primary_diagnosis']['is_emergency'] else 'No'}")
                else:
                    print("\n📚 No diagnosis history yet.")
            else:
                print("\n📚 No diagnosis history yet.")

        elif choice == '8':
            break
        else:
            print("\n❌ Invalid option!")

# Doctor menu removed: doctors are managed via Supabase dashboard

def emergency_menu(system):
    """Emergency services menu"""
    print("\n" + "="*60)
    print("🚨 EMERGENCY SERVICES")
    print("="*60)
    print("1. Find nearest hospital (Google Maps)")
    print("2. Emergency contact numbers")
    print("3. Book emergency appointment")
    print("4. Emergency symptoms check")
    print("5. Back to main menu")
    print("="*60)
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == '1':
        location = input("\nEnter your location (or press Enter for default): ").strip()
        if location:
            system.hospital_locator.set_location(location)
        
        emergency_type = input("Emergency type (heart/trauma/general or press Enter): ").strip()
        system.hospital_locator.find_nearby_hospitals(emergency_type if emergency_type else None)
    
    elif choice == '2':
        system.hospital_locator.get_emergency_contacts()
    
    elif choice == '3':
        book_emergency_appointment(system)
    
    elif choice == '4':
        print("\nEnter your symptoms:")
        symptoms = input("Symptoms: ").strip()
        if symptoms:
            result = system.diagnose(symptoms, 'emergency_patient')
            if 'error' not in result:
                system.display_result(result)
                if result['primary_diagnosis']['is_emergency']:
                    handle_emergency(system, result)
    
    elif choice == '5':
        return
    else:
        print("\n❌ Invalid option!")

def account_menu(system):
    """Account management menu"""
    while True:
        print("\n" + "="*60)
        print("👤 ACCOUNT MANAGEMENT")
        print("="*60)
        if system.auth_system.current_user:
            user = system.auth_system.current_user
            print(f"\nCurrent User: {user['name']}")
            print(f"Email: {user['email']}")
            print(f"Phone: {user['phone']}")
            print(f"User Type: {user['user_type']}")
            print(f"Login Count: {user.get('login_count', 0)}")
        else:
            print("\nNo user logged in")
        print("="*60)
        print("1. 🔐 Google Login")
        print("2. 🔄 Switch Account")
        print("3. ✏️ Update Profile")
        print("4. 👋 Logout")
        print("5. ⬅️ Back to Main Menu")
        print("="*60)
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            if system.auth_system.current_user:
                print("\n⚠️ Already logged in!")
                switch = input("Switch to different account? (yes/no): ").strip().lower()
                if switch == 'yes':
                    system.auth_system.google_login_simulation()
            else:
                system.auth_system.google_login_simulation()
        
        elif choice == '2':
            system.auth_system.switch_account()
        
        elif choice == '3':
            system.auth_system.update_profile()
        
        elif choice == '4':
            system.auth_system.logout()
        
        elif choice == '5':
            break
        else:
            print("\n❌ Invalid option!")

# Main Application
def main():
    print("="*80)
    print("COMPREHENSIVE MEDICAL DIAGNOSIS & EMERGENCY SYSTEM")
    print("With Google Login Integration")
    print("="*80)
    
    system = MedicalDiagnosisSystem()
    
    # Prompt for login
    print("\n👋 Welcome to Medical Diagnosis System!")
    login_choice = input("\nWould you like to login with Google? (yes/no): ").strip().lower()
    if login_choice == 'yes':
        system.auth_system.google_login_simulation()
    
    while True:
        print("\n" + "="*80)
        print("MAIN MENU")
        print("="*80)
        if system.auth_system.current_user:
            print(f"👤 Logged in as: {system.auth_system.current_user['name']}")
        else:
            print("👤 Not logged in (Guest mode)")
        print("="*80)
        print("1. 🩺 Patient Services")
        print("2. 🚨 Emergency Services")
        print("3. 👤 Account Management")
        print("4. 📊 View System Statistics")
        print("5. 🚪 Exit")
        print("="*80)
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            patient_menu(system)
        elif choice == '2':
            emergency_menu(system)
        elif choice == '3':
            account_menu(system)
        elif choice == '4':
            display_statistics(system)
        elif choice == '5':
            print("\n👋 Thank you for using Medical Diagnosis System!")
            print("\n📊 Session Statistics:")
            stats = logger.dump()
            for metric, count in stats['metrics'].items():
                print(f"  • {metric}: {count}")
            
            if system.auth_system.current_user:
                logout = input("\nLogout before exiting? (yes/no): ").strip().lower()
                if logout == 'yes':
                    system.auth_system.logout()
            break
        else:
            print("\n❌ Invalid option! Please select 1-6.")

if __name__ == "__main__":
    main()
