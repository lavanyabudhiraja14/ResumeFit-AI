"""Constants used across ResumeFit AI backend."""

from typing import Dict, Set

# File limits
MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

# Supported Extensions
SUPPORTED_EXTENSIONS: Set[str] = {
    ".pdf",
    ".docx",
    ".jpg",
    ".jpeg",
    ".png",
}

# Supported Content Types (MIME)
SUPPORTED_MIME_TYPES: Set[str] = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/jpeg",
    "image/png",
    "image/jpg",
}

# Magic byte signatures for file verification
MAGIC_BYTES: Dict[str, bytes] = {
    "pdf": b"%PDF",
    "docx": b"PK\x03\x04",
    "jpeg": b"\xff\xd8\xff",
    "png": b"\x89PNG\r\n\x1a\n",
}
