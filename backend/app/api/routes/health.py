"""Health check and status API routes."""

from fastapi import APIRouter
from app.core.config import settings
from app.services.parsers.image_parser import is_tesseract_available

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Health check endpoint indicating server and subsystem availability."""
    ocr_ready = is_tesseract_available()
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ocr_available": ocr_ready,
    }


@router.get("/")
def root():
    """Root endpoint providing service metadata."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs_url": "/docs",
        "health_url": f"{settings.API_V1_STR}/health",
    }
