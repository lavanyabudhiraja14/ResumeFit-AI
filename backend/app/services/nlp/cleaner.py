"""Text cleaning and normalization utility for raw resume and job text."""

import re
import unicodedata


def clean_text(text: str) -> str:
    """
    Cleans raw document or job description text:
    - Normalizes Unicode characters to standard NFKC
    - Removes unprintable control characters
    - Fixes hyphenated words split across lines
    - Normalizes diverse bullet characters
    - Standardizes whitespace while preserving paragraphs
    """
    if not text:
        return ""

    # 1. Unicode NFKC normalization (fixes ligatures like 'fi' -> 'fi', 'fl' -> 'fl')
    text = unicodedata.normalize("NFKC", text)

    # 2. Remove null bytes and non-printable control characters (except newline, tab, cr)
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    # 3. Join hyphenated words split across line breaks: e.g. "develo-\npment" -> "development"
    text = re.sub(r"(\b\w+)-\n(\w+\b)", r"\1\2", text)

    # 4. Standardize diverse bullet characters to standard bullet or newline
    text = re.sub(r"[•●▪■◆★‣►–—]+", "\n• ", text)

    # 5. Normalize multiple spaces on the same line to single space
    text = re.sub(r"[ \t]+", " ", text)

    # 6. Normalize 3+ newlines to double newline
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    return text.strip()
