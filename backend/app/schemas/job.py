"""Pydantic schemas for job description analysis."""

from typing import Dict, List
from pydantic import BaseModel, Field


class JobAnalysisRequest(BaseModel):
    job_description: str = Field(..., min_length=10, description="Raw job description text")


class JobAnalysisResponse(BaseModel):
    success: bool = True
    total_skills_count: int
    skills_by_category: Dict[str, List[str]]
    raw_skills: List[str]
    character_count: int = 0
    word_count: int = 0
