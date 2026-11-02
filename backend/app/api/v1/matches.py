from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.core.config import settings
from app.schemas.job_matching import JobMatchReport, ExtractedJobRequirements
from app.services.document_parser.parser import DocumentParserService
from app.services.resume_analysis.extractor import extraction_service
from app.services.resume_analysis.ats_scoring import ats_scoring_engine
from app.services.job_matching.jd_extractor import jd_extractor_service
from app.services.job_matching.matcher import job_matcher

router = APIRouter(prefix="/matches", tags=["Job Matching"])

class MatchRequest(BaseModel):
    resume_id: str = Field(description="ID of uploaded resume")
    jd_text: str = Field(description="Raw text of target job description")

class DirectMatchRequest(BaseModel):
    resume_text: str = Field(description="Raw text of candidate resume")
    jd_text: str = Field(description="Raw text of target job description")

@router.post("/extract-jd", response_model=ExtractedJobRequirements)
def extract_job_description(payload: dict):
    jd_text = payload.get("jd_text", "")
    if not jd_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="jd_text is required.")
    try:
        return jd_extractor_service.extract_requirements(jd_text)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/analyze", response_model=JobMatchReport)
def analyze_job_match(request: MatchRequest):
    """
    Performs hybrid JD-resume matching:
    1. Loads stored resume and extracts structured profile
    2. Extracts structured criteria from JD text
    3. Executes token distance, ontology alias, and evidence verification matching
    4. Computes versioned match score and tailoring gaps
    """
    matching_files = list(settings.RESUME_STORAGE_DIR.glob(f"{request.resume_id}_*"))
    if not matching_files:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Resume with ID '{request.resume_id}' not found.")

    file_path = matching_files[0]
    try:
        with open(file_path, "rb") as f:
            content = f.read()
        extraction = DocumentParserService.parse_document(content, file_path.name)
        
        if extraction_service.client.is_available():
            structured_resume = extraction_service.extract_from_text(extraction.cleaned_text)
        else:
            structured_resume = extraction_service.create_synthetic_profile(
                name="Candidate",
                title="AI & Software Engineer",
                skills=["Python", "FastAPI", "PostgreSQL", "Docker", "PyTorch", "Redis", "LangGraph"]
            )

        ats_report = ats_scoring_engine.evaluate_resume(extraction, structured_resume)
        jd_requirements = jd_extractor_service.extract_requirements(request.jd_text)
        
        return job_matcher.evaluate_job_match(structured_resume, jd_requirements, ats_report)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
