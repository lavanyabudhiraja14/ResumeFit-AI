"""Matching engine comparing resume skills against job requirements."""

from typing import Any, Dict, List, Set
from app.services.nlp.normalizer import SkillNormalizer
from app.services.nlp.embedder import SemanticEmbedder
from app.services.matching.scorer import calculate_match_score
from app.services.recommendations.recommender import RecommendationService


class MatchingEngine:
    def __init__(self):
        self.normalizer = SkillNormalizer()
        self.embedder = SemanticEmbedder()
        self.recommender = RecommendationService()

    def compare_skills(
        self,
        resume_skills: List[str],
        job_skills: List[str],
        semantic_threshold: float = 0.82,
    ) -> Dict[str, Any]:
        """
        Performs hybrid matching (exact + semantic) between resume skills and job requirements.
        Generates matched skills, missing skills, explainable score, and upskilling resources.
        """
        # Canonicalize resume skills
        resume_set: Set[str] = set()
        for s in resume_skills:
            norm = self.normalizer.normalize(s)
            resume_set.add(norm if norm else s.strip())

        # Canonicalize job skills
        job_canonical_list: List[str] = []
        for s in job_skills:
            norm = self.normalizer.normalize(s)
            c_name = norm if norm else s.strip()
            if c_name and c_name not in job_canonical_list:
                job_canonical_list.append(c_name)

        exact_matches = []
        semantic_matches = []
        missing_skills = []
        matched_details = []

        for j_skill in job_canonical_list:
            cat = self.normalizer.get_category(j_skill)

            # 1. Exact canonical match
            if j_skill in resume_set:
                exact_matches.append(j_skill)
                matched_details.append({
                    "name": j_skill,
                    "category": cat,
                    "match_type": "exact",
                })
                continue

            # 2. Semantic Transfer match
            best_sim = 0.0
            best_resume_skill = None
            for r_skill in resume_set:
                sim = self.embedder.compute_similarity(j_skill, r_skill)
                if sim > best_sim:
                    best_sim = sim
                    best_resume_skill = r_skill

            if best_sim >= semantic_threshold and best_resume_skill:
                semantic_matches.append({
                    "job_skill": j_skill,
                    "resume_skill": best_resume_skill,
                    "similarity": round(best_sim, 2),
                    "category": cat,
                })
                matched_details.append({
                    "name": j_skill,
                    "category": cat,
                    "match_type": "semantic",
                    "transferred_from": best_resume_skill,
                })
            else:
                missing_skills.append({
                    "name": j_skill,
                    "category": cat,
                })

        # 3. Calculate explainable match score
        score_info = calculate_match_score(
            total_job_skills=len(job_canonical_list),
            exact_matches=exact_matches,
            semantic_matches=semantic_matches,
            missing_skills=[m["name"] for m in missing_skills],
        )

        # 4. Generate recommendations for missing skills
        missing_names = [m["name"] for m in missing_skills]
        recommendations = self.recommender.get_recommendations_for_skills(missing_names)

        return {
            "match_percentage": score_info["match_percentage"],
            "matched_skills": matched_details,
            "missing_skills": missing_skills,
            "semantic_transfers": semantic_matches,
            "recommendations": recommendations,
            "score_breakdown": score_info,
        }
