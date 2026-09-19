"""Resume Improvement Suggestions Generator based strictly on actual resume content."""

import re
from typing import Any, Dict, List, Optional
from app.services.nlp.cleaner import clean_text
from app.services.nlp.extractor import SkillExtractor


PASSIVE_OPENERS = re.compile(
    r"(?i)(?:^|\n|\•|\-|\*)\s*(?:responsible for|worked on|helped with|assisted in|participated in|handled|duties included|tasks involved)\b"
)

METRIC_PATTERN = re.compile(
    r"(?:\$\s*\d+(?:,\d{3})*(?:\.\d+)?[kKmMbB]?\+?|\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:%|[kKmMbB]\+?|\+)\s*(?:users|requests|downloads|stars|clients|customers|problems|qps)?|\b(?:latency|response time|performance|cycles)\b.*?\b\d+%)",
    re.IGNORECASE,
)


class ResumeImprovementsGenerator:
    def __init__(self):
        self.skill_extractor = SkillExtractor()

    def generate_suggestions(
        self,
        resume_text: str,
        skills: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generates structured, trustworthy improvement suggestions.
        Grounded strictly in the candidate's actual text without inventing fake facts or metrics.
        """
        cleaned = clean_text(resume_text or "")
        lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
        suggestions: List[Dict[str, Any]] = []

        # 1. Experience: Passive phrasing vs Strong Action Verbs
        passive_matches = PASSIVE_OPENERS.findall(cleaned)
        if passive_matches:
            suggestions.append({
                "category": "Experience",
                "problem": "Several bullet points begin with passive phrasing ('worked on', 'responsible for', 'helped with').",
                "explanation": "Passive phrasing obscures your direct ownership and technical contribution during recruiter reviews.",
                "suggested_improvement": "Replace passive openers with active engineering verbs such as 'Architected', 'Implemented', 'Engineered', 'Automated', or 'Optimized'.",
                "priority": "High Impact",
            })

        # 2. Experience: Bullet length & specificity
        bullet_lines = [l for l in lines if l.startswith(("•", "-", "*")) or len(l.split()) < 9 and len(l.split()) > 3]
        short_bullets = [b for b in bullet_lines if len(b.split()) <= 7 and not re.search(r"(?i)\b(?:education|skills|summary|contact)\b", b)]

        if len(short_bullets) >= 2:
            suggestions.append({
                "category": "Experience",
                "problem": "Multiple bullet points provide brief overviews without technical context.",
                "explanation": "Short lines like 'Built React dashboard' leave screeners unsure of the project scale, architecture, or your specific role.",
                "suggested_improvement": "Describe the system's purpose, key features built, architectural choices, and technical trade-offs.",
                "priority": "High Impact",
            })

        # 3. Measurable Outcomes / Quantification
        metrics = METRIC_PATTERN.findall(cleaned)
        if len(metrics) == 0:
            suggestions.append({
                "category": "Experience",
                "problem": "Few or no measurable outcomes or scale metrics were detected.",
                "explanation": "Quantified achievements (e.g. latency reduced, users served, percentage improvements) provide concrete proof of your impact.",
                "suggested_improvement": "Add truthful numbers where available (e.g., 'scaled API to handle 10k daily requests', 'reduced load times by 25%', 'improved test coverage to 90%').",
                "priority": "High Impact",
            })
        elif len(metrics) <= 2:
            suggestions.append({
                "category": "Experience",
                "problem": "Limited quantified metrics identified across your experience.",
                "explanation": "Adding 1-2 additional metric-driven bullets strengthens credibility for senior engineering positions.",
                "suggested_improvement": "Where truthful, mention scale, performance gains, team size, or volume handled in recent projects.",
                "priority": "Recommended",
            })

        # 4. Projects: Depth and Problem/Solution Framing
        has_projects = bool(re.search(r"(?i)\b(?:projects|personal projects|technical projects)\b", cleaned))
        if has_projects:
            suggestions.append({
                "category": "Projects",
                "problem": "Project listings frequently focus on tool names rather than engineering challenges.",
                "explanation": "Hiring managers look for how you solve real problems and reason about architecture beyond listing libraries.",
                "suggested_improvement": "Frame project bullets around: Problem solved $\\rightarrow$ Architecture & technologies chosen $\\rightarrow$ Measurable result or link to live demo/GitHub.",
                "priority": "Recommended",
            })
        else:
            suggestions.append({
                "category": "Projects",
                "problem": "No dedicated Projects section detected.",
                "explanation": "A projects section demonstrates practical coding initiative, especially for modern tech stacks.",
                "suggested_improvement": "Add 2-3 notable projects highlighting your role, tech stack, and GitHub repository links.",
                "priority": "High Impact",
            })

        # 5. Skills: Categorization & Formatting
        raw_skills = skills if skills is not None else self.skill_extractor.extract_skills(cleaned)["raw_skills"]
        has_categorized_skills = bool(re.search(r"(?i)\b(?:languages|frameworks|databases|cloud|devops|tools)\b\s*:", cleaned))

        if len(raw_skills) >= 6 and not has_categorized_skills:
            suggestions.append({
                "category": "Skills",
                "problem": "Skills appear in an un-categorized block or comma-separated list.",
                "explanation": "Categorized skill sections (e.g., Languages, Frameworks, Databases, DevOps) allow technical recruiters to evaluate your stack in 5 seconds.",
                "suggested_improvement": "Group skills into clear categories: Languages (Python, Go), Frontend (React, Next.js), Backend (FastAPI, Node.js), Databases (PostgreSQL, Redis).",
                "priority": "Recommended",
            })

        # 6. Contact & Portfolio Profiles
        has_linkedin = bool(re.search(r"(?i)\blinkedin\b", cleaned))
        has_github = bool(re.search(r"(?i)\b(?:github|gitlab|portfolio)\b", cleaned))

        if not has_linkedin or not has_github:
            missing_profiles = []
            if not has_linkedin:
                missing_profiles.append("LinkedIn")
            if not has_github:
                missing_profiles.append("GitHub / Portfolio")

            suggestions.append({
                "category": "Contact",
                "problem": f"Missing direct links to {', '.join(missing_profiles)}.",
                "explanation": "Technical recruiters and engineering managers frequently check code repositories and professional references before scheduling interviews.",
                "suggested_improvement": f"Add clean, clickable URLs to your {', '.join(missing_profiles)} at the top of your resume.",
                "priority": "Recommended",
            })

        return suggestions
