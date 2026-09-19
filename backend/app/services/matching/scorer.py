"""Transparent and explainable match scoring engine."""

from typing import Any, Dict, List


def calculate_match_score(
    total_job_skills: int,
    exact_matches: List[str],
    semantic_matches: List[Dict[str, Any]],
    missing_skills: List[str],
) -> Dict[str, Any]:
    """
    Computes explainable match percentage:
    - Exact/Normalized match: 1.0 weight
    - Semantic transferable match: 0.75 weight
    - Missing skills: 0.0 weight
    """
    if total_job_skills == 0:
        return {
            "match_percentage": 0,
            "total_job_skills": 0,
            "exact_matches_count": 0,
            "semantic_matches_count": 0,
            "missing_skills_count": 0,
            "formula_explanation": "No technical skills were detected in the job description.",
        }

    exact_weight = 1.0 * len(exact_matches)
    semantic_weight = 0.75 * len(semantic_matches)

    raw_score = (exact_weight + semantic_weight) / total_job_skills
    percentage = int(round(raw_score * 100))
    percentage = max(0, min(100, percentage))

    # Generate transparent explanation
    parts = []
    if exact_matches:
        parts.append(f"Matched {len(exact_matches)} skills directly: {', '.join(exact_matches[:5])}{'...' if len(exact_matches) > 5 else ''}.")
    if semantic_matches:
        transfers = [f"{m['job_skill']} (via {m['resume_skill']})" for m in semantic_matches[:3]]
        parts.append(f"{len(semantic_matches)} transferable semantic matches: {', '.join(transfers)}.")
    if missing_skills:
        parts.append(f"{len(missing_skills)} required skills missing: {', '.join(missing_skills[:5])}{'...' if len(missing_skills) > 5 else ''}.")

    explanation = " ".join(parts) if parts else "No skills matched."

    return {
        "match_percentage": percentage,
        "total_job_skills": total_job_skills,
        "exact_matches_count": len(exact_matches),
        "semantic_matches_count": len(semantic_matches),
        "missing_skills_count": len(missing_skills),
        "formula_explanation": explanation,
    }
