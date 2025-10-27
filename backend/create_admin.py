"""
Create admin user for ABIS system
Usage: python create_admin.py
"""

import sys
import os
from getpass import getpass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import engine, get_db
from app.models.user import User
from app.utils.security import get_password_hash

def create_admin_user(
    username: str,
    email: str,
    full_name: str,
    password: str
):
    """Create an admin user"""
    db = next(get_db())
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print(f"❌ User with username '{username}' or email '{email}' already exists!")
            return False
        
        # Create user
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role="admin",
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ Admin user created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Role: admin")
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    print("=" * 50)
    print("ABIS - Create Admin User")
    print("=" * 50)
    print()
    
    # Get user input
    print("Enter admin user details:")
    print()
    
    username = input("Username: ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        sys.exit(1)
    
    email = input("Email: ").strip()
    if not email:
        print("❌ Email cannot be empty!")
        sys.exit(1)
    
    full_name = input("Full Name: ").strip()
    if not full_name:
        print("❌ Full name cannot be empty!")
        sys.exit(1)
    
    password = getpass("Password: ")
    if not password:
        print("❌ Password cannot be empty!")
        sys.exit(1)
    
    password_confirm = getpass("Confirm Password: ")
    if password != password_confirm:
        print("❌ Passwords do not match!")
        sys.exit(1)
    
    if len(password) < 6:
        print("❌ Password must be at least 6 characters!")
        sys.exit(1)
    
    print()
    print("Creating admin user...")
    
    success = create_admin_user(username, email, full_name, password)
    
    if success:
        print()
        print("=" * 50)
        print("You can now login with these credentials:")
        print(f"  Username: {username}")
        print(f"  Password: ********")
        print("=" * 50)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
