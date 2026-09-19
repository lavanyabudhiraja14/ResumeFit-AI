"""Skill extractor engine with boundary protection, regex overrides, and categorization."""

import re
from typing import Any, Dict, List, Set
from app.services.nlp.cleaner import clean_text
from app.services.nlp.normalizer import SkillNormalizer
from app.services.nlp.taxonomy import SKILL_TAXONOMY, CATEGORIES


class SkillExtractor:
    def __init__(self):
        self.normalizer = SkillNormalizer()
        self._compiled_regexes = self._compile_patterns()

    def _compile_patterns(self) -> List[Dict[str, Any]]:
        patterns = []

        for canonical, info in SKILL_TAXONOMY.items():
            regex_override = info.get("regex_override")
            if regex_override:
                patterns.append({
                    "canonical": canonical,
                    "pattern": re.compile(regex_override, re.IGNORECASE if canonical not in {"C", "R", "Go"} else 0),
                })
            else:
                # Gather all aliases plus canonical
                aliases = set(info.get("aliases", []))
                aliases.add(canonical.lower())

                # Sort longest phrases first to favor multi-word matching (e.g., "Data Structures and Algorithms" before "Algorithms")
                sorted_aliases = sorted(aliases, key=len, reverse=True)

                escaped_aliases = [re.escape(a) for a in sorted_aliases]
                combined_regex = r"(?<![A-Za-z0-9_])(?:" + "|".join(escaped_aliases) + r")(?![A-Za-z0-9_])"
                patterns.append({
                    "canonical": canonical,
                    "pattern": re.compile(combined_regex, re.IGNORECASE),
                })

        return patterns

    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Extracts and normalizes technical skills from document text.
        Returns total count, categorized skills, and canonical list.
        """
        if not text:
            return {
                "total_count": 0,
                "skills_by_category": {cat: [] for cat in CATEGORIES},
                "raw_skills": [],
            }

        cleaned = clean_text(text)
        detected_canonical: Set[str] = set()

        for item in self._compiled_regexes:
            canonical = item["canonical"]
            pattern = item["pattern"]
            if pattern.search(cleaned):
                detected_canonical.add(canonical)

        # Categorize detected skills
        by_category: Dict[str, List[str]] = {cat: [] for cat in CATEGORIES}
        for skill in sorted(detected_canonical):
            cat = self.normalizer.get_category(skill)
            if cat in by_category:
                by_category[cat].append(skill)
            else:
                by_category["Tools"].append(skill)

        # Filter out empty categories for clean output
        active_categories = {k: v for k, v in by_category.items() if v}

        return {
            "total_count": len(detected_canonical),
            "skills_by_category": active_categories,
            "raw_skills": sorted(list(detected_canonical)),
        }
