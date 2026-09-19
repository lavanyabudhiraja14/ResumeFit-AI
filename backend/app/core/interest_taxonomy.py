"""Centralized Interest Taxonomy for ResumeFit AI.

Single source of truth for user career & technical interests.
Provides categorized interests with stable IDs and validation utilities.
"""

from typing import List, Dict, Optional, Any

# Taxonomy categorized hierarchy
TAXONOMY_CATEGORIES: List[Dict[str, Any]] = [
    {
        "category": "Software Development",
        "description": "Frontend, backend, mobile, systems and application development",
        "items": [
            {"id": "frontend", "name": "Frontend Development", "description": "Web interfaces, UI architectures, client-side frameworks"},
            {"id": "backend", "name": "Backend Development", "description": "Server-side logic, APIs, distributed systems, microservices"},
            {"id": "fullstack", "name": "Full Stack Development", "description": "End-to-end web applications, frontend and backend integration"},
            {"id": "mobile", "name": "Mobile Development", "description": "Native and cross-platform iOS and Android applications"},
            {"id": "gamedev", "name": "Game Development", "description": "Game engines, graphics programming, gameplay mechanics"},
        ],
    },
    {
        "category": "Data & AI",
        "description": "Data analytics, machine learning, and artificial intelligence systems",
        "items": [
            {"id": "datascience", "name": "Data Science", "description": "Statistical modeling, exploratory analysis, hypothesis testing"},
            {"id": "ml", "name": "Machine Learning", "description": "Predictive models, neural networks, supervised/unsupervised learning"},
            {"id": "ai", "name": "Artificial Intelligence", "description": "Generative models, LLMs, autonomous agents, computer vision"},
            {"id": "dataengineering", "name": "Data Engineering", "description": "Data pipelines, ETL, warehouses, streaming architectures"},
            {"id": "nlp", "name": "Natural Language Processing", "description": "Text extraction, semantic embeddings, speech processing"},
        ],
    },
    {
        "category": "Infrastructure",
        "description": "Cloud systems, automated pipelines, security, and reliability engineering",
        "items": [
            {"id": "cloud", "name": "Cloud Computing", "description": "AWS, GCP, Azure, cloud architectures, serverless"},
            {"id": "devops", "name": "DevOps", "description": "CI/CD, containerization, Kubernetes, infrastructure-as-code"},
            {"id": "cybersecurity", "name": "Cybersecurity", "description": "Application security, network defense, threat detection, penetration testing"},
            {"id": "sre", "name": "Site Reliability Engineering", "description": "System availability, observability, latency optimization, incident response"},
        ],
    },
    {
        "category": "Design & Product",
        "description": "User experience, product strategy, and interface design",
        "items": [
            {"id": "uiux", "name": "UI/UX Design", "description": "Wireframing, prototyping, design systems, user research"},
            {"id": "product", "name": "Product Management", "description": "Product roadmap, user story mapping, feature prioritization, agile delivery"},
        ],
    },
    {
        "category": "Other Technology",
        "description": "Emerging technologies and quality assurance",
        "items": [
            {"id": "blockchain", "name": "Blockchain", "description": "Smart contracts, decentralized systems, Web3 protocols"},
            {"id": "qa", "name": "QA / Testing", "description": "Test automation, integration testing, quality engineering"},
        ],
    },
]

# Fast lookup map: interest_id -> {id, name, category, description}
ALL_INTERESTS_MAP: Dict[str, Dict[str, str]] = {}
for cat in TAXONOMY_CATEGORIES:
    category_name = cat["category"]
    for item in cat["items"]:
        ALL_INTERESTS_MAP[item["id"]] = {
            "id": item["id"],
            "name": item["name"],
            "category": category_name,
            "description": item.get("description", ""),
        }

VALID_INTEREST_IDS = set(ALL_INTERESTS_MAP.keys())


def get_all_categories() -> List[Dict[str, Any]]:
    """Returns the full hierarchical interest taxonomy."""
    return TAXONOMY_CATEGORIES


def validate_interest_ids(interest_ids: List[str]) -> bool:
    """Checks if all given interest IDs exist in the taxonomy."""
    return all(interest_id in VALID_INTEREST_IDS for interest_id in interest_ids)


def get_interest_details(interest_id: str) -> Optional[Dict[str, str]]:
    """Fetches metadata for a single interest ID."""
    return ALL_INTERESTS_MAP.get(interest_id)


def get_interests_details(interest_ids: List[str]) -> List[Dict[str, str]]:
    """Fetches details for a list of valid interest IDs."""
    return [ALL_INTERESTS_MAP[i_id] for i_id in interest_ids if i_id in ALL_INTERESTS_MAP]
