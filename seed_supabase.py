"""Seed Supabase with minimal test data: one doctor and one disease.
Run with: python seed_supabase.py
Requires SUPABASE_URL and SUPABASE_KEY in the environment or .env
"""
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from supabase import create_client
except Exception as e:
    print("supabase client not installed:", e)
    raise

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise SystemExit('Please set SUPABASE_URL and SUPABASE_KEY in environment')

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

# Insert a test doctor
doctor = {
    'id': 'DR001',
    'name': 'Dr. Test Doctor',
    'specialization': 'General Physician',
    'qualifications': 'MBBS',
    'experience': '10 years',
    'phone': '+1-555-0000',
    'email': 'test.doctor@example.com',
    'hospital': 'Test Hospital',
    'available_days': ['Monday', 'Wednesday', 'Friday'],
    'available_times': ['09:00-12:00', '14:00-17:00'],
    'consultation_fee': 300,
    'emergency_available': True,
    'rating': 4.2
}

# Insert a test disease
disease = {
    'name': 'Test Fever',
    'symptoms': ['fever', 'chills', 'headache'],
    'description': 'A test disease for development',
    'treatment': 'Rest and fluids',
    'severity': 'Mild',
    'duration': '3-5 days',
    'emergency': False
}

print('Seeding doctor...')
try:
    sb.table('doctors').upsert(doctor).execute()
    print('Doctor seeded')
except Exception as e:
    print('Failed to seed doctor:', e)

print('Seeding disease...')
try:
    # ensure disease table has a unique constraint on name in Supabase
    sb.table('diseases').upsert(disease).execute()
    print('Disease seeded')
except Exception as e:
    print('Failed to seed disease:', e)

print('Seeding complete')
