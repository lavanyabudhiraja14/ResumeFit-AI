"""API routes for Job Finder search, personalized recommendations, and matching."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.job_finder.service import JobSearchService
from app.schemas.job_finder import JobSearchFilter, JobSearchResponse, JobMatchItem
from app.core.auth import decode_access_token
from app.services.users.user_service import get_user_by_id

router = APIRouter(prefix="/jobs", tags=["Job Finder"])
job_service = JobSearchService()
optional_bearer = HTTPBearer(auto_error=False)


def _get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
) -> Optional[dict]:
    """Extract user if a valid bearer token is provided, without raising 401 if missing."""
    if not credentials or not credentials.credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id:
            return get_user_by_id(user_id)
    except Exception:
        return None
    return None


@router.get(
    "/recommended",
    response_model=JobSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Fetch personalized job feed tailored to candidate interests and resume",
)
def get_recommended_jobs(
    interests: Optional[str] = Query(None, description="Comma-separated interest IDs (e.g. 'frontend,cloud')"),
    location: Optional[str] = Query("", description="Location filter (e.g. 'Remote', 'Bengaluru')"),
    work_type: Optional[str] = Query("any", description="remote, hybrid, onsite, any"),
    experience_level: Optional[str] = Query("any", description="entry, mid, senior, any"),
    job_type: Optional[str] = Query("any", description="full-time, internship, part-time, contract, any"),
    search: Optional[str] = Query("", description="Keyword search in title, company, skills"),
    min_match: Optional[int] = Query(None, description="Minimum match percentage (e.g. 60, 70, 80)"),
    data_mode: Optional[str] = Query(None, description="Data mode override: 'live' or 'curated'"),
    user: Optional[dict] = Depends(_get_optional_user),
):
    """
    Personalized job feed:
    - Automatically loads user's saved interests and resume skills if authenticated.
    - Matches ANY of candidate's selected interests.
    - If resume skills exist, calculates exact ResumeFit match % and gap analysis.
    - If no resume skills exist, returns 'Recommended for your interests' without fake 0% match.
    """
    selected_interests: List[str] = []

    # 1. Determine interests
    if interests:
        selected_interests = [i.strip() for i in interests.split(",") if i.strip()]
    elif user and user.get("interests"):
        selected_interests = user.get("interests", [])

    # 2. Determine resume skills
    resume_skills: List[str] = []
    if user and user.get("resume_skills"):
        resume_skills = user.get("resume_skills", [])

    response = job_service.get_recommended_jobs(
        interests=selected_interests,
        location=location or "",
        work_type=work_type or "any",
        experience_level=experience_level or "any",
        job_type=job_type or "any",
        search=search or "",
        resume_skills=resume_skills,
        min_match=min_match,
        data_mode=data_mode,
    )
    return response


@router.post(
    "/search",
    response_model=JobSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search tech jobs and calculate match scores against candidate skills",
)
def search_jobs(filters: JobSearchFilter):
    """
    Searches jobs by role, location, work_type, experience_level, job_type, interests, and keywords.
    Reuses existing NLP skill extraction on all job postings.
    If candidate resume_skills are provided, computes match score and skill gaps via the existing MatchingEngine.
    """
    response = job_service.search_and_match(
        role=filters.role or "",
        location=filters.location or "",
        work_type=filters.work_type or "any",
        experience_level=filters.experience_level or "any",
        job_type=filters.job_type or "any",
        keywords=filters.keywords or "",
        interests=filters.interests,
        resume_skills=filters.resume_skills,
        min_match=filters.min_match,
        data_mode=filters.data_mode,
    )
    return response


@router.get(
    "/{job_id}",
    response_model=JobMatchItem,
    status_code=status.HTTP_200_OK,
    summary="Fetch single job details and requirements",
)
def get_job(
    job_id: str,
    user: Optional[dict] = Depends(_get_optional_user),
):
    resume_skills = user.get("resume_skills", []) if user else []
    item = job_service.get_job_details(job_id, resume_skills=resume_skills)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' was not found.",
        )
    return item
