"""Security and file validation utilities."""

import os
from fastapi import HTTPException, UploadFile, status
from app.core.constants import (
    MAX_FILE_SIZE_BYTES,
    SUPPORTED_EXTENSIONS,
    MAGIC_BYTES,
)


class FileValidationError(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


async def validate_uploaded_file(file: UploadFile) -> bytes:
    """
    Validates uploaded file for:
    - Non-empty filename and supported extension
    - Non-empty content and size <= MAX_FILE_SIZE_BYTES
    - Header magic bytes matching declared format
    """
    if not file.filename:
        raise FileValidationError("No filename provided.")

    filename = file.filename.strip()
    _, ext = os.path.splitext(filename.lower())

    if ext not in SUPPORTED_EXTENSIONS:
        allowed = ", ".join(sorted(list(SUPPORTED_EXTENSIONS)))
        raise FileValidationError(
            f"Unsupported file format '{ext}'. Supported formats: {allowed}"
        )

    # Read content safely into memory buffer
    content = await file.read()
    file_size = len(content)

    if file_size == 0:
        raise FileValidationError("Uploaded file is empty.")

    if file_size > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
        raise FileValidationError(
            f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum limit of {max_mb} MB.",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )

    # Reset cursor in case file is read elsewhere
    await file.seek(0)

    # Magic byte verification
    verify_magic_bytes(content, ext)

    return content


def verify_magic_bytes(content: bytes, ext: str) -> None:
    """Verifies that file content matches expected format header bytes."""
    header = content[:16]

    if ext == ".pdf":
        if not header.startswith(MAGIC_BYTES["pdf"]):
            raise FileValidationError(
                "File has .pdf extension but invalid PDF header signatures. File may be corrupted or spoofed."
            )
    elif ext == ".docx":
        if not header.startswith(MAGIC_BYTES["docx"]):
            raise FileValidationError(
                "File has .docx extension but invalid DOCX/ZIP signature. File may be corrupted or spoofed."
            )
    elif ext in {".jpg", ".jpeg"}:
        if not header.startswith(MAGIC_BYTES["jpeg"]):
            raise FileValidationError(
                "File has JPEG extension but invalid JPEG signature. File may be corrupted or spoofed."
            )
    elif ext == ".png":
        if not header.startswith(MAGIC_BYTES["png"]):
            raise FileValidationError(
                "File has .png extension but invalid PNG signature. File may be corrupted or spoofed."
            )
