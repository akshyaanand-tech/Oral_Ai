"""
Authentication Routes.
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
POST /api/auth/forgot-password
"""

import uuid
import re
import logging
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from fastapi import APIRouter, HTTPException, status, Header

from app.services.db import create_user, get_user_by_email, get_user_by_id
from app.services.auth_service import hash_password, verify_password, create_access_token, decode_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of user")
    email: str = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 chars)")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if not EMAIL_REGEX.match(v_clean):
            raise ValueError("Invalid email format.")
        return v_clean


class LoginRequest(BaseModel):
    email: str = Field(..., description="Registered email address")
    password: str = Field(..., min_length=1, description="Password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if not EMAIL_REGEX.match(v_clean):
            raise ValueError("Invalid email format.")
        return v_clean


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., description="Registered email address")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if not EMAIL_REGEX.match(v_clean):
            raise ValueError("Invalid email format.")
        return v_clean


class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str


class AuthResponse(BaseModel):
    user: UserResponse
    token: str
    message: str


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new patient user",
)
async def register_user(payload: RegisterRequest):
    email_clean = payload.email.strip().lower()
    name_clean = payload.name.strip()

    # Password validation: minimum 8 chars, mixed letters and digits
    if len(payload.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long.",
        )
    if not any(c.isdigit() for c in payload.password) or not any(c.isalpha() for c in payload.password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain both letters and numbers.",
        )

    # Check for existing email
    existing = get_user_by_email(email_clean)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please sign in.",
        )

    user_id = f"usr_{uuid.uuid4().hex[:10]}"
    pwd_hash = hash_password(payload.password)
    user_record = create_user(
        user_id=user_id,
        name=name_clean,
        email=email_clean,
        password_hash=pwd_hash,
    )

    token = create_access_token(user_id=user_id, email=email_clean, name=name_clean)
    logger.info("Registered new user '%s' (%s)", user_id, email_clean)

    return AuthResponse(
        user=UserResponse(user_id=user_id, name=name_clean, email=email_clean),
        token=token,
        message="Registration successful. Welcome to OralScreen AI!",
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Sign in with email and password",
)
async def login_user(payload: LoginRequest):
    email_clean = payload.email.strip().lower()
    user = get_user_by_email(email_clean)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please check your credentials.",
        )

    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please check your credentials.",
        )

    token = create_access_token(
        user_id=user["user_id"],
        email=user["email"],
        name=user["name"],
    )
    logger.info("User '%s' logged in successfully", user["user_id"])

    return AuthResponse(
        user=UserResponse(user_id=user["user_id"], name=user["name"], email=user["email"]),
        token=token,
        message="Sign in successful. Welcome back!",
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
)
async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header with Bearer token is required.",
        )

    token = authorization.split("Bearer ")[1].strip()
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or token is invalid. Please sign in again.",
        )

    user = get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account no longer exists.",
        )

    return UserResponse(
        user_id=user["user_id"],
        name=user["name"],
        email=user["email"],
    )


@router.post(
    "/forgot-password",
    summary="Initiate password reset flow",
)
async def forgot_password(payload: ForgotPasswordRequest):
    email_clean = payload.email.strip().lower()
    # Standard security protocol: return identical message whether email exists or not
    return {
        "message": f"If an account associated with {email_clean} exists, password reset instructions have been dispatched.",
        "email": email_clean,
    }
