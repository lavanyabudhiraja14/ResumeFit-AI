"""ATS Compatibility Analyzer identifying parsing hygiene, contact signals, and keyword readiness."""

import re
from typing import Any, Dict, List, Optional
from app.services.nlp.cleaner import clean_text
from app.services.nlp.extractor import SkillExtractor


EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?:\+?\d{1,4}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}")
LINKEDIN_PATTERN = re.compile(r"(?i)\b(?:linkedin\.com/(?:in/)?[\w\-]+|linkedin)\b")
GITHUB_PATTERN = re.compile(r"(?i)\b(?:github\.com/[\w\-]+|github)\b")

SECTION_PATTERNS = {
    "summary": re.compile(r"(?i)\b(?:summary|objective|professional summary|career objective|profile)\b"),
    "skills": re.compile(r"(?i)\b(?:skills|technical skills|technologies|core competencies|tech stack)\b"),
    "experience": re.compile(r"(?i)\b(?:experience|work experience|employment history|work history|professional experience)\b"),
    "education": re.compile(r"(?i)\b(?:education|academic background|academics|qualifications)\b"),
    "projects": re.compile(r"(?i)\b(?:projects|technical projects|personal projects|key projects)\b"),
}


class ATSCompatibilityAnalyzer:
    def __init__(self):
        self.skill_extractor = SkillExtractor()

    def analyze(
        self,
        resume_text: str,
        job_description: Optional[str] = None,
        job_skills: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyzes resume for ATS parsing compatibility:
        - Contact details detection
        - Standard section headers presence
        - Formatting and character hygiene
        - Keyword alignment when target job is supplied
        """
        cleaned = clean_text(resume_text or "")
        words = cleaned.split()
        word_count = len(words)

        positive_signals: List[str] = []
        potential_issues: List[str] = []
        score = 100  # Start at 100 and deduct for evidence-based issues

        # 1. Contact Info Analysis
        has_email = bool(EMAIL_PATTERN.search(cleaned))
        has_phone = bool(PHONE_PATTERN.search(cleaned))
        has_linkedin = bool(LINKEDIN_PATTERN.search(cleaned))
        has_github = bool(GITHUB_PATTERN.search(cleaned))

        if has_email:
            positive_signals.append("Valid email address detected")
        else:
            potential_issues.append("No email address detected (critical for recruiter contact)")
            score -= 20

        if has_phone:
            positive_signals.append("Phone number detected")
        else:
            potential_issues.append("No phone number detected")
            score -= 15

        if has_linkedin:
            positive_signals.append("LinkedIn profile reference detected")
        else:
            potential_issues.append("Missing LinkedIn profile link")
            score -= 5

        if has_github:
            positive_signals.append("GitHub / portfolio link detected")

        # 2. Section Heading Hygiene
        detected_sections = {
            "contact": has_email or has_phone,
            "summary": bool(SECTION_PATTERNS["summary"].search(cleaned)),
            "skills": bool(SECTION_PATTERNS["skills"].search(cleaned)),
            "experience": bool(SECTION_PATTERNS["experience"].search(cleaned)),
            "education": bool(SECTION_PATTERNS["education"].search(cleaned)),
            "projects": bool(SECTION_PATTERNS["projects"].search(cleaned)),
        }

        recognized_core_count = sum([
            detected_sections["skills"],
            detected_sections["experience"],
            detected_sections["education"],
        ])

        if recognized_core_count == 3:
            positive_signals.append("Standard core sections detected (Skills, Experience, Education)")
        else:
            if not detected_sections["skills"]:
                potential_issues.append("Missing standard 'Skills' section header")
                score -= 15
            if not detected_sections["experience"]:
                potential_issues.append("Missing standard 'Experience' section header")
                score -= 15
            if not detected_sections["education"]:
                potential_issues.append("Missing standard 'Education' section header")
                score -= 10

        if detected_sections["projects"]:
            positive_signals.append("Standard 'Projects' section header detected")

        # 3. Formatting & Character Hygiene
        # Check for unusual symbols / unprintable chars count
        unusual_symbols = len(re.findall(r"[^\w\s.,!?:;()\-–—•$#+/\\\"'@%&*]", cleaned))
        if unusual_symbols > 25:
            potential_issues.append(f"Contains {unusual_symbols} unusual characters or decorative symbols that may confuse ATS parsers")
            score -= 10
        else:
            positive_signals.append("Clean text formatting without problematic decorative symbols")

        # Word count check
        if word_count < 150:
            potential_issues.append(f"Resume is very brief ({word_count} words); ATS parsers may flag incomplete information")
            score -= 15
        elif word_count > 1200:
            potential_issues.append(f"Resume is very long ({word_count} words); may exceed standard 1-2 page screening limits")
            score -= 5
        else:
            positive_signals.append(f"Optimal resume length ({word_count} words) for automated parsing")

        # 4. Keyword Alignment (if target job provided)
        missing_job_keywords: List[str] = []
        if job_description or job_skills:
            target_skills = list(job_skills) if job_skills else []
            if job_description and not target_skills:
                target_skills = self.skill_extractor.extract_skills(job_description)["raw_skills"]

            resume_skills = set(self.skill_extractor.extract_skills(cleaned)["raw_skills"])
            for skill in target_skills:
                if skill not in resume_skills:
                    missing_job_keywords.append(skill)

            if missing_job_keywords:
                count = len(missing_job_keywords)
                skills_preview = ", ".join(missing_job_keywords[:4])
                potential_issues.append(
                    f"{count} important job skills are missing from your resume: {skills_preview}{'...' if count > 4 else ''}"
                )
                score -= min(20, count * 4)
            else:
                positive_signals.append("All primary job keywords are present in your resume")

        compatibility_score = min(100, max(15, score))

        return {
            "compatibility_score": compatibility_score,
            "contact": {
                "email": has_email,
                "phone": has_phone,
                "linkedin": has_linkedin,
                "github": has_github,
            },
            "sections": detected_sections,
            "positive_signals": positive_signals,
            "potential_issues": potential_issues,
            "missing_job_keywords": missing_job_keywords,
        }
