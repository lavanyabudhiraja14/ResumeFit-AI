"""Pydantic schemas for ATS Compatibility Analysis."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ContactInfoDetected(BaseModel):
    email: bool
    phone: bool
    linkedin: bool
    github: bool


class SectionsDetected(BaseModel):
    contact: bool
    summary: bool
    skills: bool
    experience: bool
    education: bool
    projects: bool


class ATSCompatibilityRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="Raw plain text of candidate resume")
    job_description: Optional[str] = Field(None, description="Optional target job description")
    job_skills: Optional[List[str]] = Field(None, description="Optional pre-extracted job skills")


class ATSCompatibilityResponse(BaseModel):
    success: bool = True
    compatibility_score: int = Field(..., description="Estimated ATS compatibility percentage (0-100)")
    contact: ContactInfoDetected
    sections: SectionsDetected
    positive_signals: List[str]
    potential_issues: List[str]
    missing_job_keywords: List[str] = []
