"""Greenhouse Public Job Board Provider.

Aggregates legitimate published public jobs directly from company Greenhouse boards
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

# Canonical display names for known technical boards
BOARD_DISPLAY_NAMES = {
    "gitlab": "GitLab",
    "cloudflare": "Cloudflare",
    "figma": "Figma",
    "inmobi": "InMobi",
    "groww": "Groww",
    "canonical": "Canonical",
}


def clean_html(raw_html: str) -> str:
    """Safely strip HTML tags and decode HTML entities into clean readable text."""
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


def infer_work_type(location: str, title: str = "") -> str:
    text = f"{location} {title}".lower()
    if "remote" in text or "home based" in text:
        return "remote"
    if "hybrid" in text:
        return "hybrid"
    return "onsite" if location and "anywhere" not in text else "remote"


def format_iso_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None
    # e.g. "2026-09-14T16:01:39-04:00" -> "2026-09-14"
    return date_str[:10] if len(date_str) >= 10 else date_str


class GreenhouseJobProvider(BaseJobProvider):
    """Fetches real published jobs from configured Greenhouse public career boards."""

    def __init__(self, boards: Optional[List[str]] = None, timeout: float = 6.0, max_jobs_per_board: int = 20):
        if boards:
            self.boards = boards
        else:
            configured = settings.GREENHOUSE_COMPANIES
            self.boards = [b.strip().lower() for b in configured.split(",") if b.strip()]
        self.timeout = timeout
        self.max_jobs_per_board = max_jobs_per_board

    def _fetch_board_jobs(self, board: str) -> List[Dict[str, Any]]:
        cache_key = f"greenhouse:{board}:{self.max_jobs_per_board}"
        cached = job_cache.get(cache_key)
        if cached is not None:
            return cached

        url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
        headers = {"User-Agent": "ResumeFit-JobFinder/1.0"}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url, headers=headers)
                if resp.status_code != 200:
                    logger.warning("Greenhouse board '%s' returned status %d", board, resp.status_code)
                    return []
                data = resp.json()
                raw_list = data.get("jobs", [])
        except httpx.TimeoutException:
            logger.warning("Greenhouse request timed out for board '%s'", board)
            return []
        except Exception as e:
            logger.warning("Greenhouse error fetching board '%s': %s", board, e)
            return []

        company_name = BOARD_DISPLAY_NAMES.get(board, board.title())
        normalized_jobs = []

        for item in raw_list:
            if len(normalized_jobs) >= self.max_jobs_per_board:
                break
            job_id_num = item.get("id")
            title = (item.get("title") or "").strip()
            if not job_id_num or not title:
                continue

            raw_loc = item.get("location", {})
            loc_str = raw_loc.get("name", "").strip() if isinstance(raw_loc, dict) else str(raw_loc).strip()
            abs_url = item.get("absolute_url")
            if not abs_url or not abs_url.startswith("http"):
                continue

            raw_content = item.get("content") or ""
            desc = clean_html(raw_content)
            if not desc:
                desc = f"{title} role at {company_name}. Location: {loc_str or 'Remote'}."

            updated_at = item.get("updated_at") or item.get("first_published")
            posted_date = format_iso_date(updated_at)

            work_type = infer_work_type(loc_str, title)

            norm_job = {
                "id": f"gh-{board}-{job_id_num}",
                "title": title,
                "company": company_name,
                "location": loc_str or "Remote",
                "work_type": work_type,
                "experience_level": "any",
                "job_type": "full-time",
                "description": desc,
                "url": abs_url,
                "source": f"Greenhouse ({company_name})",
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
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.boards) or 1) as executor:
            futures = [executor.submit(self._fetch_board_jobs, b) for b in self.boards]
            for f in concurrent.futures.as_completed(futures):
                try:
                    all_jobs.extend(f.result())
                except Exception as err:
                    logger.warning("Error fetching board in thread: %s", err)

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
                # Special matching for common tech hubs
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
        for board in self.boards:
            jobs = self._fetch_board_jobs(board)
            for j in jobs:
                if j["id"] == job_id:
                    return dict(j)
        return None
