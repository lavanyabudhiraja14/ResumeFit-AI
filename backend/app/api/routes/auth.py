"""API routes for User Authentication (Signup & Login)."""

from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserSummary
from app.core.auth import hash_password, verify_password, create_access_token
from app.services.users.user_service import get_user_by_email, create_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user and return session token",
)
def signup(request: SignupRequest):
    """
    Registers a new user account with Name, Email, and Password.
    Hashes password with PBKDF2-HMAC-SHA256 and creates token.
    """
    existing = get_user_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    pw_hash = hash_password(request.password)
    user = create_user(
        name=request.name,
        email=request.email,
        password_hash=pw_hash,
    )

    token = create_access_token(user_id=user["id"], email=user["email"])
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserSummary(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            interests=user["interests"],
            onboarding_completed=user["onboarding_completed"],
            created_at=user["created_at"],
        ),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and return session token",
)
def login(request: LoginRequest):
    """
    Authenticates an existing user via Email and Password.
    Returns JWT token and user profile with onboarding status.
    """
    user = get_user_by_email(request.email)
    if not user or not verify_password(request.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user_id=user["id"], email=user["email"])
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserSummary(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            interests=user["interests"],
            onboarding_completed=user["onboarding_completed"],
            created_at=user["created_at"],
        ),
    )
