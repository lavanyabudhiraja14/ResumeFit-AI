"""Abstract base provider interface for job search backends."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseJobProvider(ABC):
    @abstractmethod
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
        """
        Query the underlying job data source and return a list of raw job dictionaries.
        """
        pass

    @abstractmethod
    def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific job by unique ID."""
        pass
