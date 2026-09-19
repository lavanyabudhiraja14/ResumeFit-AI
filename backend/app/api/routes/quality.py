"""API route for Resume Quality Score."""

from fastapi import APIRouter, status
from app.services.quality.scorer import ResumeQualityScorer
from app.schemas.quality import ResumeQualityRequest, ResumeQualityResponse

router = APIRouter(prefix="/resume", tags=["Resume Quality"])
scorer = ResumeQualityScorer()


@router.post(
    "/quality",
    response_model=ResumeQualityResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate transparent Resume Quality Score across 5 dimensions",
)
def evaluate_resume_quality(request: ResumeQualityRequest):
    """
    Evaluates Structure, Skills, Experience, Projects, and Readability.
    Returns explainable overall score (0-100), dimensional breakdown, strengths, and weak areas.
    """
    result = scorer.evaluate(resume_text=request.text, extracted_skills=request.skills)

    return ResumeQualityResponse(
        success=True,
        overall_score=result["overall_score"],
        breakdown=result["breakdown"],
        strengths=result["strengths"],
        weak_areas=result["weak_areas"],
        word_count=result["word_count"],
        metrics_detected_count=result["metrics_detected_count"],
    )
