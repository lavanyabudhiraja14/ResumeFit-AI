"""Pydantic schemas for Job Finder service and provider abstraction."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Job(BaseModel):
    id: str = Field(..., description="Unique job identifier")
    title: str = Field(..., description="Job title / role")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location (e.g. Remote, Bengaluru, India, US)")
    work_type: str = Field("remote", description="Work arrangement: remote, hybrid, onsite")
    experience_level: str = Field("any", description="entry, mid, senior, any")
    job_type: str = Field("full-time", description="full-time, internship, part-time, contract")
    description: str = Field(..., description="Full or excerpt job description")
    skills: List[str] = Field(default_factory=list, description="Extracted required technical skills")
    interest_domains: List[str] = Field(default_factory=list, description="Standardized interest domains (e.g. frontend, cloud)")
    url: str = Field(..., description="Legitimate URL to original job posting / company careers")
    source: str = Field(..., description="Data provider or source name")
    data_mode: str = Field("curated", description="Honest indicator: 'curated' (development sample) or 'live'")
    posted_date: str = Field("Recent", description="Formatted posting date")


class JobSearchFilter(BaseModel):
    role: Optional[str] = Field("", description="Target role (e.g. Full Stack, Frontend, Python)")
    location: Optional[str] = Field("", description="Target location (e.g. Remote, India, Bengaluru)")
    work_type: Optional[str] = Field("any", description="remote, hybrid, onsite, any")
    experience_level: Optional[str] = Field("any", description="entry, mid, senior, any")
    job_type: Optional[str] = Field("any", description="full-time, internship, part-time, contract, any")
    keywords: Optional[str] = Field("", description="Optional technical keywords")
    interests: Optional[List[str]] = Field(default_factory=list, description="Candidate interest IDs to filter by")
    resume_skills: Optional[List[str]] = Field(default_factory=list, description="Candidate resume skills for matching")
    min_match: Optional[int] = Field(None, description="Minimum match percentage threshold (e.g. 60, 70, 80)")
    data_mode: Optional[str] = Field(None, description="Data mode filter: 'live' or 'curated'")


class JobMatchItem(BaseModel):
    job: Job
    match_percentage: Optional[int] = Field(None, description="Match score calculated via MatchingEngine. None if no resume provided.")
    matched_skills: List[str] = Field(default_factory=list, description="Required skills candidate has")
    missing_skills: List[str] = Field(default_factory=list, description="Required skills candidate lacks")
    interest_relevance: Optional[float] = Field(None, description="Relevance score matching candidate's interest domains")


class JobSearchResponse(BaseModel):
    success: bool = True
    total_jobs: int
    results: List[JobMatchItem]
    source: str = Field("Curated Development Job Provider", description="Active job data provider name")
    data_mode: str = Field("curated", description="Data mode: 'curated' development sample data or 'live'")
