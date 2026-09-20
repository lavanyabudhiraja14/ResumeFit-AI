"""Local embedding wrapper and semantic similarity calculator.

NOTE: This module intentionally does NOT depend on sentence-transformers/torch.
That dependency pulls 500MB+ into memory at import time, which reliably OOMs
on small hosting tiers (e.g. Render's free 512MB plan). Skill-similarity for
this app is well covered by the curated domain-transfer table plus a fast
character-trigram fallback, so the heavy model was removed rather than made
"optional" -- an optional import still risks being triggered accidentally.
"""

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# Established domain transfer relationships (similarity score ~ 0.82-0.88)
DOMAIN_RELATED_SKILLS = {
    "AWS": {"Google Cloud": 0.85, "Microsoft Azure": 0.85},
    "Google Cloud": {"AWS": 0.85, "Microsoft Azure": 0.85},
    "Microsoft Azure": {"AWS": 0.85, "Google Cloud": 0.85},
    "TypeScript": {"JavaScript": 0.88},
    "JavaScript": {"TypeScript": 0.80},
    "Tailwind CSS": {"CSS": 0.86, "Bootstrap": 0.82},
    "Bootstrap": {"CSS": 0.86, "Tailwind CSS": 0.82},
    "Next.js": {"React": 0.88},
    "Express.js": {"Node.js": 0.85},
    "FastAPI": {"Flask": 0.82, "Django": 0.80, "Python": 0.85},
    "Django": {"FastAPI": 0.80, "Flask": 0.82, "Python": 0.85},
    "PostgreSQL": {"MySQL": 0.84, "SQL": 0.88},
    "MySQL": {"PostgreSQL": 0.84, "SQL": 0.88},
    "Kubernetes": {"Docker": 0.85},
    "GitHub Actions": {"GitLab CI": 0.85, "Jenkins": 0.82, "CI/CD": 0.88},
    "GitLab CI": {"GitHub Actions": 0.85, "Jenkins": 0.82, "CI/CD": 0.88},
    "Jenkins": {"GitHub Actions": 0.82, "GitLab CI": 0.82, "CI/CD": 0.88},
    "PyTorch": {"TensorFlow": 0.84, "Deep Learning": 0.86},
    "TensorFlow": {"PyTorch": 0.84, "Deep Learning": 0.86},
}


class SemanticEmbedder:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SemanticEmbedder, cls).__new__(cls)
        return cls._instance

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Computes semantic similarity between two terms or sentences.

        Uses (1) exact match, (2) a curated domain-transfer lookup table for
        known related skills, then (3) a lightweight character-trigram
        (Jaccard) fallback. No ML model is loaded, so this is fast and has a
        negligible, constant memory footprint.
        """
        t1 = text1.strip().lower()
        t2 = text2.strip().lower()

        if t1 == t2:
            return 1.0

        # Check domain transfer rules first (instant & deterministic)
        if text1 in DOMAIN_RELATED_SKILLS and text2 in DOMAIN_RELATED_SKILLS[text1]:
            return DOMAIN_RELATED_SKILLS[text1][text2]
        if text2 in DOMAIN_RELATED_SKILLS and text1 in DOMAIN_RELATED_SKILLS[text2]:
            return DOMAIN_RELATED_SKILLS[text2][text1]

        # Fast Jaccard character-trigram fallback
        return self._ngram_similarity(text1, text2)

    def _ngram_similarity(self, s1: str, s2: str, n: int = 3) -> float:
        s1, s2 = s1.lower(), s2.lower()
        if len(s1) < n or len(s2) < n:
            return 1.0 if s1 == s2 else 0.0
        set1 = {s1[i : i + n] for i in range(len(s1) - n + 1)}
        set2 = {s2[i : i + n] for i in range(len(s2) - n + 1)}
        union = len(set1 | set2)
        return len(set1 & set2) / union if union > 0 else 0.0
