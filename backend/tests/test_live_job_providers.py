"""Comprehensive automated tests for Live Job Providers, Aggregation, Caching, and Resilience."""

import pytest
from unittest.mock import MagicMock, patch
import httpx

from app.services.job_finder.providers.greenhouse_provider import GreenhouseJobProvider
from app.services.job_finder.providers.lever_provider import LeverJobProvider
from app.services.job_finder.providers.ashby_provider import AshbyJobProvider
from app.services.job_finder.providers.public_feed_provider import PublicFeedJobProvider
from app.services.job_finder.providers.curated_provider import CuratedJobProvider
from app.services.job_finder.aggregator import LiveJobAggregator, canonicalize_url, make_composite_key
from app.services.job_finder.cache import job_cache
from app.services.job_finder.service import JobSearchService
from app.core.database import get_db_connection


@pytest.fixture(autouse=True)
def clean_state():
    """Ensure clean database and cache state before each test."""
    job_cache.clear()
    with get_db_connection() as conn:
        conn.execute("DELETE FROM users;")
        conn.commit()
    yield
    job_cache.clear()


# Mock payloads
SAMPLE_GH_PAYLOAD = {
    "jobs": [
        {
            "id": 1001,
            "title": "Senior Frontend Engineer",
            "location": {"name": "Bengaluru, India"},
            "absolute_url": "https://job-boards.greenhouse.io/gitlab/jobs/1001?utm_source=test",
            "content": "<p>Develop web interfaces with React, Next.js, and TypeScript.</p>",
            "updated_at": "2026-09-15T12:00:00Z",
        }
    ]
}

SAMPLE_LEVER_PAYLOAD = [
    {
        "id": "lever-001",
        "text": "Backend Engineer - Platform",
        "hostedUrl": "https://jobs.lever.co/cred/lever-001",
        "categories": {
            "location": "Bengaluru, India",
            "commitment": "Full-time",
        },
        "workplaceType": "hybrid",
        "descriptionPlain": "Build scalable distributed services using Python, FastAPI, and PostgreSQL.",
        "createdAt": 1726000000000,
    }
]

SAMPLE_ASHBY_PAYLOAD = {
    "jobs": [
        {
            "id": "ashby-001",
            "title": "Machine Learning Engineer",
            "jobUrl": "https://jobs.ashbyhq.com/openai/ashby-001",
            "location": "Remote",
            "isRemote": True,
            "workplaceType": "Remote",
            "employmentType": "FullTime",
            "descriptionPlain": "Train generative AI models using PyTorch, Transformers, and Python.",
            "publishedAt": "2026-09-18T10:00:00Z",
        }
    ]
}

SAMPLE_JOBICY_PAYLOAD = {
    "jobs": [
        {
            "id": 9001,
            "url": "https://jobicy.com/jobs/9001",
            "jobTitle": "DevOps Cloud Engineer",
            "companyName": "CloudTech",
            "jobGeo": "Worldwide",
            "jobType": ["Full-Time"],
            "jobDescription": "<p>Maintain Kubernetes clusters and Terraform infrastructure on AWS.</p>",
            "pubDate": "2026-09-17T08:00:00Z",
        }
    ]
}


def test_greenhouse_provider_normalization():
    """Test Greenhouse provider parses and normalizes live jobs accurately."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = SAMPLE_GH_PAYLOAD

    with patch.object(httpx.Client, "get", return_value=mock_resp):
        provider = GreenhouseJobProvider(boards=["gitlab"])
        jobs = provider.search_jobs()

        assert len(jobs) == 1
        job = jobs[0]
        assert job["id"] == "gh-gitlab-1001"
        assert job["title"] == "Senior Frontend Engineer"
        assert job["company"] == "GitLab"
        assert "Bengaluru" in job["location"]
        assert job["data_mode"] == "live"
        assert job["source"] == "Greenhouse (GitLab)"
        assert job["url"].startswith("http")
        assert "React" in job["description"]
        assert job["posted_date"] == "2026-09-15"


def test_lever_provider_normalization():
    """Test Lever provider parses and normalizes live jobs accurately."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = SAMPLE_LEVER_PAYLOAD

    with patch.object(httpx.Client, "get", return_value=mock_resp):
        provider = LeverJobProvider(companies=["cred"])
        jobs = provider.search_jobs()

        assert len(jobs) == 1
        job = jobs[0]
        assert job["id"] == "lever-cred-lever-001"
        assert job["title"] == "Backend Engineer - Platform"
        assert job["company"] == "CRED"
        assert "Bengaluru" in job["location"]
        assert job["work_type"] == "hybrid"
        assert job["data_mode"] == "live"
        assert job["source"] == "Lever (CRED)"
        assert job["url"] == "https://jobs.lever.co/cred/lever-001"
        assert "FastAPI" in job["description"]


