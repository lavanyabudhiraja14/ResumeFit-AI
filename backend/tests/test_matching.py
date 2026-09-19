"""Unit tests for matching engine, scoring formula, semantic transfers, and recommendations."""

from app.services.matching.engine import MatchingEngine
from app.services.matching.scorer import calculate_match_score
from app.services.recommendations.recommender import RecommendationService


def test_matching_engine_exact_and_missing_skills():
    engine = MatchingEngine()
    resume_skills = ["React", "JavaScript", "Node.js", "MongoDB", "Git"]
    job_skills = ["React", "JavaScript", "Node.js", "MongoDB", "AWS", "Docker", "Redis"]

    result = engine.compare_skills(resume_skills=resume_skills, job_skills=job_skills)

    assert result["match_percentage"] == 57  # 4 / 7 = 57.14% -> 57%
    matched_names = [m["name"] for m in result["matched_skills"]]
    assert "React" in matched_names
    assert "JavaScript" in matched_names
    assert "Node.js" in matched_names
    assert "MongoDB" in matched_names

    missing_names = [m["name"] for m in result["missing_skills"]]
    assert "AWS" in missing_names
    assert "Docker" in missing_names
    assert "Redis" in missing_names

    # Check recommendations generated for missing skills
    rec_skills = [r["skill"] for r in result["recommendations"]]
    assert "Docker" in rec_skills
    assert "AWS" in rec_skills
    assert "Redis" in rec_skills
    for rec in result["recommendations"]:
        assert "youtube.com" in rec["url"]
        assert rec["platform"] == "YouTube"


def test_semantic_transfer_matching():
    engine = MatchingEngine()
    # Resume has Google Cloud, job requires AWS
    resume_skills = ["Google Cloud", "Python"]
    job_skills = ["AWS", "Python"]

    result = engine.compare_skills(resume_skills=resume_skills, job_skills=job_skills)

    # AWS should be recognized as a semantic transfer from Google Cloud
    matched_names = [m["name"] for m in result["matched_skills"]]
    assert "AWS" in matched_names
    assert "Python" in matched_names

    semantic_transfers = result["semantic_transfers"]
    assert len(semantic_transfers) == 1
    assert semantic_transfers[0]["job_skill"] == "AWS"
    assert semantic_transfers[0]["resume_skill"] == "Google Cloud"


def test_recommendation_service_curated_and_fallback():
    recommender = RecommendationService()

    # Curated skill: Docker
    docker_rec = recommender.get_recommendation("Docker")
    assert docker_rec["skill"] == "Docker"
    assert "TechWorld with Nana" in docker_rec["creator"]
    assert "youtube.com" in docker_rec["url"]

    # Novel uncatalogued skill: CustomSkillXYZ
    custom_rec = recommender.get_recommendation("CustomSkillXYZ")
    assert custom_rec["skill"] == "CustomSkillXYZ"
    assert "youtube.com/results" in custom_rec["url"]


def test_match_api_endpoint(client):
    payload = {
        "resume_skills": ["React", "JavaScript", "Node.js", "MongoDB", "Git"],
        "job_description": "We need a developer with React, Node.js, AWS, Docker, and Redis.",
    }
    response = client.post("/api/match/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["match_percentage"] > 0
    assert len(data["matched_skills"]) >= 2
    assert len(data["missing_skills"]) >= 2
    assert len(data["recommendations"]) >= 2
    assert "formula_explanation" in data["score_breakdown"]


def test_recommendation_api_endpoint(client):
    response = client.get("/api/recommendations/Docker")
    assert response.status_code == 200
    data = response.json()
    assert data["skill"] == "Docker"
    assert data["platform"] == "YouTube"
    assert "youtube.com" in data["url"]
