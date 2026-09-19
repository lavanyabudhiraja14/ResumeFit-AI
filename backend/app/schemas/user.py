"""Pydantic schemas for User Profile and Interests."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.core.interest_taxonomy import VALID_INTEREST_IDS


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    interests: List[str] = []
    onboarding_completed: bool = False
    resume_filename: Optional[str] = None
    resume_skills: List[str] = []
    created_at: Optional[str] = None


class UserResumeUpdateRequest(BaseModel):
    filename: str = Field(..., description="Uploaded resume file name")
    skills: List[str] = Field(..., description="Extracted resume skills")



class InterestsUpdateRequest(BaseModel):
    interests: List[str] = Field(..., min_length=1, description="List of valid interest IDs (minimum 1)")

    @field_validator("interests")
    @classmethod
    def validate_interests(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("At least one interest must be selected")
        invalid = [item for item in v if item not in VALID_INTEREST_IDS]
        if invalid:
            raise ValueError(f"Invalid interest ID(s): {', '.join(invalid)}")
        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for item in v:
            if item not in seen:
                seen.add(item)
                deduped.append(item)
        return deduped


class InterestDetail(BaseModel):
    id: str
    name: str
    category: str
    description: Optional[str] = ""


class TaxonomyCategoryItem(BaseModel):
    category: str
    description: str
    items: List[InterestDetail]


class TaxonomyResponse(BaseModel):
    categories: List[TaxonomyCategoryItem]
    total_interests: int


class UserInterestsResponse(BaseModel):
    interests: List[str]
    interest_details: List[InterestDetail]
    onboarding_completed: bool
