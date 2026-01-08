"""
Fix User Registration Issue
This script helps diagnose and fix foreign key constraint violations
by ensuring users exist in the database before adding related records.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def check_user_exists(email: str) -> bool:
    """Check if a user exists in the database"""
    try:
        response = supabase.table('users').select('*').eq('email', email).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return False

def create_user(email: str, name: str, phone: str):
    """Create a user in the database"""
    try:
        import bcrypt
        from datetime import datetime
        
        # Create a default password hash (user should change this)
        default_password = "changeme123"
        password_hash = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user_data = {
            'email': email,
            'name': name,
            'phone': phone,
            'password_hash': password_hash,
            'user_type': 'patient',
            'registered_on': datetime.now().isoformat(),
            'login_count': 0
        }
        
        supabase.table('users').insert(user_data).execute()
        print(f"✅ User created successfully: {email}")
        print(f"⚠️  Default password: {default_password}")
        print(f"⚠️  User should change password after first login")
        return True
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

def list_users():
    """List all users in the database"""
    try:
        response = supabase.table('users').select('email, name, phone, registered_on').execute()
        if response.data:
            print(f"\n📋 Found {len(response.data)} users:")
            for user in response.data:
                print(f"  - {user['email']} ({user['name']}) - Registered: {user.get('registered_on', 'N/A')}")
        else:
            print("\n⚠️  No users found in database")
        return response.data
    except Exception as e:
        print(f"❌ Error listing users: {e}")
        return []

def main():
    print("=" * 80)
    print("USER REGISTRATION FIX TOOL")
    print("=" * 80)
    
    while True:
        print("\nOptions:")
        print("1. Check if a user exists")
        print("2. Create a new user")
        print("3. List all users")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            email = input("Enter email to check: ").strip()
            if check_user_exists(email):
                print(f"✅ User exists: {email}")
            else:
                print(f"❌ User does not exist: {email}")
                create_new = input("Would you like to create this user? (y/n): ").strip().lower()
                if create_new == 'y':
                    name = input("Enter name: ").strip()
                    phone = input("Enter phone: ").strip()
                    create_user(email, name, phone)
        
        elif choice == "2":
            email = input("Enter email: ").strip()
            if check_user_exists(email):
                print(f"⚠️  User already exists: {email}")
            else:
                name = input("Enter name: ").strip()
                phone = input("Enter phone: ").strip()
                create_user(email, name, phone)
        
        elif choice == "3":
            list_users()
        
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()
