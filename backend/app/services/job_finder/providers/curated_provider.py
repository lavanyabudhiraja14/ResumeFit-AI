"""Curated Verified Tech Job Provider for development and demonstration.

Clearly labeled as development/sample data with legitimate verified company careers portals.
"""

from typing import Any, Dict, List, Optional
from app.services.job_finder.providers.base import BaseJobProvider

VERIFIED_TECH_JOBS: List[Dict[str, Any]] = [
    {
        "id": "job-stripe-fs-01",
        "title": "Full Stack Software Engineer",
        "company": "Stripe",
        "location": "Remote - US & India",
        "work_type": "remote",
        "experience_level": "mid",
        "job_type": "full-time",
        "description": "Stripe builds economic infrastructure for the internet. We are looking for Full Stack Engineers to build global payment APIs and web interfaces. Requirements: 3+ years experience with React, TypeScript, Node.js, and REST APIs. Experience with distributed systems, PostgreSQL, and Docker containerization. Familiarity with AWS and Redis caching is a strong plus.",
        "url": "https://stripe.com/jobs",
        "source": "Stripe Careers (Curated Sample)",
        "data_mode": "curated",
        "posted_date": "2 days ago",
    },
    {
        "id": "job-vercel-fe-02",
        "title": "Senior Frontend Developer",
        "company": "Vercel",
        "location": "Remote",
        "work_type": "remote",
        "experience_level": "senior",
        "job_type": "full-time",
        "description": "Vercel is the platform for frontend developers. Seeking a Senior Frontend Engineer to advance our design system and dashboard. Requirements: Deep expertise in React, Next.js, TypeScript, and modern CSS / Tailwind CSS. Strong understanding of web performance, browser APIs, Git, and automated testing.",
        "url": "https://vercel.com/careers",
        "source": "Vercel Careers (Curated Sample)",
        "data_mode": "curated",
        "posted_date": "3 days ago",
    },
    {
        "id": "job-datadog-be-03",
        "title": "Backend Software Engineer - Python",
        "company": "Datadog",
        "location": "Bengaluru, India / Hybrid",
        "work_type": "hybrid",
        "experience_level": "mid",
        "job_type": "full-time",
        "description": "Datadog is the monitoring and security platform for cloud applications. We need Backend Engineers to build high-throughput data pipelines. Requirements: Proficient in Python, FastAPI, PostgreSQL, and Redis. Experience with Docker, Kubernetes, microservices architecture, and Linux environments.",
        "url": "https://www.datadoghq.com/careers",
        "source": "Datadog Careers (Curated Sample)",
        "data_mode": "curated",
        "posted_date": "1 day ago",
    },
    {
        "id": "job-github-devops-04",
        "title": "DevOps & Cloud Infrastructure Engineer",
        "company": "GitHub",
        "location": "Remote",
        "work_type": "remote",
        "experience_level": "mid",
        "job_type": "full-time",
        "description": "Join GitHub's infrastructure engineering group. Requirements: Extensive experience with Docker, Kubernetes, CI/CD pipelines (GitHub Actions), and Terraform. Strong background in AWS or Microsoft Azure, Linux system administration, and shell scripting. Python or Go programming experience preferred.",
        "url": "https://github.com/about/careers",
        "source": "GitHub Careers (Curated Sample)",
        "data_mode": "curated",
        "posted_date": "Just now",
    },
    {
        "id": "job-postman-api-05",
        "title": "Software Engineer - APIs & Integrations",
        "company": "Postman",
        "location": "Bengaluru, India",
        "work_type": "onsite",
        "experience_level": "entry",
        "job_type": "full-time",
        "description": "Postman is looking for early-career Software Engineers passionate about developer tooling and API platforms. Requirements: Solid foundation in JavaScript, Node.js, Express.js, and REST APIs. Knowledge of Data Structures and Algorithms, Git, and SQL databases like PostgreSQL or MySQL.",
        "url": "https://www.postman.com/company/careers",
        "source": "Postman Careers (Curated Sample)",
        "data_mode": "curated",
        "posted_date": "4 days ago",
    },
    {
        "id": "job-meta-ai-06",
        "title": "Machine Learning Engineer - GenAI",
        "company": "Meta",
        "location": "Remote - US & India",
        "work_type": "remote",
        "experience_level": "mid",
        "job_type": "full-time",
        "description": "Meta builds generative AI technologies. Requirements: Strong proficiency in Python, PyTorch, NumPy, and Pandas. Experience with Machine Learning algorithms, Natural Language Processing, and deploying models to cloud infrastructure using Docker and AWS.",
        "url": "https://www.metacareers.com",
        "source": "Meta Careers (Curated Sample)",
        "data_mode": "curated",
        "posted_date": "1 week ago",
    },
    {
        "id": "job-canva-fe-07",
        "title": "Frontend Software Engineer",
        "company": "Canva",
        "location": "Hyderabad, India / Hybrid",
        "work_type": "hybrid",
        "experience_level": "mid",
        "job_type": "full-time",
        "description": "Canva's mission is to empower everyone to design anything. Requirements: Strong experience with React, TypeScript, HTML, and modern CSS. Experience building complex interactive web applications, state management with Redux, and collaborative real-time UI components.",
        "url": "https://www.canva.com/careers",
        "source": "Canva Careers (Curated Sample)",
        "data_mode": "curated",
        "posted_date": "3 days ago",
    },
    {
        "id": "job-snowflake-de-08",
        "title": "Data Platform & Pipeline Engineer",
        "company": "Snowflake",
        "location": "Bengaluru, India",
        "work_type": "hybrid",
        "experience_level": "mid",
        "job_type": "full-time",
        "description": "Build massive-scale distributed data warehouses and pipelines. Requirements: Strong proficiency in Python or Java, SQL, Apache Spark, and Kafka. Experience with ETL workflows using Airflow, cloud platforms (AWS, Snowflake), and distributed systems.",
        "url": "https://careers.snowflake.com",
        "source": "Snowflake Careers (Curated Sample)",
        "data_mode": "curated",
        "posted_date": "5 days ago",
    },
    {
        "id": "job-figma-uiux-09",
        "title": "Product Designer (UI/UX)",
        "company": "Figma",
        "location": "Remote",
        "work_type": "remote",
        "experience_level": "mid",
        "job_type": "full-time",
        "description": "Figma is the collaborative interface design tool. Seeking product designers to create intuitive developer and design experiences. Requirements: Experience with Figma, wireframing, high-fidelity prototyping, design systems, and user research. Strong visual design and interaction design portfolio.",
        "url": "https://www.figma.com/careers",
        "source": "Figma Careers (Curated Sample)",
        "data_mode": "curated",
        "posted_date": "2 days ago",
    },
    {
        "id": "job-crowdstrike-sec-10",
        "title": "Cybersecurity & Application Security Engineer",
        "company": "CrowdStrike",
        "location": "Delhi NCR, India",
        "work_type": "hybrid",
        "experience_level": "senior",
        "job_type": "full-time",
        "description": "Help stop breaches worldwide. Requirements: Solid background in application security, penetration testing, vulnerability management, and OWASP top 10. Experience with Python, Go, network security protocols, cryptography, and cloud security monitoring.",
        "url": "https://www.crowdstrike.com/careers",
        "source": "CrowdStrike Careers (Curated Sample)",
        "data_mode": "curated",
        "posted_date": "4 days ago",
    },
    {
        "id": "job-browserstack-qa-11",
        "title": "Software Development Engineer in Test (SDET)",
        "company": "BrowserStack",
        "location": "Mumbai, India",
        "work_type": "onsite",
        "experience_level": "entry",
        "job_type": "full-time",
        "description": "Build automated testing infrastructure for millions of developers. Requirements: Proficiency in JavaScript or Python. Experience with Selenium, Cypress, Playwright, and Pytest. Strong understanding of test automation, CI/CD pipelines, and web debugging.",
        "url": "https://www.browserstack.com/careers",
        "source": "BrowserStack Careers (Curated Sample)",
        "data_mode": "curated",
        "posted_date": "6 days ago",
    },
    {
        "id": "job-uber-mobile-12",
        "title": "Mobile Engineer - iOS & Android",
        "company": "Uber",
        "location": "Bengaluru, India",
        "work_type": "hybrid",
        "experience_level": "mid",
        "job_type": "full-time",
        "description": "Build high-performance driver and rider applications. Requirements: Deep experience with Swift or Kotlin, React Native, and mobile architecture patterns. Strong understanding of REST APIs, local mobile databases (SQLite, Realm), and offline-first mobile sync.",
        "url": "https://www.uber.com/careers",
        "source": "Uber Careers (Curated Sample)",
        "data_mode": "curated",
        "posted_date": "3 days ago",
    },
    {
        "id": "job-google-cloud-13",
        "title": "Cloud Solutions Architect",
        "company": "Google",
        "location": "Hyderabad, India / Remote",
        "work_type": "hybrid",
        "experience_level": "senior",
        "job_type": "full-time",
        "description": "Help enterprise customers scale on Google Cloud Platform. Requirements: Expertise in GCP, Kubernetes, Terraform, microservices architecture, and cloud networking. Strong proficiency with Python or Go, Docker containerization, and modern observability.",
        "url": "https://careers.google.com",
        "source": "Google Careers (Curated Sample)",
        "data_mode": "curated",
        "posted_date": "1 day ago",
    },
    {
        "id": "job-spotify-datasci-14",
        "title": "Data Scientist - Personalization & Algorithms",
        "company": "Spotify",
        "location": "Remote",
        "work_type": "remote",
        "experience_level": "mid",
        "job_type": "full-time",
        "description": "Power music recommendations for hundreds of millions of users. Requirements: Advanced degrees or experience in Statistics, Computer Science, or Mathematics. Mastery of Python, SQL, Pandas, Scikit-learn, and A/B experimentation frameworks.",
        "url": "https://www.lifeatspotify.com",
        "source": "Spotify Careers (Curated Sample)",
        "data_mode": "curated",
        "posted_date": "4 days ago",
    },
]


