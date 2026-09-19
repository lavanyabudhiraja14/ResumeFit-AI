"""API route for single skill learning resource recommendations."""

from fastapi import APIRouter, status
from app.services.recommendations.recommender import RecommendationService
from app.schemas.match import LearningResource

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])
recommender = RecommendationService()


@router.get(
    "/{skill}",
    response_model=LearningResource,
    status_code=status.HTTP_200_OK,
    summary="Fetch free learning course recommendations for a specific skill",
)
def get_skill_recommendation(skill: str):
    """Returns curated free YouTube course for the requested skill."""
    rec = recommender.get_recommendation(skill)
    return LearningResource(**rec)
