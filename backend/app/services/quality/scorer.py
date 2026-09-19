"""Transparent, deterministic Resume Quality Scorer across 5 reliable dimensions."""

import re
from typing import Any, Dict, List, Optional
from app.services.nlp.cleaner import clean_text
from app.services.nlp.extractor import SkillExtractor


# Spacing-tolerant section heading regex helper
def _spaced_heading_pattern(headings: List[str]) -> re.Pattern:
    patterns = []
    for h in headings:
        chars = [re.escape(c) for c in h if not c.isspace()]
        spaced = r"\s*".join(chars)
        patterns.append(spaced)
    regex = rf"(?i)(?:^|\n|\r|\•|\-|\*|\s)(?:{'|'.join(patterns)})(?::|\s|\n|\r|$)"
    return re.compile(regex, re.MULTILINE)


SECTION_DETECTORS = {
    "contact": [
        re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", re.IGNORECASE),
        re.compile(r"(?:\+?\d{1,4}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"),
        _spaced_heading_pattern(["CONTACT", "CONTACT INFO", "CONTACT INFORMATION"]),
    ],
    "summary": [
        _spaced_heading_pattern(["SUMMARY", "PROFESSIONAL SUMMARY", "CAREER OBJECTIVE", "OBJECTIVE", "ABOUT ME", "PROFILE"]),
    ],
    "education": [
        _spaced_heading_pattern(["EDUCATION", "ACADEMIC BACKGROUND", "ACADEMIC DETAILS", "ACADEMICS", "QUALIFICATIONS"]),
        re.compile(r"(?i)\b(?:Bachelor of Technology|Bachelor of Science|B\.Tech|B\.E\.|Master of|M\.Tech|B\.S\.|B\.A\.|CGPA|GPA)\b"),
    ],
    "skills": [
        _spaced_heading_pattern(["TECHNICAL SKILLS", "SKILLS", "CORE COMPETENCIES", "TECHNOLOGIES", "AREAS OF EXPERTISE", "TECH STACK"]),
    ],
    "experience": [
        _spaced_heading_pattern(["WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE", "EMPLOYMENT HISTORY", "EXPERIENCE", "INTERNSHIPS", "WORK HISTORY"]),
    ],
    "projects": [
        _spaced_heading_pattern(["PERSONAL PROJECTS", "PROJECTS", "ACADEMIC PROJECTS", "KEY PROJECTS", "TECHNICAL PROJECTS"]),
    ],
    "certifications": [
        _spaced_heading_pattern(["CERTIFICATIONS", "CERTIFICATES", "LICENSES", "PROFESSIONAL CERTIFICATIONS"]),
    ],
    "links": [
        re.compile(r"(?i)\b(?:github\.com|linkedin\.com|leetcode\.com|hackerrank\.com|gitlab\.com)\b"),
        _spaced_heading_pattern(["LINKS", "PORTFOLIO", "PROFILES", "CODING PROFILES"]),
    ],
}

METRIC_PATTERN = re.compile(
    r"(?:\$\s*\d+(?:,\d{3})*(?:\.\d+)?[kKmMbB]?\+?|\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:%|[kKmMbB]\+?|\+)\s*(?:users|requests|downloads|stars|clients|customers|problems|qps)?|\b(?:latency|response time|performance|cycles)\b.*?\b\d+%)",
    re.IGNORECASE,
)

ACTION_VERB_PATTERN = re.compile(
    r"(?i)\b(?:developed|engineered|architected|implemented|automated|designed|built|optimized|spearheaded|led|created|maintained|deployed|reduced|accelerated|orchestrated|streamlined)\b"
)