def test_ashby_provider_normalization():
    """Test Ashby provider parses and normalizes live jobs accurately."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = SAMPLE_ASHBY_PAYLOAD

    with patch.object(httpx.Client, "get", return_value=mock_resp):
        provider = AshbyJobProvider(companies=["openai"])
        jobs = provider.search_jobs()

        assert len(jobs) == 1
        job = jobs[0]
        assert job["id"] == "ashby-openai-ashby-001"
        assert job["title"] == "Machine Learning Engineer"
        assert job["company"] == "OpenAI"
        assert job["work_type"] == "remote"
        assert job["data_mode"] == "live"
        assert job["source"] == "Ashby (OpenAI)"
        assert job["posted_date"] == "2026-09-18"


def test_public_feed_jobicy_normalization():
    """Test Jobicy public remote feed parsing and normalization."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = SAMPLE_JOBICY_PAYLOAD

    with patch.object(httpx.Client, "get", return_value=mock_resp):
        provider = PublicFeedJobProvider(count=10)
        jobs = provider.search_jobs()

        assert len(jobs) == 1
        job = jobs[0]
        assert job["id"] == "jobicy-9001"
        assert job["title"] == "DevOps Cloud Engineer"
        assert job["company"] == "CloudTech"
        assert job["work_type"] == "remote"
        assert job["source"] == "Jobicy"
        assert job["data_mode"] == "live"
        assert "Kubernetes" in job["description"]


def test_provider_timeout_and_error_handling():
    """Verify that timeout or HTTP error does not crash the provider and returns empty list."""
    with patch.object(httpx.Client, "get", side_effect=httpx.TimeoutException("Network timeout")):
        provider = GreenhouseJobProvider(boards=["gitlab"])
        jobs = provider.search_jobs()
        assert jobs == []

    mock_resp_500 = MagicMock()
    mock_resp_500.status_code = 500
    with patch.object(httpx.Client, "get", return_value=mock_resp_500):
        provider = AshbyJobProvider(companies=["openai"])
        jobs = provider.search_jobs()
        assert jobs == []


