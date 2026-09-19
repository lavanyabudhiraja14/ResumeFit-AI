"""Pydantic schemas for resume upload and skill extraction."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ResumeAnalysisResponse(BaseModel):
    success: bool = True
    filename: str
    extension: str
    file_size: int
    total_skills_count: int
    skills_by_category: Dict[str, List[str]]
    raw_skills: List[str]
    page_count: int = 1
    character_count: int = 0
    word_count: int = 0
    raw_text: Optional[str] = None
    quality: Optional[Dict[str, Any]] = None
