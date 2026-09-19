"""Ashby Public Job Board Provider.

Aggregates legitimate published public jobs directly from company Ashby boards
without requiring any API keys.
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

ASHBY_DISPLAY_NAMES = {
    "openai": "OpenAI",
    "linear": "Linear",
    "ramp": "Ramp",
    "sentry": "Sentry",
    "replit": "Replit",
    "notion": "Notion",
}


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


def infer_work_type(is_remote: bool, workplace_type: str, location: str, title: str = "") -> str:
    if is_remote:
        return "remote"
    wpt = (workplace_type or "").lower()
    if wpt in ["remote", "hybrid", "onsite"]:
        return wpt
    text = f"{location} {title}".lower()
    if "remote" in text:
        return "remote"
    if "hybrid" in text:
        return "hybrid"
    return "onsite" if location else "remote"


def format_iso_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None
    return date_str[:10] if len(date_str) >= 10 else date_str


class AshbyJobProvider(BaseJobProvider):
    """Fetches real published jobs from configured Ashby public company job boards."""

    def __init__(self, companies: Optional[List[str]] = None, timeout: float = 6.0, max_jobs_per_company: int = 20):
        if companies:
            self.companies = companies
        else:
            configured = settings.ASHBY_COMPANIES
            self.companies = [c.strip().lower() for c in configured.split(",") if c.strip()]
        self.timeout = timeout
        self.max_jobs_per_company = max_jobs_per_company

    def _fetch_company_jobs(self, slug: str) -> List[Dict[str, Any]]:
        cache_key = f"ashby:{slug}:{self.max_jobs_per_company}"
        cached = job_cache.get(cache_key)
        if cached is not None:
            return cached

        url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
        headers = {"User-Agent": "ResumeFit-JobFinder/1.0"}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url, headers=headers)
                if resp.status_code != 200:
                    logger.warning("Ashby company '%s' returned status %d", slug, resp.status_code)
                    return []
                data = resp.json()
                raw_list = data.get("jobs", [])
        except httpx.TimeoutException:
            logger.warning("Ashby request timed out for company '%s'", slug)
            return []
        except Exception as e:
            logger.warning("Ashby error fetching company '%s': %s", slug, e)
            return []

        company_name = ASHBY_DISPLAY_NAMES.get(slug, slug.title())
        normalized_jobs = []

        for item in raw_list:
            if len(normalized_jobs) >= self.max_jobs_per_company:
                break
            job_id = item.get("id")
            title = (item.get("title") or "").strip()
            if not job_id or not title:
                continue

            job_url = item.get("jobUrl")
            if not job_url or not job_url.startswith("http"):
                continue

            loc_str = (item.get("location") or "").strip()
            is_remote = bool(item.get("isRemote", False))
            workplace_type = item.get("workplaceType", "")
            work_type = infer_work_type(is_remote, workplace_type, loc_str, title)

            emp_type = (item.get("employmentType") or "FullTime").lower()
            job_type = "internship" if "intern" in emp_type else ("contract" if "contract" in emp_type else "full-time")

            desc = item.get("descriptionPlain") or ""
            if not desc:
                desc = clean_html(item.get("descriptionHtml") or "")
            if not desc:
                desc = f"{title} opportunity at {company_name}. Location: {loc_str or 'Remote'}."

            posted_date = format_iso_date(item.get("publishedAt"))

            norm_job = {
                "id": f"ashby-{slug}-{job_id}",
                "title": title,
                "company": company_name,
                "location": loc_str or "Remote",
                "work_type": work_type,
                "experience_level": "any",
                "job_type": job_type,
                "description": desc.strip(),
                "url": job_url,
                "source": f"Ashby ({company_name})",
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
        import concurrent.futures

        all_jobs: List[Dict[str, Any]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.companies) or 1) as executor:
            futures = [executor.submit(self._fetch_company_jobs, c) for c in self.companies]
            for f in concurrent.futures.as_completed(futures):
                try:
                    all_jobs.extend(f.result())
                except Exception as err:
                    logger.warning("Error fetching ashby company in thread: %s", err)

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
                if loc_q == "remote" and ("remote" in loc_lower or job["work_type"] == "remote"):
                    pass
                elif loc_q in loc_lower:
                    pass
                elif loc_q in ["bengaluru", "bangalore"] and ("bengaluru" in loc_lower or "bangalore" in loc_lower):
                    pass
                elif loc_q in ["delhi", "delhi ncr", "noida", "gurgaon", "gurugram"] and any(
                    city in loc_lower for city in ["delhi", "noida", "gurgaon", "gurugram"]
                ):
                    pass
                else:
                    continue
            if wt_q != "any" and wt_q != job.get("work_type", "remote").lower():
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
        for slug in self.companies:
            jobs = self._fetch_company_jobs(slug)
            for j in jobs:
                if j["id"] == job_id:
                    return dict(j)
        return None
