"""API route for job description skill analysis."""

from fastapi import APIRouter, status
from app.services.nlp.cleaner import clean_text
from app.services.nlp.extractor import SkillExtractor
from app.schemas.job import JobAnalysisRequest, JobAnalysisResponse

router = APIRouter(prefix="/job", tags=["Job"])
skill_extractor = SkillExtractor()


@router.post(
    "/analyze",
    response_model=JobAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze job description and extract required technical skills",
)
def analyze_job_description(request: JobAnalysisRequest):
    """
    Accepts raw job description text.
    Extracts and normalizes all identified technical skills and tools required by the job.
    """
    cleaned = clean_text(request.job_description)
    extracted = skill_extractor.extract_skills(cleaned)
    words = cleaned.split()

    return JobAnalysisResponse(
        success=True,
        total_skills_count=extracted["total_count"],
        skills_by_category=extracted["skills_by_category"],
        raw_skills=extracted["raw_skills"],
        character_count=len(cleaned),
        word_count=len(words),
    )