class CuratedJobProvider(BaseJobProvider):
    def __init__(self):
        self._jobs = VERIFIED_TECH_JOBS

    def search_jobs(
        self,
        role: str = "",
        location: str = "",
        work_type: str = "any",
        experience_level: str = "any",
        job_type: str = "any",
        keywords: str = "",
    ) -> List[Dict[str, Any]]:
        results = []
        role_q = role.lower().strip()
        loc_q = location.lower().strip()
        wt_q = work_type.lower().strip()
        exp_q = experience_level.lower().strip()
        jt_q = job_type.lower().strip()
        kw_q = keywords.lower().strip()

        for job in self._jobs:
            # Filter by role / title / keywords
            if role_q and role_q not in job["title"].lower() and role_q not in job["description"].lower():
                continue

            # Filter by location
            if loc_q and loc_q != "all" and loc_q not in job["location"].lower():
                continue

            # Filter by work type (remote, hybrid, onsite)
            if wt_q != "any" and wt_q != job.get("work_type", "remote").lower():
                continue

            # Filter by experience level (entry, mid, senior)
            if exp_q != "any" and exp_q != job.get("experience_level", "any").lower():
                continue

            # Filter by job type (full-time, internship, contract)
            if jt_q != "any" and jt_q != job.get("job_type", "full-time").lower():
                continue

            # Filter by keywords
            if kw_q and (kw_q not in job["description"].lower() and kw_q not in job["title"].lower()):
                continue

            results.append(dict(job))

        return results

    def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        for job in self._jobs:
            if job["id"] == job_id:
                return dict(job)
        return None
