import hashlib
import hmac
import sqlite3
from datetime import datetime, timedelta
import json
import base64
from typing import Optional

from config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_db_connection

# Simple JWT implementation without external dependencies
def create_access_token(data: dict, expires_delta: timedelta = None):
    """Simple JWT token creation"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        **data,
        "exp": expire.timestamp()
    }
    
    # Encode header
    header = json.dumps({"alg": "HS256", "typ": "JWT"}).encode()
    header_b64 = base64.urlsafe_b64encode(header).decode()
    
    # Encode payload
    payload_json = json.dumps(payload).encode()
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode()
    
    # Create signature
    message = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode()
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def verify_token(token: str):
    """Simple JWT token verification"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
            
        header_b64, payload_b64, signature_b64 = parts
        
        # Verify signature
        message = f"{header_b64}.{payload_b64}".encode()
        expected_signature = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).digest()
        expected_signature_b64 = base64.urlsafe_b64encode(expected_signature).decode()
        
        if not hmac.compare_digest(signature_b64, expected_signature_b64):
            return None
        
        # Check expiration
        payload_json = base64.urlsafe_b64decode(payload_b64 + '==')  # Add padding
        payload = json.loads(payload_json)
        
        if datetime.utcnow().timestamp() > payload['exp']:
            return None
            
        return payload
    except Exception:
        return None

def get_password_hash(password: str) -> str:
    """Simple password hashing using SHA-256 (for demo purposes)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return get_password_hash(plain_password) == hashed_password

def authenticate_user(username: str, password: str):
    """Authenticate a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, hashed_password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return False
    
    user_id, username, hashed_password = user
    if not verify_password(password, hashed_password):
        return False
    
    return {"user_id": user_id, "username": username}

def register_user(username: str, email: str, password: str):
    """Register a new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        hashed_password = get_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
            (username, email, hashed_password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_username(username: str):
    """Get user by username"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, email FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {"id": user[0], "username": user[1], "email": user[2]}
    return None