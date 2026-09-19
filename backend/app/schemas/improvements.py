"""Pydantic schemas for Resume Improvement Suggestions."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ImprovementItem(BaseModel):
    category: str = Field(..., description="Area of improvement: Experience, Projects, Skills, Contact, Formatting")
    problem: str = Field(..., description="Specific observation in the resume text")
    explanation: str = Field(..., description="Why this matters for recruiter screening and technical evaluations")
    suggested_improvement: str = Field(..., description="Actionable, grounded suggestion")
    priority: str = Field("Recommended", description="High Impact or Recommended")


class ResumeImprovementsRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="Raw plain text of resume")
    skills: Optional[List[str]] = Field(None, description="Pre-extracted skills if available")


class ResumeImprovementsResponse(BaseModel):
    success: bool = True
    total_suggestions: int
    suggestions: List[ImprovementItem]
