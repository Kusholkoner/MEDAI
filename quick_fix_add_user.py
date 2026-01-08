"""
Quick Fix: Add Missing User to Database
This script adds the user test34@gmail.com to the database
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def add_user():
    """Add test34@gmail.com to the database"""
    email = "test34@gmail.com"
    
    # Check if user already exists
    try:
        response = supabase.table('users').select('*').eq('email', email).execute()
        if len(response.data) > 0:
            print(f"User already exists: {email}")
            print(f"   Name: {response.data[0]['name']}")
            print(f"   Phone: {response.data[0]['phone']}")
            return True
    except Exception as e:
        print(f"Error checking user: {e}")
    
    # Create user - without password_hash if column doesn't exist
    try:
        user_data = {
            'email': email,
            'name': 'Test User 34',
            'phone': '9876543210',
            'user_type': 'patient',
            'registered_on': datetime.now().isoformat(),
            'login_count': 0
        }
        
        supabase.table('users').insert(user_data).execute()
        
        print("=" * 80)
        print("USER CREATED SUCCESSFULLY")
        print("=" * 80)
        print(f"Email: {email}")
        print(f"Name: {user_data['name']}")
        print(f"Phone: {user_data['phone']}")
        print("=" * 80)
        print("\nYou can now:")
        print("1. Add medicine reminders")
        print("2. Add health records")
        print("\nAll foreign key constraint errors should be resolved.")
        
        return True
        
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("QUICK FIX: Adding test34@gmail.com to database")
    print("=" * 80)
    add_user()
