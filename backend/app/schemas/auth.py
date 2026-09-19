"""Pydantic schemas for Authentication."""

import re
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class SignupRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of user")
    email: str = Field(..., min_length=5, max_length=255, description="Valid email address")
    password: str = Field(..., min_length=6, max_length=128, description="User password (min 6 characters)")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("Name must be at least 2 characters")
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        cleaned = v.strip().lower()
        # Clean RFC-compliant email regex
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", cleaned):
            raise ValueError("Invalid email format")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must contain at least 6 characters")
        return v


class LoginRequest(BaseModel):
    email: str = Field(..., description="User registered email")
    password: str = Field(..., description="User password")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UserSummary(BaseModel):
    id: str
    name: str
    email: str
    interests: List[str] = []
    onboarding_completed: bool = False
    created_at: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSummary
