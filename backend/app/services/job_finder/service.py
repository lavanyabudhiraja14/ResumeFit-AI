"""Job Search Service coordinating providers, skill extraction, domain classification, and matching engine."""

import logging
from typing import Any, Dict, List, Optional, Set
from app.core.config import settings
from app.services.nlp.extractor import SkillExtractor
from app.services.matching.engine import MatchingEngine
from app.services.job_finder.providers.curated_provider import CuratedJobProvider
from app.services.job_finder.providers.base import BaseJobProvider
from app.services.job_finder.aggregator import LiveJobAggregator
from app.services.job_finder.classifier import JobDomainClassifier
from app.schemas.job_finder import Job, JobMatchItem, JobSearchResponse

logger = logging.getLogger(__name__)


class JobSearchService:
    def __init__(
        self,
        provider: Optional[BaseJobProvider] = None,
        data_mode: Optional[str] = None,
    ):
        self.mode = data_mode or settings.JOB_DATA_MODE
        self.curated_provider = CuratedJobProvider()
        self.live_aggregator = LiveJobAggregator()

        self._custom_provider = provider is not None
        if provider is not None:
            self.provider = provider
        elif self.mode == "live":
            self.provider = self.live_aggregator
        else:
            self.provider = self.curated_provider

        # Direct reuse of existing NLP, Matching, and Domain Classification engines
        self.skill_extractor = SkillExtractor()
        self.matching_engine = MatchingEngine()
        self.classifier = JobDomainClassifier()

    def get_recommended_jobs(
        self,
        interests: Optional[List[str]] = None,
        role: str = "",
        location: str = "",
        work_type: str = "any",
        experience_level: str = "any",
        job_type: str = "any",
        search: str = "",
        resume_skills: Optional[List[str]] = None,
        min_match: Optional[int] = None,
        data_mode: Optional[str] = None,
    ) -> JobSearchResponse:
        """
        Personalized job feed algorithm:
        1. Selects live or curated provider based on data_mode / configuration.
        2. Queries provider with basic criteria (location, work type, experience, job type).
        3. Normalizes jobs with extracted skills and deterministic domain tags.
        4. Filters jobs to match ANY of user's selected interests.
        5. If candidate resume skills exist, executes ResumeFit MatchingEngine to calculate exact match %,
           matched skills, and missing skills.
        6. Filters by min_match if requested.
        7. Ranks results by match score (if resume provided) and interest domain relevance.
        """
        effective_mode = data_mode or self.mode
        active_provider: BaseJobProvider
        if self._custom_provider:
            active_provider = self.provider
        elif data_mode == "curated":
            active_provider = self.curated_provider
        elif data_mode == "live":
            active_provider = self.live_aggregator
        else:
            active_provider = self.provider

        query_role = role or search
        raw_jobs = active_provider.search_jobs(
            role=query_role,
            location=location,
            work_type=work_type,
            experience_level=experience_level,
            job_type=job_type,
            keywords=search if not role else "",
        )

        user_interest_set: Set[str] = set(interests or [])
        results: List[JobMatchItem] = []

        for raw in raw_jobs:
            # Re-use existing NLP pipeline to extract job skills
            extracted = self.skill_extractor.extract_skills(raw["description"])
            job_skills = extracted["raw_skills"]

            # Deterministic domain classification
            domains = self.classifier.classify_job(
                title=raw["title"],
                description=raw["description"],
                skills=job_skills,
            )

            job_data_mode = raw.get("data_mode", effective_mode)

            # Construct normalized job model
            job_model = Job(
                id=raw["id"],
                title=raw["title"],
                company=raw["company"],
                location=raw["location"],
                work_type=raw.get("work_type", "remote"),
                experience_level=raw.get("experience_level", "any"),
                job_type=raw.get("job_type", "full-time"),
                description=raw["description"],
                skills=job_skills,
                interest_domains=domains,
                url=raw["url"],
                source=raw["source"],
                data_mode=job_data_mode,
                posted_date=raw.get("posted_date", "Recent"),
            )

            # Interest filtering: match ANY of user's selected interests
            relevance = 1.0
            if user_interest_set:
                job_domain_set = set(domains)
                overlap = user_interest_set.intersection(job_domain_set)
                if not overlap:
                    # No interest match -> exclude from personalized feed
                    continue
                relevance = self.classifier.calculate_interest_relevance(domains, list(user_interest_set))

            # Resume matching via existing MatchingEngine
            if resume_skills and len(resume_skills) > 0:
                match_out = self.matching_engine.compare_skills(
                    resume_skills=resume_skills,
                    job_skills=job_skills,
                )
                match_pct = match_out["match_percentage"]

                # Optional threshold filter
                if min_match is not None and match_pct < min_match:
                    continue

                matched_names = [m["name"] for m in match_out["matched_skills"]]
                missing_names = [m["name"] for m in match_out["missing_skills"]]

                results.append(
                    JobMatchItem(
                        job=job_model,
                        match_percentage=match_pct,
                        matched_skills=matched_names,
                        missing_skills=missing_names,
                        interest_relevance=relevance,
                    )
                )
            else:
                # User has no resume -> do NOT show fake 0% match!
                results.append(
                    JobMatchItem(
                        job=job_model,
                        match_percentage=None,
                        matched_skills=[],
                        missing_skills=[],
                        interest_relevance=relevance,
                    )
                )

        # Ranking
        if resume_skills and len(resume_skills) > 0:
            results.sort(
                key=lambda x: (
                    x.match_percentage if x.match_percentage is not None else -1,
                    x.interest_relevance or 0.0,
                ),
                reverse=True,
            )
        else:
            results.sort(
                key=lambda x: (x.interest_relevance or 0.0),
                reverse=True,
            )

        source_label = (
            "Public Live Job Feeds (Greenhouse, Lever, Ashby, Jobicy)"
            if effective_mode == "live"
            else "Curated Development Job Provider"
        )

        return JobSearchResponse(
            success=True,
            total_jobs=len(results),
            results=results,
            source=source_label,
            data_mode=effective_mode,
        )

    def search_and_match(
        self,
        role: str = "",
        location: str = "",
        work_type: str = "any",
        experience_level: str = "any",
        job_type: str = "any",
        keywords: str = "",
        interests: Optional[List[str]] = None,
        resume_skills: Optional[List[str]] = None,
        min_match: Optional[int] = None,
        data_mode: Optional[str] = None,
    ) -> JobSearchResponse:
        """Backward-compatible search wrapper."""
        return self.get_recommended_jobs(
            interests=interests,
            role=role,
            location=location,
            work_type=work_type,
            experience_level=experience_level,
            job_type=job_type,
            search=keywords,
            resume_skills=resume_skills,
            min_match=min_match,
            data_mode=data_mode,
        )

    def get_job_details(self, job_id: str, resume_skills: Optional[List[str]] = None) -> Optional[JobMatchItem]:
        # Try active provider first, then fallback to both curated and live
        raw = self.provider.get_job_by_id(job_id)
        if not raw:
            raw = self.curated_provider.get_job_by_id(job_id)
        if not raw:
            raw = self.live_aggregator.get_job_by_id(job_id)
        if not raw:
            return None

        extracted = self.skill_extractor.extract_skills(raw["description"])
        job_skills = extracted["raw_skills"]

        domains = self.classifier.classify_job(
            title=raw["title"],
            description=raw["description"],
            skills=job_skills,
        )

        job_model = Job(
            id=raw["id"],
            title=raw["title"],
            company=raw["company"],
            location=raw["location"],
            work_type=raw.get("work_type", "remote"),
            experience_level=raw.get("experience_level", "any"),
            job_type=raw.get("job_type", "full-time"),
            description=raw["description"],
            skills=job_skills,
            interest_domains=domains,
            url=raw["url"],
            source=raw["source"],
            data_mode=raw.get("data_mode", "live"),
            posted_date=raw.get("posted_date", "Recent"),
        )

        if resume_skills and len(resume_skills) > 0:
            match_out = self.matching_engine.compare_skills(
                resume_skills=resume_skills,
                job_skills=job_skills,
            )
            return JobMatchItem(
                job=job_model,
                match_percentage=match_out["match_percentage"],
                matched_skills=[m["name"] for m in match_out["matched_skills"]],
                missing_skills=[m["name"] for m in match_out["missing_skills"]],
            )

        return JobMatchItem(job=job_model, match_percentage=None)
