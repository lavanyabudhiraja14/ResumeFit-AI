"""API route for Centralized Interest Taxonomy."""

from fastapi import APIRouter
from app.schemas.user import TaxonomyResponse, TaxonomyCategoryItem, InterestDetail
from app.core.interest_taxonomy import get_all_categories, ALL_INTERESTS_MAP

router = APIRouter(prefix="/interests", tags=["Interests"])


@router.get(
    "",
    response_model=TaxonomyResponse,
    summary="Get centralized interest taxonomy for onboarding and profile settings",
)
def get_interest_taxonomy():
    """Returns the standardized, single-source-of-truth interest categories and items."""
    categories_raw = get_all_categories()
    category_items = []
    for cat in categories_raw:
        items = [
            InterestDetail(
                id=item["id"],
                name=item["name"],
                category=cat["category"],
                description=item.get("description", ""),
            )
            for item in cat["items"]
        ]
        category_items.append(
            TaxonomyCategoryItem(
                category=cat["category"],
                description=cat["description"],
                items=items,
            )
        )

    return TaxonomyResponse(
        categories=category_items,
        total_interests=len(ALL_INTERESTS_MAP),
    )