class ResumeQualityScorer:
    def __init__(self):
        self.skill_extractor = SkillExtractor()

    def evaluate(self, resume_text: str, extracted_skills: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Evaluates resume quality across 5 dimensions:
        1. Structure (25%)
        2. Skills (25%)
        3. Experience (25%)
        4. Projects (15%)
        5. Readability (10%)
        """
        cleaned = clean_text(resume_text or "")
        words = cleaned.split()
        word_count = len(words)

        if not extracted_skills:
            skill_res = self.skill_extractor.extract_skills(cleaned)
            detected_skills = skill_res["raw_skills"]
            skills_by_category = skill_res["skills_by_category"]
        else:
            detected_skills = extracted_skills
            skills_by_category = {}
            for s in detected_skills:
                cat = self.skill_extractor.normalizer.get_category(s)
                skills_by_category.setdefault(cat, []).append(s)

        # 1. Detect Sections
        detected_sections: Dict[str, bool] = {}
        for sec, patterns in SECTION_DETECTORS.items():
            detected_sections[sec] = any(p.search(cleaned) for p in patterns)

        strengths: List[str] = []
        weak_areas: List[str] = []

        # --- Dimension 1: Structure (25%) ---
        structure_score = 40  # base
        if detected_sections["skills"]:
            structure_score += 15
            strengths.append("Dedicated technical skills section detected")
        else:
            weak_areas.append("Missing dedicated Skills section")

        if detected_sections["experience"]:
            structure_score += 15
            strengths.append("Professional work/internship experience section detected")
        else:
            weak_areas.append("No work or internship experience section detected")

        if detected_sections["projects"]:
            structure_score += 10
            strengths.append("Dedicated Projects portfolio section detected")
        else:
            weak_areas.append("No Projects section detected")

        if detected_sections["education"]:
            structure_score += 10
            strengths.append("Education and academic background clearly documented")
        else:
            weak_areas.append("No formal Education section detected")

        if detected_sections["contact"]:
            structure_score += 5
        if detected_sections["links"]:
            structure_score += 5
            strengths.append("Professional profile and portfolio links included (GitHub / LinkedIn)")

        structure_score = min(100, max(20, structure_score))

        # --- Dimension 2: Skills Coverage (25%) ---
        total_skills = len(detected_skills)
        cat_count = len(skills_by_category)

        if total_skills >= 10:
            skills_score = 95
            strengths.append(f"Strong technical skills inventory ({total_skills} verified skills detected)")
        elif total_skills >= 6:
            skills_score = 80
            strengths.append(f"Solid technical skills presence ({total_skills} skills detected)")
        elif total_skills >= 3:
            skills_score = 65
            weak_areas.append(f"Limited technical skills detected ({total_skills} skills); consider adding tools & frameworks")
        else:
            skills_score = 40
            weak_areas.append("Very few technical skills detected (under 3 skills)")

        if cat_count >= 4:
            skills_score = min(100, skills_score + 5)
            strengths.append(f"Well-rounded skill breadth spanning {cat_count} distinct technical domains")
        elif cat_count <= 1 and total_skills > 0:
            weak_areas.append("Skills are concentrated in only 1 domain; consider broadening your tech stack")

        # --- Dimension 3: Experience Descriptions (25%) ---
        metrics = METRIC_PATTERN.findall(cleaned)
        action_verbs = ACTION_VERB_PATTERN.findall(cleaned)

        if detected_sections["experience"]:
            experience_score = 60
            if len(metrics) >= 3:
                experience_score += 25
                strengths.append(f"Strong use of quantified metrics and impact outcomes ({len(metrics)} metrics found)")
            elif len(metrics) >= 1:
                experience_score += 15
                strengths.append("Contains measurable outcomes and metrics")
            else:
                weak_areas.append("Few or no quantified metrics in experience (e.g. percentages, impact numbers, scale)")

            if len(action_verbs) >= 5:
                experience_score += 15
                strengths.append("Strong use of active leadership action verbs (developed, engineered, optimized)")
            elif len(action_verbs) >= 2:
                experience_score += 10
            else:
                weak_areas.append("Consider using stronger action verbs to begin experience bullets")
        else:
            experience_score = 40
            weak_areas.append("Lacks professional experience descriptions")

        experience_score = min(100, max(20, experience_score))

        # --- Dimension 4: Projects (15%) ---
        if detected_sections["projects"]:
            projects_score = 75
            # Check if tech skills are mentioned near projects
            if total_skills >= 4:
                projects_score += 20
                strengths.append("Projects demonstrate practical application of technical skills")
            else:
                projects_score += 10
        else:
            projects_score = 45
            weak_areas.append("Adding key projects can showcase hands-on technical abilities")

        projects_score = min(100, max(20, projects_score))

        # --- Dimension 5: Readability (10%) ---
        if 200 <= word_count <= 800:
            readability_score = 95
            strengths.append("Optimal resume length and content density (1-2 pages)")
        elif 150 <= word_count < 200:
            readability_score = 80
            weak_areas.append("Resume is somewhat brief (under 200 words); consider elaborating on project impacts")
        elif 800 < word_count <= 1200:
            readability_score = 80
            weak_areas.append("Resume is somewhat lengthy; consider condensing to focused high-impact bullets")
        elif word_count < 150:
            readability_score = 50
            weak_areas.append("Resume is very brief (under 150 words); consider adding more technical substance")
        else:
            readability_score = 65
            weak_areas.append("Resume exceeds 1200 words; consider streamlining to 2 concise pages")

        # Overall Weighted Score Formula
        overall_score = round(
            0.25 * structure_score
            + 0.25 * skills_score
            + 0.25 * experience_score
            + 0.15 * projects_score
            + 0.10 * readability_score
        )
        overall_score = min(100, max(10, overall_score))

        return {
            "overall_score": overall_score,
            "breakdown": {
                "structure": structure_score,
                "skills": skills_score,
                "experience": experience_score,
                "projects": projects_score,
                "readability": readability_score,
            },
            "strengths": strengths,
            "weak_areas": weak_areas,
            "word_count": word_count,
            "metrics_detected_count": len(metrics),
        }
