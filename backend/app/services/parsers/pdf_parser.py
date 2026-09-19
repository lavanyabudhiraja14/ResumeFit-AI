"""PDF parser implementation using PyMuPDF (fitz) with OCR fallback for scanned pages."""

import io
from typing import Any, Dict
import fitz  # PyMuPDF
from app.services.parsers.base import BaseParser
from app.core.security import FileValidationError


class PDFParser(BaseParser):
    def __init__(self, image_parser: BaseParser = None):
        self.image_parser = image_parser

    def extract_text(self, file_bytes: bytes, filename: str = "") -> Dict[str, Any]:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            raise FileValidationError(f"Failed to parse PDF: Corrupted or unreadable format ({str(e)})")

        try:
            page_count = len(doc)
            if page_count == 0:
                raise FileValidationError("PDF contains no pages.")

            extracted_pages = []
            total_chars = 0

            for page_num in range(page_count):
                page = doc[page_num]
                page_text = page.get_text("text")
                extracted_pages.append(page_text.strip())
                total_chars += len(page_text.strip())

            full_text = "\n\n".join(p for p in extracted_pages if p)
            is_scanned = total_chars < 50

            # If document appears to be scanned image PDF and image_parser is provided, attempt OCR on page pixmaps
            if is_scanned and self.image_parser:
                ocr_texts = []
                for page_num in range(page_count):
                    page = doc[page_num]
                    pix = page.get_pixmap(dpi=150)
                    img_bytes = pix.tobytes("png")
                    try:
                        ocr_res = self.image_parser.extract_text(img_bytes, filename=f"page_{page_num+1}.png")
                        if ocr_res["text"]:
                            ocr_texts.append(ocr_res["text"])
                    except Exception:
                        pass
                if ocr_texts:
                    full_text = "\n\n".join(ocr_texts)
                    total_chars = len(full_text)

            words = full_text.split()
            word_count = len(words)

            return {
                "text": full_text,
                "page_count": page_count,
                "character_count": total_chars,
                "word_count": word_count,
                "is_scanned": is_scanned,
                "metadata": {
                    "format": "pdf",
                    "title": doc.metadata.get("title", ""),
                    "author": doc.metadata.get("author", ""),
                },
            }
        finally:
            doc.close()
