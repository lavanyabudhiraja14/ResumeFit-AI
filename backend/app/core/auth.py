"""Authentication, Password Hashing, and JWT/Token Utilities."""

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a unique random salt."""
    salt = secrets.token_hex(16)
    iterations = 100_000
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return f"{salt}${iterations}${hash_bytes.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored PBKDF2 hash."""
    try:
        parts = hashed_password.split("$")
        if len(parts) != 3:
            return False
        salt, iterations_str, original_hash = parts
        iterations = int(iterations_str)
        computed_hash = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        ).hex()
        return hmac.compare_digest(computed_hash, original_hash)
    except Exception:
        return False


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data.encode("ascii"))


def create_access_token(user_id: str, email: str, expires_delta_seconds: Optional[int] = None) -> str:
    """Creates an HMAC-SHA256 signed JWT token."""
    header = {"alg": "HS256", "typ": "JWT"}
    header_bytes = json.dumps(header, separators=(",", ":")).encode("utf-8")
    header_b64 = _b64url_encode(header_bytes)

    expire_duration = expires_delta_seconds or (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(time.time()),
        "exp": int(time.time()) + expire_duration,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = _b64url_encode(payload_bytes)

    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    signature = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates an HMAC-SHA256 signed token."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Malformed authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        header_b64, payload_b64, signature_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
        expected_sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        provided_sig = _b64url_decode(signature_b64)

        if not hmac.compare_digest(expected_sig, provided_sig):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload_bytes = _b64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Expiration check
        if payload.get("exp", 0) < time.time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
) -> Dict[str, Any]:
    """FastAPI dependency to extract and verify the current authenticated user."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Lazy import to avoid circular dependencies
    from app.services.users.user_service import get_user_by_id

    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
