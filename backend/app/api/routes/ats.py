"""API route for ATS Compatibility Analyzer."""

from fastapi import APIRouter, status
from app.services.ats.analyzer import ATSCompatibilityAnalyzer
from app.schemas.ats import ATSCompatibilityRequest, ATSCompatibilityResponse

router = APIRouter(prefix="/resume", tags=["ATS Compatibility"])
analyzer = ATSCompatibilityAnalyzer()


@router.post(
    "/ats",
    response_model=ATSCompatibilityResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze resume ATS compatibility, contact info detection, and keyword coverage",
)
def evaluate_ats_compatibility(request: ATSCompatibilityRequest):
    """
    Evaluates potential ATS parsing issues:
    - Contact info verification (email, phone, LinkedIn, GitHub)
    - Standard section headers detection
    - Formatting and character hygiene
    - Keyword alignment against target job if provided
    """
    result = analyzer.analyze(
        resume_text=request.resume_text,
        job_description=request.job_description,
        job_skills=request.job_skills,
    )

    return ATSCompatibilityResponse(
        success=True,
        compatibility_score=result["compatibility_score"],
        contact=result["contact"],
        sections=result["sections"],
        positive_signals=result["positive_signals"],
        potential_issues=result["potential_issues"],
        missing_job_keywords=result["missing_job_keywords"],
    )
