"""Deterministic Job Domain Classifier.

Maps job titles, descriptions, and technical skills to standardized interest taxonomy IDs:
frontend, backend, fullstack, mobile, gamedev, datascience, ml, ai, dataengineering,
nlp, cloud, devops, cybersecurity, sre, uiux, product, blockchain, qa.
"""

import re
from typing import List, Set, Dict, Any
from app.core.interest_taxonomy import VALID_INTEREST_IDS

# Domain keywords and skills mappings
DOMAIN_RULES: Dict[str, Dict[str, List[str]]] = {
    "frontend": {
        "title": [r"\bfrontend\b", r"\bfront-end\b", r"\bweb developer\b", r"\breact developer\b", r"\bui engineer\b"],
        "skills": ["react", "vue", "angular", "next.js", "typescript", "javascript", "html", "css", "tailwind", "redux", "svelte", "web performance"],
    },
    "backend": {
        "title": [r"\bbackend\b", r"\bback-end\b", r"\bapi\b", r"\bserver\b", r"\bplatform engineer\b"],
        "skills": ["python", "fastapi", "django", "node.js", "express", "go", "golang", "java", "spring boot", "postgresql", "redis", "mongodb", "mysql", "microservices", "rest api", "graphql"],
    },
    "fullstack": {
        "title": [r"\bfull[\s-]?stack\b", r"\bfullstack\b"],
        "skills": ["mern", "mean", "jamstack", "full stack", "react", "node.js"],
    },
    "mobile": {
        "title": [r"\bmobile\b", r"\bios\b", r"\bandroid\b", r"\breact native\b", r"\bflutter\b"],
        "skills": ["swift", "kotlin", "react native", "flutter", "ios", "android", "xcode", "mobile development"],
    },
    "gamedev": {
        "title": [r"\bgame\b", r"\bgameplay\b", r"\bunity\b", r"\bunreal\b", r"\bgraphics programmer\b"],
        "skills": ["unity", "unreal engine", "c++", "opengl", "vulkan", "shader", "game physics", "directx"],
    },
    "datascience": {
        "title": [r"\bdata scientist\b", r"\bdata science\b", r"\bapplied scientist\b"],
        "skills": ["statistics", "pandas", "numpy", "scipy", "scikit-learn", "r", "data analysis", "exploratory data analysis"],
    },
    "ml": {
        "title": [r"\bmachine learning\b", r"\bml engineer\b", r"\bdeep learning\b"],
        "skills": ["machine learning", "deep learning", "pytorch", "tensorflow", "scikit-learn", "neural networks", "model deployment", "computer vision"],
    },
    "ai": {
        "title": [r"\bai engineer\b", r"\bartificial intelligence\b", r"\bllm\b", r"\bgenai\b", r"\bgenerative ai\b"],
        "skills": ["artificial intelligence", "llms", "generative ai", "transformers", "langchain", "prompt engineering", "nlp", "rag"],
    },
    "dataengineering": {
        "title": [r"\bdata engineer\b", r"\betl\b", r"\bdata pipeline\b", r"\bdata warehouse\b"],
        "skills": ["spark", "apache spark", "kafka", "airflow", "snowflake", "bigquery", "sql", "etl", "data pipeline", "dbt"],
    },
    "nlp": {
        "title": [r"\bnlp\b", r"\bnatural language\b", r"\bspeech\b"],
        "skills": ["nlp", "natural language processing", "spacy", "nltk", "hugging face", "transformers", "embeddings", "bert"],
    },
    "cloud": {
        "title": [r"\bcloud engineer\b", r"\bcloud architect\b", r"\baws\b", r"\bazure\b", r"\bgcp\b"],
        "skills": ["aws", "azure", "google cloud", "gcp", "cloud computing", "serverless", "cloudformation", "iam"],
    },
    "devops": {
        "title": [r"\bdevops\b", r"\binfrastructure\b", r"\bplatform\b", r"\bci/cd\b"],
        "skills": ["docker", "kubernetes", "terraform", "ci/cd", "jenkins", "github actions", "ansible", "helm", "linux"],
    },
    "cybersecurity": {
        "title": [r"\bsecurity\b", r"\bcybersecurity\b", r"\binfosec\b", r"\bappsec\b", r"\bpenetration\b"],
        "skills": ["cybersecurity", "penetration testing", "owasp", "cryptography", "network security", "vulnerability assessment", "siem"],
    },
    "sre": {
        "title": [r"\bsre\b", r"\bsite reliability\b", r"\breliability\b"],
        "skills": ["site reliability engineering", "sre", "observability", "prometheus", "grafana", "datadog", "incident management", "slos"],
    },
    "uiux": {
        "title": [r"\bui/ux\b", r"\bux designer\b", r"\bui designer\b", r"\bproduct designer\b"],
        "skills": ["figma", "wireframing", "prototyping", "user research", "ui design", "ux design", "design systems"],
    },
    "product": {
        "title": [r"\bproduct manager\b", r"\btechnical product\b", r"\bproduct management\b"],
        "skills": ["product management", "product roadmap", "user stories", "agile", "scrum", "feature prioritization"],
    },
    "blockchain": {
        "title": [r"\bblockchain\b", r"\bweb3\b", r"\bsmart contract\b", r"\bcrypto\b"],
        "skills": ["blockchain", "solidity", "smart contracts", "ethereum", "web3", "rust"],
    },
    "qa": {
        "title": [r"\bqa\b", r"\bquality assurance\b", r"\bsdet\b", r"\btest engineer\b", r"\bautomation engineer\b"],
        "skills": ["qa", "testing", "selenium", "cypress", "playwright", "jest", "pytest", "test automation", "unit testing"],
    },
}


