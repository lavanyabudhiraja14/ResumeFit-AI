"""Tests for Personalized Job Finder, Domain Classification, and Resume Matching."""

import pytest
from app.services.job_finder.classifier import JobDomainClassifier
from app.services.job_finder.providers.curated_provider import CuratedJobProvider
from app.services.job_finder.service import JobSearchService
from app.core.database import get_db_connection


@pytest.fixture(autouse=True)
def clean_test_db():
    """Ensure clean database state before each test."""
    with get_db_connection() as conn:
        conn.execute("DELETE FROM users;")
        conn.commit()
    yield


def test_job_provider_returns_normalized_jobs():
    """Verify provider returns normalized jobs with required metadata."""
    provider = CuratedJobProvider()
    jobs = provider.search_jobs()

    assert len(jobs) > 0
    for job in jobs:
        assert "id" in job
        assert "title" in job
        assert "company" in job
        assert "location" in job
        assert "work_type" in job
        assert "experience_level" in job
        assert "job_type" in job
        assert "description" in job
        assert "url" in job
        assert job["url"].startswith("http")
        assert job.get("data_mode") == "curated"


def test_job_domain_classifier():
    """Verify deterministic mapping of job titles, descriptions, and skills to interest IDs."""
    classifier = JobDomainClassifier()

    # 1. Frontend
    fe_domains = classifier.classify_job(
        title="Senior Frontend Engineer",
        description="Build responsive web apps using React, Next.js, TypeScript, and CSS.",
        skills=["React", "TypeScript", "Next.js", "CSS"],
    )
    assert "frontend" in fe_domains

    # 2. Backend
    be_domains = classifier.classify_job(
        title="Backend Software Engineer",
        description="High throughput API services using Python, FastAPI, and PostgreSQL.",
        skills=["Python", "FastAPI", "PostgreSQL"],
    )
    assert "backend" in be_domains

    # 3. Full Stack implies both fullstack, frontend, and backend
    fs_domains = classifier.classify_job(
        title="Full Stack Software Engineer",
        description="Build web applications with React and Node.js.",
        skills=["React", "Node.js"],
    )
    assert "fullstack" in fs_domains
    assert "frontend" in fs_domains
    assert "backend" in fs_domains

    # 4. Machine Learning & AI
    ai_domains = classifier.classify_job(
        title="Machine Learning Engineer",
        description="Train deep learning models using PyTorch, Transformers, and NLP.",
        skills=["PyTorch", "NLP", "Machine Learning"],
    )
    assert "ml" in ai_domains
    assert "ai" in ai_domains

    # 5. DevOps & Cloud
    devops_domains = classifier.classify_job(
        title="DevOps & Cloud Infrastructure Engineer",
        description="Manage Kubernetes clusters and AWS infrastructure via Terraform.",
        skills=["Docker", "Kubernetes", "AWS", "Terraform"],
    )
    assert "devops" in devops_domains
    assert "cloud" in devops_domains


def test_multiple_interest_matching_any_interest():
    """A user selecting multiple interests receives jobs matching ANY of their chosen interests."""
    service = JobSearchService()

    # User interested in frontend OR cloud
    response = service.get_recommended_jobs(interests=["frontend", "cloud"])
    assert response.success is True
    assert len(response.results) > 0

    for item in response.results:
        domains = item.job.interest_domains
        # Must match at least one of the selected interests
        assert "frontend" in domains or "cloud" in domains


def test_search_and_filters():
    """Test filtering by keyword, location, work_type, and job_type."""
    service = JobSearchService()

    # Location filter (e.g. Bengaluru)
    bengaluru_res = service.get_recommended_jobs(location="Bengaluru")
    for item in bengaluru_res.results:
        assert "bengaluru" in item.job.location.lower()

    # Work type filter (remote)
    remote_res = service.get_recommended_jobs(work_type="remote")
    for item in remote_res.results:
        assert item.job.work_type.lower() == "remote"

    # Search keyword in company or title
    search_res = service.get_recommended_jobs(search="Stripe")
    assert len(search_res.results) >= 1
    assert any("stripe" in item.job.company.lower() for item in search_res.results)


def test_no_resume_behavior():
    """When candidate has no resume, match_percentage must be None (never fake 0%)."""
    service = JobSearchService()
    response = service.get_recommended_jobs(interests=["frontend"], resume_skills=None)

    assert response.total_jobs > 0
    for item in response.results:
        assert item.match_percentage is None
        assert item.matched_skills == []
        assert item.missing_skills == []


def test_resume_matching_and_gaps():
    """When resume skills exist, exact match %, matched skills, and missing skills are computed."""
    service = JobSearchService()
    resume_skills = ["React", "TypeScript", "JavaScript", "HTML", "CSS"]

    response = service.get_recommended_jobs(interests=["frontend"], resume_skills=resume_skills)
    assert response.total_jobs > 0

    top_item = response.results[0]
    assert top_item.match_percentage is not None
    assert 0 <= top_item.match_percentage <= 100
    assert len(top_item.matched_skills) > 0
    assert isinstance(top_item.missing_skills, list)


def test_min_match_threshold_filter():
    """Test filtering out jobs below a match percentage threshold."""
    service = JobSearchService()
    resume_skills = ["React", "TypeScript", "JavaScript", "HTML", "CSS"]

    # Request jobs with at least 50% match
    response = service.get_recommended_jobs(
        interests=["frontend"],
        resume_skills=resume_skills,
        min_match=50,
    )
    for item in response.results:
        assert item.match_percentage is not None
        assert item.match_percentage >= 50


def test_recommended_jobs_api_endpoint(client):
    """Test GET /api/jobs/recommended via test client with query parameters."""
    response = client.get("/api/jobs/recommended?interests=frontend,backend&location=Remote")
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["data_mode"] == "curated"
    assert len(data["results"]) > 0

    for item in data["results"]:
        job = item["job"]
        assert "frontend" in job["interest_domains"] or "backend" in job["interest_domains"]
        assert "remote" in job["location"].lower() or job["work_type"] == "remote"


def test_authenticated_user_recommended_jobs(client):
    """Test GET /api/jobs/recommended automatically picks up authenticated user's interests & resume."""
    # 1. Sign up user
    signup_res = client.post(
        "/api/auth/signup",
        json={"name": "Cloud Dev", "email": "cloud.dev@example.com", "password": "Password123!"},
    )
    token = signup_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Save interests
    client.put("/api/users/me/interests", json={"interests": ["cloud", "devops"]}, headers=headers)

    # 3. Save resume skills
    resume_payload = {
        "filename": "devops_resume.pdf",
        "skills": ["Docker", "Kubernetes", "AWS", "Terraform", "Linux"],
    }
    client.post("/api/users/me/resume", json=resume_payload, headers=headers)

    # 4. Fetch recommended jobs with auth header (no query params)
    rec_res = client.get("/api/jobs/recommended", headers=headers)
    assert rec_res.status_code == 200
    data = rec_res.json()
    assert len(data["results"]) > 0

    for item in data["results"]:
        # Should have match_percentage computed from saved resume
        assert item["match_percentage"] is not None
        assert "Docker" in item["matched_skills"] or "AWS" in item["matched_skills"] or "Kubernetes" in item["matched_skills"]


def test_job_details_api(client):
    """Test fetching single job details."""
    response = client.get("/api/jobs/job-stripe-fs-01")
    assert response.status_code == 200
    data = response.json()
    assert data["job"]["company"] == "Stripe"
    assert data["job"]["data_mode"] == "curated"

    # Non-existent job
    res_404 = client.get("/api/jobs/non-existent-job-id")
    assert res_404.status_code == 404
