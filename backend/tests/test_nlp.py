"""Unit tests for NLP skill extraction, normalization, boundary safety, and API endpoints."""

import io
from app.services.nlp.normalizer import SkillNormalizer
from app.services.nlp.extractor import SkillExtractor


def test_normalizer_canonical_mappings():
    normalizer = SkillNormalizer()

    # React variations
    assert normalizer.normalize("React.js") == "React"
    assert normalizer.normalize("React JS") == "React"
    assert normalizer.normalize("reactjs") == "React"

    # Node.js variations
    assert normalizer.normalize("node") == "Node.js"
    assert normalizer.normalize("nodejs") == "Node.js"
    assert normalizer.normalize("Node.js") == "Node.js"

    # PostgreSQL variations
    assert normalizer.normalize("postgres") == "PostgreSQL"
    assert normalizer.normalize("PostgreSQL DB") == "PostgreSQL"
    assert normalizer.normalize("psql") == "PostgreSQL"

    # MongoDB variations
    assert normalizer.normalize("mongo") == "MongoDB"
    assert normalizer.normalize("mongo db") == "MongoDB"

    # Cloud & DevOps
    assert normalizer.normalize("k8s") == "Kubernetes"
    assert normalizer.normalize("gcp") == "Google Cloud"
    assert normalizer.normalize("amazon web services") == "AWS"


def test_boundary_safe_extraction_and_false_positive_prevention():
    extractor = SkillExtractor()

    # Ambiguous sentence containing words that start or end with C, R, Go
    text = (
        "We are having a Good continuous integration discussion about REST APIs, "
        "reacting quickly to changes, and going to production."
    )
    result = extractor.extract_skills(text)
    raw = result["raw_skills"]

    # "REST API" and "CI/CD" might match, but "C", "R", "Go", "React" shouldn't match "reacting" or "going"
    assert "C" not in raw
    assert "R" not in raw
    assert "Go" not in raw
    assert "React" not in raw  # "reacting" must not match React

    # Now with explicit programming language references:
    prog_text = "Proficient in C, C++, C#, Go programming, and R language."
    prog_result = extractor.extract_skills(prog_text)
    prog_raw = prog_result["raw_skills"]

    assert "C" in prog_raw
    assert "C++" in prog_raw
    assert "C#" in prog_raw
    assert "Go" in prog_raw
    assert "R" in prog_raw


def test_multiword_skills_and_categorization():
    extractor = SkillExtractor()
    text = (
        "Strong foundation in Data Structures and Algorithms, Object-Oriented Programming, "
        "and System Design. Built cloud infrastructure with AWS and Docker."
    )
    res = extractor.extract_skills(text)
    cats = res["skills_by_category"]

    assert "Data Structures and Algorithms" in cats["CS Fundamentals"]
    assert "Object-Oriented Programming" in cats["CS Fundamentals"]
    assert "System Design" in cats["CS Fundamentals"]
    assert "AWS" in cats["Cloud"]
    assert "Docker" in cats["DevOps"]


def test_job_analysis_api_endpoint(client):
    jd_payload = {
        "job_description": (
            "Looking for a Senior Frontend Developer proficient in React, TypeScript, "
            "Tailwind CSS, Next.js, and Git. Experience with Docker and AWS is a plus."
        )
    }
    response = client.post("/api/job/analyze", json=jd_payload)
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["total_skills_count"] >= 6
    assert "React" in data["raw_skills"]
    assert "TypeScript" in data["raw_skills"]
    assert "Docker" in data["raw_skills"]
    assert "AWS" in data["raw_skills"]


def test_resume_analysis_api_endpoint(client, sample_pdf_bytes):
    response = client.post(
        "/api/resume/analyze",
        files={"file": ("candidate_resume.pdf", sample_pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["filename"] == "candidate_resume.pdf"
    assert data["total_skills_count"] >= 8
    assert "Python" in data["raw_skills"]
    assert "FastAPI" in data["raw_skills"]
    assert "Docker" in data["raw_skills"]
    assert "PostgreSQL" in data["raw_skills"]
