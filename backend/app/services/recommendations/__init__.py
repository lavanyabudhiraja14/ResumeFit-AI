"""Upskilling recommendations package."""

from app.services.recommendations.catalog import RECOMMENDATION_CATALOG
from app.services.recommendations.recommender import RecommendationService

__all__ = ["RECOMMENDATION_CATALOG", "RecommendationService"]
