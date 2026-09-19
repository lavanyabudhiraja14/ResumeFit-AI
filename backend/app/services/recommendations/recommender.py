"""Upskilling Recommendation Service mapping missing skills to free learning resources."""

import urllib.parse
from typing import Any, Dict, List
from app.services.recommendations.catalog import RECOMMENDATION_CATALOG


class RecommendationService:
    def get_recommendations_for_skills(self, skills: List[str]) -> List[Dict[str, Any]]:
        """
        Generates free learning recommendations for a list of missing skills.
        Uses curated YouTube courses where available, with structured fallback search links.
        """
        recommendations = []

        for skill in skills:
            rec = self.get_recommendation(skill)
            if rec:
                recommendations.append(rec)

        return recommendations

    def get_recommendation(self, skill: str) -> Dict[str, Any]:
        """Returns course recommendation for a single skill."""
        skill_clean = skill.strip()

        if skill_clean in RECOMMENDATION_CATALOG:
            item = RECOMMENDATION_CATALOG[skill_clean]
            return {
                "skill": skill_clean,
                "title": item["title"],
                "platform": item["platform"],
                "creator": item["creator"],
                "url": item["url"],
                "duration": item["duration"],
                "level": item.get("level", "All Levels"),
            }

        # Fallback: structured educational search link on YouTube
        encoded_query = urllib.parse.quote_plus(f"{skill_clean} full course tutorial")
        return {
            "skill": skill_clean,
            "title": f"Learn {skill_clean} - Free Video Tutorials",
            "platform": "YouTube",
            "creator": "Top Tech Educators",
            "url": f"https://www.youtube.com/results?search_query={encoded_query}",
            "duration": "Self-paced",
            "level": "Beginner to Intermediate",
        }
