"""Unit tests for ATS Compatibility Analyzer and API endpoint."""

from app.services.ats.analyzer import ATSCompatibilityAnalyzer

SAMPLE_STANDARD_RESUME = """
Jane Doe
Email: jane.doe@example.com | Phone: (555) 123-4567 | LinkedIn: linkedin.com/in/janedoe | GitHub: github.com/janedoe

SUMMARY
Experienced Software Developer with 3+ years in web development and cloud technologies.

SKILLS
Python, JavaScript, TypeScript, React, Node.js, Docker, Git, SQL, PostgreSQL

EXPERIENCE
Software Engineer - WebTech (2021 - Present)
- Developed RESTful APIs using Python and FastAPI.
- Built reactive frontends with React and TypeScript.

EDUCATION
Bachelor of Science in Computer Science - Tech University (2017 - 2021)

PROJECTS
Task Manager App - Full stack application with React and Node.js.
"""

SAMPLE_MISSING_CONTACT_RESUME = """
Developer Candidate
I am looking for a job.
SKILLS: Python, HTML
EXPERIENCE: Worked at Company A
"""


def test_standard_resume_ats_compatibility():
    analyzer = ATSCompatibilityAnalyzer()
    result = analyzer.analyze(SAMPLE_STANDARD_RESUME)

    assert result["compatibility_score"] >= 85
    contact = result["contact"]
    assert contact["email"] is True
    assert contact["phone"] is True
    assert contact["linkedin"] is True
    assert contact["github"] is True

    sections = result["sections"]
    assert sections["skills"] is True
    assert sections["experience"] is True
    assert sections["education"] is True
    assert len(result["positive_signals"]) >= 3


def test_missing_contact_details_flags_issues():
    analyzer = ATSCompatibilityAnalyzer()
    result = analyzer.analyze(SAMPLE_MISSING_CONTACT_RESUME)

    assert result["compatibility_score"] < 70
    contact = result["contact"]
    assert contact["email"] is False
    assert contact["phone"] is False
    assert any("email" in issue.lower() for issue in result["potential_issues"])


def test_ats_keyword_coverage_with_job():
    analyzer = ATSCompatibilityAnalyzer()
    job_desc = "Seeking a developer with Python, React, AWS, Kubernetes, and Redis."
    result = analyzer.analyze(SAMPLE_STANDARD_RESUME, job_description=job_desc)

    # Resume has Python and React, but missing AWS, Kubernetes, Redis
    missing = result["missing_job_keywords"]
    assert "AWS" in missing
    assert "Kubernetes" in missing
    assert "Redis" in missing
    assert any("missing from your resume" in issue.lower() for issue in result["potential_issues"])


def test_ats_api_endpoint(client):
    payload = {
        "resume_text": SAMPLE_STANDARD_RESUME,
        "job_description": "Looking for a Python and Docker developer.",
    }
    response = client.post("/api/resume/ats", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["compatibility_score"] >= 80
    assert "contact" in data
    assert "sections" in data
    assert "positive_signals" in data
    assert "potential_issues" in data
