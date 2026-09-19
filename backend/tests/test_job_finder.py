"""Unit tests for Job Finder service, provider abstraction, and API endpoints."""

from app.services.job_finder.service import JobSearchService
from app.services.job_finder.providers.curated_provider import CuratedJobProvider


def test_job_provider_filtering():
    provider = CuratedJobProvider()

    # Search for Frontend roles
    frontend_jobs = provider.search_jobs(role="Frontend")
    assert len(frontend_jobs) >= 2
    for j in frontend_jobs:
        assert "frontend" in j["title"].lower() or "frontend" in j["description"].lower()

    # Search for Remote work
    remote_jobs = provider.search_jobs(work_type="remote")
    assert len(remote_jobs) >= 3
    for j in remote_jobs:
        assert j["work_type"] == "remote"

    # Search for Location "India"
    india_jobs = provider.search_jobs(location="India")
    assert len(india_jobs) >= 2
    for j in india_jobs:
        assert "india" in j["location"].lower()


def test_job_service_extracts_skills_and_matches():
    service = JobSearchService()
    candidate_skills = ["React", "TypeScript", "Next.js", "Node.js", "PostgreSQL", "Docker"]

    response = service.search_and_match(
        role="Frontend",
        resume_skills=candidate_skills,
    )

    assert response.success is True
    assert response.total_jobs >= 2
    top_result = response.results[0]

    # Check that job has extracted skills
    assert len(top_result.job.skills) >= 2
    assert top_result.match_percentage is not None
    assert top_result.match_percentage > 0
    assert len(top_result.matched_skills) > 0

    # Verify descending sort by match percentage
    scores = [r.match_percentage for r in response.results if r.match_percentage is not None]
    assert scores == sorted(scores, reverse=True)


def test_job_search_api_endpoint(client):
    payload = {
        "role": "Full Stack",
        "work_type": "remote",
        "resume_skills": ["React", "Node.js", "TypeScript", "PostgreSQL", "Docker", "AWS"],
    }
    response = client.post("/api/jobs/search", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["total_jobs"] >= 1
    first_job = data["results"][0]
    assert first_job["match_percentage"] is not None
    assert "stripe" in first_job["job"]["company"].lower() or "engineer" in first_job["job"]["title"].lower()


def test_get_job_details_api_endpoint(client):
    response = client.get("/api/jobs/job-stripe-fs-01")
    assert response.status_code == 200
    data = response.json()
    assert data["job"]["id"] == "job-stripe-fs-01"
    assert data["job"]["company"] == "Stripe"
    assert "https://" in data["job"]["url"]

    # Invalid ID
    bad_res = client.get("/api/jobs/non-existent-id")
    assert bad_res.status_code == 404
