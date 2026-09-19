"""Tests for document parsers, security validation, and magic bytes."""

import io
import pytest
from fastapi import UploadFile
from app.services.parsers.pdf_parser import PDFParser
from app.services.parsers.docx_parser import DOCXParser
from app.services.parsers.document_service import DocumentService
from app.core.security import validate_uploaded_file, FileValidationError


def test_pdf_parser_extracts_text(sample_pdf_bytes):
    parser = PDFParser()
    result = parser.extract_text(sample_pdf_bytes, filename="test.pdf")

    assert result["page_count"] == 1
    assert "John Doe" in result["text"]
    assert "FastAPI" in result["text"]
    assert "Docker" in result["text"]
    assert result["character_count"] > 100
    assert result["word_count"] > 20
    assert not result["is_scanned"]


def test_docx_parser_extracts_paragraphs_and_tables(sample_docx_bytes):
    parser = DOCXParser()
    result = parser.extract_text(sample_docx_bytes, filename="test.docx")

    assert "Jane Smith" in result["text"]
    assert "Java" in result["text"]
    assert "PostgreSQL" in result["text"]
    assert "AWS" in result["text"]
    assert result["metadata"]["table_count"] == 1


@pytest.mark.asyncio
async def test_validate_unsupported_file_extension():
    fake_file = UploadFile(
        filename="resume.txt",
        file=io.BytesIO(b"Some plain text resume"),
    )
    with pytest.raises(FileValidationError) as exc:
        await validate_uploaded_file(fake_file)
    assert "Unsupported file format" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_validate_empty_file():
    empty_file = UploadFile(
        filename="empty.pdf",
        file=io.BytesIO(b""),
    )
    with pytest.raises(FileValidationError) as exc:
        await validate_uploaded_file(empty_file)
    assert "empty" in str(exc.value.detail).lower()


@pytest.mark.asyncio
async def test_validate_corrupted_pdf_magic_bytes():
    corrupted = UploadFile(
        filename="fake.pdf",
        file=io.BytesIO(b"NOT_A_REAL_PDF_HEADER_JUST_RANDOM_TEXT"),
    )
    with pytest.raises(FileValidationError) as exc:
        await validate_uploaded_file(corrupted)
    assert "invalid PDF header" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_document_service_pdf_pipeline(sample_pdf_bytes):
    service = DocumentService()
    file = UploadFile(
        filename="engineer_resume.pdf",
        file=io.BytesIO(sample_pdf_bytes),
    )
    result = await service.parse_resume_file(file)

    assert result["filename"] == "engineer_resume.pdf"
    assert result["extension"] == ".pdf"
    assert "Python" in result["text"]
    assert result["character_count"] > 50


@pytest.mark.asyncio
async def test_document_service_docx_pipeline(sample_docx_bytes):
    service = DocumentService()
    file = UploadFile(
        filename="engineer_resume.docx",
        file=io.BytesIO(sample_docx_bytes),
    )
    result = await service.parse_resume_file(file)

    assert result["filename"] == "engineer_resume.docx"
    assert result["extension"] == ".docx"
    assert "Jane Smith" in result["text"]
    assert "PostgreSQL" in result["text"]