def test_missing_job_url_filtered_out():
    """Verify that records with missing or invalid URLs are safely skipped."""
    bad_payload = {
        "jobs": [
            {
                "id": 999,
                "title": "Invalid Job",
                "absolute_url": "",  # missing url
                "content": "No URL here",
            }
        ]
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = bad_payload

    with patch.object(httpx.Client, "get", return_value=mock_resp):
        provider = GreenhouseJobProvider(boards=["gitlab"])
        jobs = provider.search_jobs()
        assert len(jobs) == 0


def test_deduplication_logic():
    """Verify deterministic URL canonicalization and composite key deduplication."""
    url1 = "https://boards.greenhouse.io/test/jobs/123?utm_source=feed&gh_jid=123"
    url2 = "https://boards.greenhouse.io/test/jobs/123"
    assert canonicalize_url(url1) == canonicalize_url(url2)

    comp1 = make_composite_key("Stripe, Inc.", "Software Engineer", "Remote")
    comp2 = make_composite_key("stripe", "software engineer", "remote")
    assert comp1 == comp2

    # Test LiveJobAggregator deduplicates two providers returning identical jobs
    p1 = MagicMock()
    p1.search_jobs.return_value = [
        {"id": "j1", "company": "Acme", "title": "Dev", "location": "Remote", "url": "https://acme.com/job/1"}
    ]
    p2 = MagicMock()
    p2.search_jobs.return_value = [
        {"id": "j2", "company": "Acme", "title": "Dev", "location": "Remote", "url": "https://acme.com/job/1?utm_medium=email"}
    ]

    aggregator = LiveJobAggregator(providers=[p1, p2])
    deduped = aggregator.search_jobs()
    assert len(deduped) == 1
    assert deduped[0]["id"] == "j1"


def test_partial_provider_failure():
    """Verify that if one provider fails, the aggregator still returns jobs from healthy providers."""
    p_failing = MagicMock()
    p_failing.search_jobs.side_effect = Exception("Service unavailable")

    p_healthy = MagicMock()
    p_healthy.search_jobs.return_value = [
        {"id": "h1", "company": "GoodCo", "title": "Engineer", "location": "Remote", "url": "https://goodco.com/1"}
    ]

    aggregator = LiveJobAggregator(providers=[p_failing, p_healthy])
    results = aggregator.search_jobs()
    assert len(results) == 1
    assert results[0]["company"] == "GoodCo"


def test_caching_layer():
    """Verify that cached data is served without calling external endpoints again."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = SAMPLE_GH_PAYLOAD

    with patch.object(httpx.Client, "get", return_value=mock_resp) as mock_get:
        provider = GreenhouseJobProvider(boards=["gitlab"])
        # First call hits mock
        res1 = provider.search_jobs()
        assert len(res1) == 1
        assert mock_get.call_count == 1

        # Second call hits cache
        res2 = provider.search_jobs()
        assert len(res2) == 1
        assert mock_get.call_count == 1  # No additional call!


def test_live_data_mode_vs_curated_separation():
    """Verify that live mode returns data_mode='live' and curated mode returns 'curated' without mixing."""
    service = JobSearchService()

    # Curated mode
    curated_res = service.get_recommended_jobs(data_mode="curated")
    assert curated_res.data_mode == "curated"
    for item in curated_res.results:
        assert item.job.data_mode == "curated"

    # Mock live provider
    mock_provider = MagicMock()
    mock_provider.search_jobs.return_value = [
        {
            "id": "test-live-1",
            "title": "Full Stack Engineer",
            "company": "LiveCo",
            "location": "Remote",
            "work_type": "remote",
            "description": "React and Python web apps",
            "url": "https://liveco.com/job/1",
            "source": "Live Provider",
            "data_mode": "live",
            "posted_date": "2026-09-19",
        }
    ]
    service_live = JobSearchService(provider=mock_provider, data_mode="live")
    live_res = service_live.get_recommended_jobs(data_mode="live")
    assert live_res.data_mode == "live"
    assert len(live_res.results) == 1
    assert live_res.results[0].job.data_mode == "live"


def test_interest_filtering_on_live_jobs():
    """Verify domain classification and interest filtering on live job feeds."""
    mock_provider = MagicMock()
    mock_provider.search_jobs.return_value = [
        {
            "id": "fe-1",
            "title": "Frontend Developer",
            "company": "WebCo",
            "location": "Remote",
            "description": "Build user interfaces with React, Vue, CSS, and TypeScript.",
            "url": "https://webco.com/1",
            "source": "Greenhouse (WebCo)",
            "data_mode": "live",
        },
        {
            "id": "cloud-1",
            "title": "Cloud Architect",
            "company": "CloudCo",
            "location": "Remote",
            "description": "Manage AWS, Terraform, and Kubernetes infrastructure.",
            "url": "https://cloudco.com/1",
            "source": "Ashby (CloudCo)",
            "data_mode": "live",
        },
    ]

    service = JobSearchService(provider=mock_provider, data_mode="live")

    # User interested in frontend only
    fe_res = service.get_recommended_jobs(interests=["frontend"], data_mode="live")
    assert len(fe_res.results) == 1
    assert fe_res.results[0].job.id == "fe-1"

    # User interested in cloud only
    cloud_res = service.get_recommended_jobs(interests=["cloud"], data_mode="live")
    assert len(cloud_res.results) == 1
    assert cloud_res.results[0].job.id == "cloud-1"

    # User interested in frontend OR cloud
    both_res = service.get_recommended_jobs(interests=["frontend", "cloud"], data_mode="live")
    assert len(both_res.results) == 2


def test_location_filtering_india_and_remote():
    """Verify location filtering handles India hubs and Remote appropriately."""
    mock_provider = MagicMock()
    mock_provider.search_jobs.return_value = [
        {
            "id": "j-bengaluru",
            "title": "Backend Engineer",
            "company": "IndiCo",
            "location": "Bengaluru, Karnataka, India",
            "work_type": "hybrid",
            "description": "Python FastAPI backend",
            "url": "https://indico.com/1",
            "source": "Lever (IndiCo)",
            "data_mode": "live",
        },
        {
            "id": "j-remote",
            "title": "Frontend Engineer",
            "company": "GlobCo",
            "location": "Remote - Worldwide",
            "work_type": "remote",
            "description": "React web app",
            "url": "https://globco.com/1",
            "source": "Ashby (GlobCo)",
            "data_mode": "live",
        },
    ]

    service = JobSearchService(provider=mock_provider, data_mode="live")

    # Bengaluru filter
    bengaluru_res = service.get_recommended_jobs(location="Bengaluru", data_mode="live")
    assert any(item.job.id == "j-bengaluru" for item in bengaluru_res.results)

    # Remote filter
    remote_res = service.get_recommended_jobs(location="Remote", data_mode="live")
    assert any(item.job.id == "j-remote" for item in remote_res.results)


def test_resumefit_matching_on_live_jobs():
    """Verify that candidate resume skills trigger exact MatchingEngine analysis on live jobs."""
    mock_provider = MagicMock()
    mock_provider.search_jobs.return_value = [
        {
            "id": "live-fullstack",
            "title": "Full Stack Engineer",
            "company": "ScaleCo",
            "location": "Remote",
            "description": "Requirements: React, TypeScript, Python, and PostgreSQL.",
            "url": "https://scaleco.com/1",
            "source": "Greenhouse (ScaleCo)",
            "data_mode": "live",
        }
    ]

    service = JobSearchService(provider=mock_provider, data_mode="live")
    resume_skills = ["React", "TypeScript", "Python"]

    res = service.get_recommended_jobs(resume_skills=resume_skills, data_mode="live")
    assert len(res.results) == 1
    match_item = res.results[0]

    assert match_item.match_percentage is not None
    assert match_item.match_percentage > 50
    assert "React" in match_item.matched_skills or "TypeScript" in match_item.matched_skills
    assert isinstance(match_item.missing_skills, list)


def test_no_resume_behavior_on_live_jobs():
    """Verify that when no resume is uploaded, match_percentage is None (never fake 0%)."""
    mock_provider = MagicMock()
    mock_provider.search_jobs.return_value = [
        {
            "id": "live-1",
            "title": "Frontend Engineer",
            "company": "LiveCo",
            "location": "Remote",
            "description": "React and CSS",
            "url": "https://liveco.com/1",
            "source": "Jobicy",
            "data_mode": "live",
        }
    ]

    service = JobSearchService(provider=mock_provider, data_mode="live")
    res = service.get_recommended_jobs(resume_skills=None, data_mode="live")
    assert len(res.results) == 1
    assert res.results[0].match_percentage is None
    assert res.results[0].matched_skills == []
    assert res.results[0].missing_skills == []


def test_recommended_jobs_api_with_data_mode(client):
    """Test API endpoint accepts data_mode parameter."""
    # 1. Curated mode request
    res_curated = client.get("/api/jobs/recommended?data_mode=curated")
    assert res_curated.status_code == 200
    data_c = res_curated.json()
    assert data_c["data_mode"] == "curated"
    assert len(data_c["results"]) > 0

    # 2. Single job details API for curated job
    res_job = client.get("/api/jobs/job-stripe-fs-01")
    assert res_job.status_code == 200
    assert res_job.json()["job"]["company"] == "Stripe"
