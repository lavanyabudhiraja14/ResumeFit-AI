"""Image OCR parser implementation using Pillow and pytesseract."""

import io
import shutil
from typing import Any, Dict
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
from app.services.parsers.base import BaseParser
from app.core.security import FileValidationError


def is_tesseract_available() -> bool:
    """Check if tesseract binary is available in the system PATH."""
    return shutil.which("tesseract") is not None


class ImageParser(BaseParser):
    def __init__(self):
        self.available = is_tesseract_available()

    def extract_text(self, file_bytes: bytes, filename: str = "") -> Dict[str, Any]:
        if not self.available:
            raise FileValidationError(
                "OCR processing is unavailable because the Tesseract OCR engine is not installed on the server. "
                "Please upload a standard text PDF or DOCX resume, or install Tesseract on macOS via: brew install tesseract"
            )

        try:
            image = Image.open(io.BytesIO(file_bytes))
        except Exception as e:
            raise FileValidationError(f"Invalid or corrupted image file: {str(e)}")

        try:
            # Preprocessing: Convert to grayscale and increase contrast
            gray = ImageOps.grayscale(image)
            enhancer = ImageEnhance.Contrast(gray)
            processed_image = enhancer.enhance(1.8)

            # Perform OCR
            text = pytesseract.image_to_string(processed_image)
            cleaned_text = text.strip()
            words = cleaned_text.split()

            return {
                "text": cleaned_text,
                "page_count": 1,
                "character_count": len(cleaned_text),
                "word_count": len(words),
                "is_scanned": True,
                "metadata": {
                    "format": image.format.lower() if image.format else "image",
                    "dimensions": f"{image.width}x{image.height}",
                },
            }
        except pytesseract.TesseractNotFoundError:
            self.available = False
            raise FileValidationError(
                "Tesseract executable not found. Please install Tesseract (e.g. `brew install tesseract`) to enable image resume parsing."
            )
        except Exception as e:
            raise FileValidationError(f"Failed to extract text from image: {str(e)}")