class JobDomainClassifier:
    """Classifies a job posting into standardized interest taxonomy domains."""

    def classify_job(
        self,
        title: str,
        description: str = "",
        skills: List[str] = None,
    ) -> List[str]:
        """
        Deterministically evaluates job title, description, and skills.
        Returns a sorted list of matched valid interest IDs.
        """
        title_lower = title.lower()
        desc_lower = description.lower()
        skills_set = {s.lower().strip() for s in (skills or [])}

        matched_domains: Set[str] = set()

        for domain_id, rules in DOMAIN_RULES.items():
            # 1. Check title patterns (strong signal)
            title_matched = False
            for pattern in rules["title"]:
                if re.search(pattern, title_lower):
                    matched_domains.add(domain_id)
                    title_matched = True
                    break

            if title_matched:
                continue

            # 2. Check skill matches
            skill_hits = sum(1 for s in rules["skills"] if s in skills_set or s in desc_lower)
            if skill_hits >= 2:
                matched_domains.add(domain_id)

        # Cross-domain implications
        if "fullstack" in matched_domains:
            matched_domains.add("frontend")
            matched_domains.add("backend")
        if "nlp" in matched_domains:
            matched_domains.add("ai")
            matched_domains.add("ml")
        if "ml" in matched_domains and ("deep learning" in desc_lower or "neural" in desc_lower):
            matched_domains.add("ai")
        if "sre" in matched_domains:
            matched_domains.add("devops")
        if "devops" in matched_domains and any(s in skills_set or s in desc_lower for s in ["aws", "azure", "gcp"]):
            matched_domains.add("cloud")

        # Filter strictly to valid taxonomy IDs
        final_domains = [d for d in matched_domains if d in VALID_INTEREST_IDS]
        return sorted(final_domains)

    def calculate_interest_relevance(
        self,
        job_domains: List[str],
        user_interests: List[str],
    ) -> float:
        """
        Calculates a deterministic relevance score between job domains and user interests.
        Returns:
            1.0: Strong primary match
            0.6: Partial overlap
            0.0: No match
        """
        if not user_interests or not job_domains:
            return 0.0

        user_set = set(user_interests)
        job_set = set(job_domains)
        intersection = user_set.intersection(job_set)

        if not intersection:
            return 0.0

        # Exact ratio of overlap
        return round(len(intersection) / len(user_set), 2)
