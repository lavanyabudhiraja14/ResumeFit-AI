"""Live Job Aggregator coordinating multiple public job providers with fault tolerance and deduplication."""

import logging
import re
import urllib.parse
from typing import Any, Dict, List, Optional, Set
from app.services.job_finder.providers.base import BaseJobProvider
from app.services.job_finder.providers.greenhouse_provider import GreenhouseJobProvider
from app.services.job_finder.providers.lever_provider import LeverJobProvider
from app.services.job_finder.providers.ashby_provider import AshbyJobProvider
from app.services.job_finder.providers.public_feed_provider import PublicFeedJobProvider

logger = logging.getLogger(__name__)


def canonicalize_url(url: str) -> str:
    """Normalize a job URL by removing tracking query parameters and trailing slashes."""
    if not url:
        return ""
    try:
        parsed = urllib.parse.urlparse(url)
        # Strip common tracking query params
        q_params = urllib.parse.parse_qsl(parsed.query)
        clean_params = [
            (k, v)
            for k, v in q_params
            if not k.lower().startswith("utm_") and k.lower() not in ["gh_jid", "ref", "source"]
        ]
        clean_query = urllib.parse.urlencode(clean_params)
        clean_path = parsed.path.rstrip("/")
        return urllib.parse.urlunparse(
            (parsed.scheme.lower(), parsed.netloc.lower(), clean_path, parsed.params, clean_query, "")
        )
    except Exception:
        return url.strip().lower().rstrip("/")


def make_composite_key(company: str, title: str, location: str) -> str:
    """Create a normalized key for duplicate detection when URLs differ."""
    c = company.lower()
    c = re.sub(r"\b(inc|llc|ltd|corp|corporation)\b", "", c)
    c = re.sub(r"[^a-z0-9]", "", c)
    t = re.sub(r"[^a-z0-9]", "", title.lower())
    l = re.sub(r"[^a-z0-9]", "", location.lower())
    return f"{c}::{t}::{l}"


class LiveJobAggregator(BaseJobProvider):
    """
    Coordinates Greenhouse, Lever, Ashby, and Public Feed providers.
    Ensures that failure of one provider does not take down the feed.
    Performs deterministic deduplication across sources.
    """

    def __init__(self, providers: Optional[List[BaseJobProvider]] = None):
        if providers is not None:
            self.providers = providers
        else:
            self.providers = [
                GreenhouseJobProvider(),
                LeverJobProvider(),
                AshbyJobProvider(),
                PublicFeedJobProvider(),
            ]

    def search_jobs(
        self,
        role: str = "",
        location: str = "",
        work_type: str = "any",
        experience_level: str = "any",
        job_type: str = "any",
        keywords: str = "",
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        import concurrent.futures

        raw_jobs: List[Dict[str, Any]] = []

        def query_single_provider(provider: BaseJobProvider) -> List[Dict[str, Any]]:
            provider_name = provider.__class__.__name__
            try:
                return provider.search_jobs(
                    role=role,
                    location=location,
                    work_type=work_type,
                    experience_level=experience_level,
                    job_type=job_type,
                    keywords=keywords,
                    **kwargs,
                )
            except Exception as e:
                logger.error("Provider '%s' failed during search: %s", provider_name, e)
                return []

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.providers) or 1) as executor:
            futures = [executor.submit(query_single_provider, p) for p in self.providers]
            for f in futures:
                raw_jobs.extend(f.result())

        # Deterministic deduplication
        deduped: List[Dict[str, Any]] = []
        seen_urls: Set[str] = set()
        seen_composite: Set[str] = set()

        for job in raw_jobs:
            c_url = canonicalize_url(job.get("url", ""))
            comp_key = make_composite_key(
                job.get("company", ""),
                job.get("title", ""),
                job.get("location", ""),
            )

            if c_url and c_url in seen_urls:
                continue
            if comp_key in seen_composite:
                continue

            if c_url:
                seen_urls.add(c_url)
            seen_composite.add(comp_key)
            deduped.append(job)

        return deduped

    def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        for provider in self.providers:
            try:
                job = provider.get_job_by_id(job_id)
                if job:
                    return job
            except Exception as e:
                logger.error("Provider '%s' failed in get_job_by_id: %s", provider.__class__.__name__, e)
        return None
