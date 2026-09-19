"""Extensible canonical skill normalizer mapping any alias/variant to canonical form."""

from typing import Dict, List, Optional
from app.services.nlp.taxonomy import SKILL_TAXONOMY, CATEGORIES


class SkillNormalizer:
    def __init__(self):
        self._alias_map: Dict[str, str] = {}
        self._category_map: Dict[str, str] = {}
        self._initialize_indices()

    def _initialize_indices(self):
        for canonical, info in SKILL_TAXONOMY.items():
            category = info.get("category", "Tools")
            self._category_map[canonical] = category

            # Map canonical name itself
            self._alias_map[canonical.lower()] = canonical

            # Map aliases
            for alias in info.get("aliases", []):
                self._alias_map[alias.lower()] = canonical

    def normalize(self, raw_name: str) -> Optional[str]:
        """Normalizes a raw skill string to its canonical form, or None if unknown."""
        cleaned = raw_name.strip().lower()
        return self._alias_map.get(cleaned)

    def get_category(self, canonical_name: str) -> str:
        """Returns category for a canonical skill, defaulting to Tools."""
        return self._category_map.get(canonical_name, "Tools")

    def get_all_canonical_skills(self) -> List[str]:
        """Returns all recognized canonical skills."""
        return list(SKILL_TAXONOMY.keys())

    def get_categories(self) -> List[str]:
        """Returns all registered categories."""
        return CATEGORIES
