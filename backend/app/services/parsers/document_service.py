"""Coordinator service for document validation and text parsing."""

import os
from typing import Any, Dict
from fastapi import UploadFile
from app.core.security import validate_uploaded_file, FileValidationError
from app.services.parsers.pdf_parser import PDFParser
from app.services.parsers.docx_parser import DOCXParser
from app.services.parsers.image_parser import ImageParser, is_tesseract_available


class DocumentService:
    def __init__(self):
        self.image_parser = ImageParser()
        self.pdf_parser = PDFParser(image_parser=self.image_parser)
        self.docx_parser = DOCXParser()

    async def parse_resume_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Validates and parses uploaded resume file.
        Returns metadata and extracted plain text.
        """
        content = await validate_uploaded_file(file)
        filename = file.filename.strip() if file.filename else "unknown"
        _, ext = os.path.splitext(filename.lower())

        if ext == ".pdf":
            result = self.pdf_parser.extract_text(content, filename=filename)
        elif ext == ".docx":
            result = self.docx_parser.extract_text(content, filename=filename)
        elif ext in {".jpg", ".jpeg", ".png"}:
            result = self.image_parser.extract_text(content, filename=filename)
        else:
            raise FileValidationError(f"Unsupported extension '{ext}'")

        if not result["text"].strip():
            raise FileValidationError(
                "No readable text could be extracted from the uploaded document. "
                "Please verify that the document is not empty or password-protected."
            )

        return {
            "filename": filename,
            "extension": ext,
            "file_size": len(content),
            "text": result["text"],
            "page_count": result.get("page_count", 1),
            "character_count": result.get("character_count", len(result["text"])),
            "word_count": result.get("word_count", len(result["text"].split())),
            "is_scanned": result.get("is_scanned", False),
            "metadata": result.get("metadata", {}),
        }
