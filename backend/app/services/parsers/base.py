"""Abstract base class for document parsers."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseParser(ABC):
    """Abstract interface that all file parsers must implement."""

    @abstractmethod
    def extract_text(self, file_bytes: bytes, filename: str = "") -> Dict[str, Any]:
        """
        Extract clean text and structural metadata from raw document bytes.

        Returns:
            Dict containing:
                - text: Extracted plain text string
                - page_count: Number of pages (or 1 for images/single docs)
                - character_count: Total characters extracted
                - word_count: Total words extracted
                - is_scanned: Whether the document appears to be a scanned image
                - metadata: Any format-specific metadata
        """
        pass
