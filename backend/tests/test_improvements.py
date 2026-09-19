"""Unit tests for Resume Improvement Suggestions Generator and API endpoint."""

from app.services.improvements.generator import ResumeImprovementsGenerator

SAMPLE_WEAK_RESUME = """
John Doe
Email: john@example.com

EXPERIENCE
Developer - Company XYZ
- Worked on a React dashboard.
- Responsible for backend APIs.
- Helped with database maintenance.

SKILLS
Python, JavaScript, React, Docker, SQL, Git
"""


def test_improvements_flags_passive_verbs_and_short_bullets():
    generator = ResumeImprovementsGenerator()
    suggestions = generator.generate_suggestions(SAMPLE_WEAK_RESUME)

    assert len(suggestions) >= 2
    categories = [s["category"] for s in suggestions]
    assert "Experience" in categories

    # Verify specific advice is grounded
    has_passive_advice = any("passive" in s["problem"].lower() or "action verbs" in s["suggested_improvement"].lower() for s in suggestions)
    assert has_passive_advice

    has_metric_advice = any("measurable" in s["problem"].lower() or "metric" in s["problem"].lower() for s in suggestions)
    assert has_metric_advice


def test_improvements_flags_missing_portfolio_links():
    generator = ResumeImprovementsGenerator()
    suggestions = generator.generate_suggestions(SAMPLE_WEAK_RESUME)

    has_link_advice = any("contact" in s["category"].lower() for s in suggestions)
    assert has_link_advice


def test_improvements_api_endpoint(client):
    payload = {
        "resume_text": SAMPLE_WEAK_RESUME,
    }
    response = client.post("/api/resume/improvements", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["total_suggestions"] >= 2
    for item in data["suggestions"]:
        assert "category" in item
        assert "problem" in item
        assert "explanation" in item
        assert "suggested_improvement" in item
