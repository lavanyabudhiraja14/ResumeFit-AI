"""API route for Resume Improvement Suggestions."""

from fastapi import APIRouter, status
from app.services.improvements.generator import ResumeImprovementsGenerator
from app.schemas.improvements import ResumeImprovementsRequest, ResumeImprovementsResponse

router = APIRouter(prefix="/resume", tags=["Resume Improvements"])
generator = ResumeImprovementsGenerator()


@router.post(
    "/improvements",
    response_model=ResumeImprovementsResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate evidence-based resume improvement suggestions",
)
def generate_resume_improvements(request: ResumeImprovementsRequest):
    """
    Generates actionable, grounded improvement guidance:
    - Identifies passive verbs and suggests strong action verbs
    - Recommends quantifiable metrics and impact framing
    - Suggests structural categorization for technical skills
    - Highlights missing contact or portfolio links
    """
    suggestions = generator.generate_suggestions(
        resume_text=request.resume_text,
        skills=request.skills,
    )

    return ResumeImprovementsResponse(
        success=True,
        total_suggestions=len(suggestions),
        suggestions=suggestions,
    )
