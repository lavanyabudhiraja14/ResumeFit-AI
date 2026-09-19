"""API route for resume upload and skill extraction."""

from fastapi import APIRouter, File, UploadFile, status
from app.services.parsers.document_service import DocumentService
from app.services.nlp.extractor import SkillExtractor
from app.services.quality.scorer import ResumeQualityScorer
from app.schemas.resume import ResumeAnalysisResponse

router = APIRouter(prefix="/resume", tags=["Resume"])
document_service = DocumentService()
skill_extractor = SkillExtractor()
quality_scorer = ResumeQualityScorer()


@router.post(
    "/analyze",
    response_model=ResumeAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload and extract technical skills from resume document",
)
async def analyze_resume(file: UploadFile = File(...)):
    """
    Accepts PDF, DOCX, JPG, JPEG, or PNG resumes.
    Performs file validation, text extraction (with OCR for images),
    and extracts normalized technical skills grouped by category.
    """
    parsed_doc = await document_service.parse_resume_file(file)
    extracted = skill_extractor.extract_skills(parsed_doc["text"])
    quality_result = quality_scorer.evaluate(parsed_doc["text"], extracted["raw_skills"])

    return ResumeAnalysisResponse(
        success=True,
        filename=parsed_doc["filename"],
        extension=parsed_doc["extension"],
        file_size=parsed_doc["file_size"],
        total_skills_count=extracted["total_count"],
        skills_by_category=extracted["skills_by_category"],
        raw_skills=extracted["raw_skills"],
        page_count=parsed_doc.get("page_count", 1),
        character_count=parsed_doc.get("character_count", 0),
        word_count=parsed_doc.get("word_count", 0),
        raw_text=parsed_doc["text"],
        quality=quality_result,
    )
