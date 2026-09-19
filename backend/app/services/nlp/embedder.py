"""Local embedding wrapper and semantic similarity calculator."""

import logging
from typing import List, Optional
import numpy as np

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
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SemanticEmbedder, cls).__new__(cls)
            cls._instance._init_model()
        return cls._instance

    def _init_model(self):
        self.model_loaded = False
        self._model = None
        self._load_attempted = False

    def _get_model(self):
        if not self._load_attempted:
            self._load_attempted = True
            try:
                import os
                # Allow enabling network model download only if explicit flag is set
                allow_download = os.getenv("ENABLE_NEURAL_DOWNLOAD", "false").lower() == "true"
                from sentence_transformers import SentenceTransformer
                try:
                    self._model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
                    self.model_loaded = True
                except Exception:
                    if allow_download:
                        self._model = SentenceTransformer("all-MiniLM-L6-v2")
                        self.model_loaded = True
                    else:
                        self._model = None
                        self.model_loaded = False
            except Exception as e:
                logger.warning(f"SentenceTransformer not loaded, using domain transfer fallback: {e}")
                self._model = None
                self.model_loaded = False
        return self._model

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Computes cosine semantic similarity between two terms or sentences."""
        t1 = text1.strip().lower()
        t2 = text2.strip().lower()

        if t1 == t2:
            return 1.0

        # Check domain transfer rules first (instant & deterministic)
        if text1 in DOMAIN_RELATED_SKILLS and text2 in DOMAIN_RELATED_SKILLS[text1]:
            return DOMAIN_RELATED_SKILLS[text1][text2]
        if text2 in DOMAIN_RELATED_SKILLS and text1 in DOMAIN_RELATED_SKILLS[text2]:
            return DOMAIN_RELATED_SKILLS[text2][text1]

        # Use neural embedding model if available
        model = self._get_model()
        if model:
            try:
                embeddings = model.encode([text1, text2], normalize_embeddings=True)
                sim = float(np.dot(embeddings[0], embeddings[1]))
                return max(0.0, min(1.0, sim))
            except Exception:
                pass

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
