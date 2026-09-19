"""Unit tests for Resume Quality Scorer and API endpoint."""

from app.services.quality.scorer import ResumeQualityScorer


SAMPLE_COMPLETE_RESUME = """
Alex Johnson
Email: alex.johnson@example.com | Phone: +1-555-0199 | LinkedIn: linkedin.com/in/alexj | GitHub: github.com/alexj

PROFESSIONAL SUMMARY
Dynamic Full-Stack Software Engineer with 4+ years of experience building high-scale distributed applications.

TECHNICAL SKILLS
Languages: Python, JavaScript, TypeScript, SQL, C++
Frontend: React, Next.js, HTML, CSS, Tailwind CSS, Redux
Backend: Node.js, Express.js, FastAPI, REST APIs, GraphQL
Databases & Cloud: PostgreSQL, MongoDB, Redis, Docker, AWS, Git

WORK EXPERIENCE
Senior Full-Stack Developer - CloudScale Systems (2021 - Present)
- Architected and implemented microservices using FastAPI and PostgreSQL, serving 500k+ active users.
- Optimized API response latency by 42% through Redis caching and query indexing.
- Automated CI/CD deployment pipelines using Docker and GitHub Actions, cutting release cycles by 60%.
- Led a team of 4 engineers and spearheaded adoption of TypeScript and Next.js.

Software Engineer - FinTech Labs (2019 - 2021)
- Developed secure transaction processing services handling $10M+ in monthly transaction volume.
- Engineered responsive frontend dashboards with React, Redux, and Tailwind CSS.

PROJECTS
OpenSource Workflow Engine (github.com/alexj/workflow)
- Developed distributed task runner in Go and Python with Redis queue integration.
- Gained 1,200+ GitHub stars and 5,000+ monthly downloads.

EDUCATION
Bachelor of Technology in Computer Science
State University of Technology (2015 - 2019) | CGPA: 8.8 / 10
"""

SAMPLE_MINIMAL_RESUME = """
John Doe
Email: john@example.com
I am looking for a software job.
Skills: Python, HTML
"""


def test_complete_resume_quality_evaluation():
    scorer = ResumeQualityScorer()
    result = scorer.evaluate(SAMPLE_COMPLETE_RESUME)

    assert result["overall_score"] >= 75
    breakdown = result["breakdown"]
    assert breakdown["structure"] >= 80
    assert breakdown["skills"] >= 85
    assert breakdown["experience"] >= 80
    assert breakdown["projects"] >= 80
    assert breakdown["readability"] >= 85

    # Check strengths detected
    strengths = result["strengths"]
    assert any("skills section" in s.lower() for s in strengths)
    assert any("experience" in s.lower() for s in strengths)
    assert any("metrics" in s.lower() for s in strengths)
    assert result["metrics_detected_count"] >= 3


def test_minimal_resume_quality_identifies_gaps():
    scorer = ResumeQualityScorer()
    result = scorer.evaluate(SAMPLE_MINIMAL_RESUME)

    assert result["overall_score"] < 60
    weak_areas = result["weak_areas"]
    assert any("experience" in w.lower() for w in weak_areas)
    assert any("projects" in w.lower() for w in weak_areas)
    assert any("skills" in w.lower() for w in weak_areas)


def test_quality_api_endpoint(client):
    payload = {
        "text": SAMPLE_COMPLETE_RESUME,
    }
    response = client.post("/api/resume/quality", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["overall_score"] >= 75
    assert "structure" in data["breakdown"]
    assert "skills" in data["breakdown"]
    assert "experience" in data["breakdown"]
    assert "projects" in data["breakdown"]
    assert "readability" in data["breakdown"]
    assert len(data["strengths"]) > 0


def test_resume_analyze_includes_quality(client, sample_pdf_bytes):
    response = client.post(
        "/api/resume/analyze",
        files={"file": ("candidate_resume.pdf", sample_pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "raw_text" in data
    assert data["quality"] is not None
    assert "overall_score" in data["quality"]
    assert "breakdown" in data["quality"]
