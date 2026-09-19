"""API routes for User Profile and Interests Management."""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import (
    UserResponse,
    UserResumeUpdateRequest,
    InterestsUpdateRequest,
    UserInterestsResponse,
    InterestDetail,
    TaxonomyResponse,
    TaxonomyCategoryItem,
)
from app.core.auth import get_current_user
from app.core.interest_taxonomy import (
    get_all_categories,
    get_interests_details,
    ALL_INTERESTS_MAP,
)
from app.services.users.user_service import update_user_interests, update_user_resume

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get profile of currently authenticated user",
)
def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns profile information for the authenticated bearer token user."""
    return UserResponse(
        id=current_user["id"],
        name=current_user["name"],
        email=current_user["email"],
        interests=current_user["interests"],
        onboarding_completed=current_user["onboarding_completed"],
        resume_filename=current_user.get("resume_filename"),
        resume_skills=current_user.get("resume_skills", []),
        created_at=current_user.get("created_at"),
    )


@router.post(
    "/me/resume",
    response_model=UserResponse,
    summary="Save user uploaded resume skills to their profile",
)
def save_user_resume(
    request: UserResumeUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Saves user's resume filename and extracted skills."""
    updated = update_user_resume(
        user_id=current_user["id"],
        filename=request.filename,
        skills=request.skills,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse(
        id=updated["id"],
        name=updated["name"],
        email=updated["email"],
        interests=updated["interests"],
        onboarding_completed=updated["onboarding_completed"],
        resume_filename=updated.get("resume_filename"),
        resume_skills=updated.get("resume_skills", []),
        created_at=updated.get("created_at"),
    )



@router.get(
    "/me/interests",
    response_model=UserInterestsResponse,
    summary="Get user's saved interests with rich metadata",
)
def get_user_interests(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns the list of interest IDs and their category details."""
    interests_ids = current_user.get("interests", [])
    details = get_interests_details(interests_ids)

    return UserInterestsResponse(
        interests=interests_ids,
        interest_details=[InterestDetail(**d) for d in details],
        onboarding_completed=current_user.get("onboarding_completed", False),
    )


@router.put(
    "/me/interests",
    response_model=UserInterestsResponse,
    summary="Update user's selected interests and mark onboarding complete",
)
def set_user_interests(
    request: InterestsUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Saves selected interest IDs to user profile and marks onboarding as completed.
    Validates all IDs against the central taxonomy.
    """
    updated_user = update_user_interests(
        user_id=current_user["id"],
        interests=request.interests,
        mark_onboarding_completed=True,
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    details = get_interests_details(updated_user["interests"])
    return UserInterestsResponse(
        interests=updated_user["interests"],
        interest_details=[InterestDetail(**d) for d in details],
        onboarding_completed=updated_user["onboarding_completed"],
    )
