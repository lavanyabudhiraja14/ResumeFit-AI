"""Pydantic schemas for Resume Quality evaluation."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class QualityBreakdown(BaseModel):
    structure: int = Field(..., description="Structure & section completeness (0-100)")
    skills: int = Field(..., description="Technical skill depth and breadth (0-100)")
    experience: int = Field(..., description="Experience description & metrics (0-100)")
    projects: int = Field(..., description="Project portfolio & tech integration (0-100)")
    readability: int = Field(..., description="Content density and layout hygiene (0-100)")


class ResumeQualityRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Raw plain text of resume")
    skills: Optional[List[str]] = Field(None, description="Pre-extracted skills if available")


class ResumeQualityResponse(BaseModel):
    success: bool = True
    overall_score: int = Field(..., description="Deterministic overall quality score (0-100)")
    breakdown: QualityBreakdown
    strengths: List[str]
    weak_areas: List[str]
    word_count: int = 0
    metrics_detected_count: int = 0
