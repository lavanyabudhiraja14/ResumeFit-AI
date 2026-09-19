"""Public Remote Job Feed Provider (Jobicy).

Aggregates legitimate published remote developer and engineering jobs from Jobicy's
public feed API without requiring an API key. Includes clear source attribution.
"""

import html
import logging
import re
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings
from app.services.job_finder.providers.base import BaseJobProvider
from app.services.job_finder.cache import job_cache

logger = logging.getLogger(__name__)


def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    text = html.unescape(raw_html)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</li>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def format_iso_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None
    return date_str[:10] if len(date_str) >= 10 else date_str


class PublicFeedJobProvider(BaseJobProvider):
    """Fetches real published remote jobs from legitimate public Jobicy feed."""

    def __init__(self, count: int = 50, timeout: float = 6.0):
        self.count = count
        self.timeout = timeout

    def _fetch_feed_jobs(self) -> List[Dict[str, Any]]:
        cache_key = f"public_feed:jobicy:{self.count}"
        cached = job_cache.get(cache_key)
        if cached is not None:
            return cached

        if not settings.PUBLIC_FEED_ENABLED:
            return []

        url = f"https://jobicy.com/api/v2/remote-jobs?count={self.count}&industry=engineering"
        headers = {"User-Agent": "ResumeFit-JobFinder/1.0"}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url, headers=headers)
                if resp.status_code != 200:
                    logger.warning("Jobicy feed returned status %d", resp.status_code)
                    return []
                data = resp.json()
                raw_list = data.get("jobs", [])
        except httpx.TimeoutException:
            logger.warning("Jobicy feed request timed out")
            return []
        except Exception as e:
            logger.warning("Jobicy feed error: %s", e)
            return []

        normalized_jobs = []
        for item in raw_list:
            raw_id = item.get("id")
            title = (item.get("jobTitle") or "").strip()
            company = (item.get("companyName") or "").strip()
            url_str = item.get("url")

            if not raw_id or not title or not company:
                continue
            if not url_str or not url_str.startswith("http"):
                continue

            geo = (item.get("jobGeo") or "Remote").strip()
            location = f"Remote ({geo})" if geo.lower() != "remote" else "Remote"

            # Parse job types
            jt_raw = item.get("jobType")
            if isinstance(jt_raw, list) and jt_raw:
                jt_str = jt_raw[0].lower()
            elif isinstance(jt_raw, str):
                jt_str = jt_raw.lower()
            else:
                jt_str = "full-time"

            job_type = "internship" if "intern" in jt_str else ("part-time" if "part" in jt_str else "full-time")

            # Description
            raw_desc = item.get("jobDescription") or item.get("jobExcerpt") or ""
            desc = clean_html(raw_desc)
            if not desc:
                desc = f"{title} remote role at {company}."

            posted_date = format_iso_date(item.get("pubDate"))

            norm_job = {
                "id": f"jobicy-{raw_id}",
                "title": title,
                "company": company,
                "location": location,
                "work_type": "remote",
                "experience_level": "any",
                "job_type": job_type,
                "description": desc.strip(),
                "url": url_str,
                "source": "Jobicy",
                "data_mode": "live",
                "posted_date": posted_date or "Recent",
            }
            normalized_jobs.append(norm_job)

        job_cache.set(cache_key, normalized_jobs)
        return normalized_jobs

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
        all_jobs = self._fetch_feed_jobs()

        role_q = role.lower().strip()
        loc_q = location.lower().strip()
        wt_q = work_type.lower().strip()
        exp_q = experience_level.lower().strip()
        jt_q = job_type.lower().strip()
        kw_q = keywords.lower().strip()

        filtered = []
        for job in all_jobs:
            if role_q and role_q not in job["title"].lower() and role_q not in job["description"].lower():
                continue
            if loc_q and loc_q != "all":
                loc_lower = job["location"].lower()
                if loc_q == "remote":
                    pass
                elif loc_q in loc_lower:
                    pass
                else:
                    continue
            if wt_q != "any" and wt_q != "remote":
                continue
            if exp_q != "any" and exp_q != job.get("experience_level", "any").lower():
                continue
            if jt_q != "any" and jt_q != job.get("job_type", "full-time").lower():
                continue
            if kw_q and (kw_q not in job["description"].lower() and kw_q not in job["title"].lower()):
                continue
            filtered.append(dict(job))

        return filtered

    def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        jobs = self._fetch_feed_jobs()
        for j in jobs:
            if j["id"] == job_id:
                return dict(j)
        return None
