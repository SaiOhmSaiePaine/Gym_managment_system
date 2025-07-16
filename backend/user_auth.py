#!/usr/bin/env python3
"""
User authentication utilities for the Lost & Found Campus API
"""

import json
import hashlib
import uuid
from datetime import datetime

USER_DATABASE_FILE = "user_db.json"

def hash_password(password):
    """Create a SHA-256 hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, password):
    """Verify password against stored hash"""
    return stored_hash == hash_password(password)

def load_users():
    """Load users from JSON file or return empty list if file doesn't exist"""
    try:
        with open(USER_DATABASE_FILE, 'r') as f:
            users = json.load(f)
            print(f"👥 Loaded {len(users)} users from database")
            return users
    except FileNotFoundError:
        print("👥 No user database file found, creating empty user database")
        save_users([])
        return []
    except Exception as e:
        print(f"❌ Error loading user database: {e}")
        return []

def save_users(users):
    """Save users to JSON file"""
    try:
        with open(USER_DATABASE_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        print(f"💾 Saved {len(users)} users to database")
    except Exception as e:
        print(f"❌ Error saving user database: {e}")

def find_user_by_email(users, email):
    """Find a user by email"""
    for user in users:
        if user["email"] == email:
            return user
    return None

def create_user(name, email, password):
    """Create a new user"""
    # Load existing users
    users = load_users()
    
    # Check if email already exists
    if find_user_by_email(users, email):
        return None, "Email already exists"
    
    # Create new user
    new_user = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "password_hash": hash_password(password),
        "created_at": datetime.now().isoformat()
    }
    
    # Add to users list and save
    users.append(new_user)
    save_users(users)
    
    # Return user without password hash
    user_data = new_user.copy()
    user_data.pop("password_hash")
    
    return user_data, None

def authenticate_user(email, password):
    """Authenticate a user with email and password"""
    users = load_users()
    user = find_user_by_email(users, email)
    
    if not user:
        return None, "User not found"
    
    if not verify_password(user["password_hash"], password):
        return None, "Invalid password"
    
    # Return user without password hash
    user_data = user.copy()
    user_data.pop("password_hash")
    
    return user_data, None

def get_user_by_id(user_id):
    """Get user data by ID (excluding password hash)"""
    users = load_users()
    
    for user in users:
        if user["id"] == user_id:
            user_data = user.copy()
            user_data.pop("password_hash")
            return user_data
    
    return None

# Initialize users on module import
users = load_users()
