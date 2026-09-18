"""
Authentication Service.
Handles NIST-compliant PBKDF2-HMAC-SHA256 password hashing with salt and JWT session tokens.
"""

import os
import hmac
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

import jwt

JWT_SECRET = os.getenv("JWT_SECRET", "oral-ai-secure-screening-secret-key-2026-fallback")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days


def hash_password(password: str) -> str:
    """
    Hashes a plaintext password using PBKDF2-HMAC-SHA256 with a secure 16-byte random salt.
    Format: pbkdf2_sha256$100000$<salt_hex>$<hash_hex>
    """
    salt = secrets.token_bytes(16)
    iterations = 100_000
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${derived.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifies a plaintext password against a stored hash using constant-time comparison.
    """
    try:
        parts = password_hash.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_derived = bytes.fromhex(parts[3])

        computed_derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(expected_derived, computed_derived)
    except Exception:
        return False


def create_access_token(user_id: str, email: str, name: str) -> str:
    """
    Creates a signed JWT access token.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes and validates a JWT access token.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        return None
