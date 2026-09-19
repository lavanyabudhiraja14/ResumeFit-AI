"""API route for resume vs job description matching."""

from fastapi import APIRouter, HTTPException, status
from app.services.nlp.extractor import SkillExtractor
from app.services.matching.engine import MatchingEngine
from app.schemas.match import MatchAnalysisRequest, MatchAnalysisResponse

router = APIRouter(prefix="/match", tags=["Matching"])
skill_extractor = SkillExtractor()
matching_engine = MatchingEngine()


@router.post(
    "/analyze",
    response_model=MatchAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare resume skills against job requirements and generate recommendations",
)
def analyze_match(request: MatchAnalysisRequest):
    """
    Compares candidate resume skills against job requirements.
    Calculates transparent match score, identifies gaps, and recommends free YouTube courses.
    """
    job_skills = list(request.job_skills) if request.job_skills else []

    # If raw job description is provided, extract its technical skills
    if request.job_description and not job_skills:
        extracted = skill_extractor.extract_skills(request.job_description)
        job_skills = extracted["raw_skills"]

    if not job_skills and not request.job_description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide either 'job_description' text or 'job_skills' list.",
        )

    results = matching_engine.compare_skills(
        resume_skills=request.resume_skills,
        job_skills=job_skills,
    )

    return MatchAnalysisResponse(
        success=True,
        match_percentage=results["match_percentage"],
        matched_skills=results["matched_skills"],
        missing_skills=results["missing_skills"],
        recommendations=results["recommendations"],
        score_breakdown=results["score_breakdown"],
    )
