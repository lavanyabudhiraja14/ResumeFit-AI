"""Pydantic schemas for matching engine and upskilling recommendations."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MatchSkillItem(BaseModel):
    name: str
    category: str
    match_type: Optional[str] = "exact"  # "exact" or "semantic"
    transferred_from: Optional[str] = None


class LearningResource(BaseModel):
    skill: str
    title: str
    platform: str
    creator: str
    url: str
    duration: str
    level: str = "Beginner to Intermediate"


class ScoreBreakdown(BaseModel):
    match_percentage: int
    total_job_skills: int
    exact_matches_count: int
    semantic_matches_count: int
    missing_skills_count: int
    formula_explanation: str


class MatchAnalysisRequest(BaseModel):
    resume_skills: List[str] = Field(..., description="Skills extracted from resume")
    job_description: Optional[str] = Field(None, description="Raw job description text")
    job_skills: Optional[List[str]] = Field(None, description="Pre-extracted job skills")


class MatchAnalysisResponse(BaseModel):
    success: bool = True
    match_percentage: int
    matched_skills: List[MatchSkillItem]
    missing_skills: List[MatchSkillItem]
    recommendations: List[LearningResource]
    score_breakdown: ScoreBreakdown
