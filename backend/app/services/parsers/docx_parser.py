"""DOCX parser implementation using python-docx."""

import io
from typing import Any, Dict
import docx
from app.services.parsers.base import BaseParser
from app.core.security import FileValidationError


class DOCXParser(BaseParser):
    def extract_text(self, file_bytes: bytes, filename: str = "") -> Dict[str, Any]:
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
        except Exception as e:
            raise FileValidationError(f"Failed to parse DOCX: Corrupted or invalid Word document ({str(e)})")

        extracted_lines = []

        # 1. Extract paragraphs
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                extracted_lines.append(text)

        # 2. Extract tables (resumes frequently layout skills in tables)
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    # Deduplicate repeated cell spans
                    unique_cells = []
                    for c in row_cells:
                        if not unique_cells or c != unique_cells[-1]:
                            unique_cells.append(c)
                    extracted_lines.append(" | ".join(unique_cells))

        full_text = "\n".join(extracted_lines)
        words = full_text.split()

        return {
            "text": full_text,
            "page_count": 1,  # DOCX does not natively store pre-computed page counts without rendering engine
            "character_count": len(full_text),
            "word_count": len(words),
            "is_scanned": False,
            "metadata": {
                "format": "docx",
                "paragraph_count": len(doc.paragraphs),
                "table_count": len(doc.tables),
            },
        }
