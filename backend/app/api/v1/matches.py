from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.core.config import settings
from app.schemas.job_matching import JobMatchReport, ExtractedJobRequirements
from app.schemas.designation_matching import DesignationMatchReport, DesignationListResponse
from app.services.document_parser.parser import DocumentParserService
from app.services.resume_analysis.extractor import extraction_service
from app.services.resume_analysis.ats_scoring import ats_scoring_engine
from app.services.job_matching.jd_extractor import jd_extractor_service
from app.services.job_matching.matcher import job_matcher
from app.services.job_matching.designation_matcher import designation_matcher_service

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
        
        structured_resume = None
        if extraction_service.client.is_available():
            try:
                structured_resume = extraction_service.extract_from_text(extraction.cleaned_text)
            except Exception:
                structured_resume = None

        if not structured_resume:
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


# ─────────────────────────────────────────────────────────────────────────────
# Designation Benchmark Matching Endpoints
# ─────────────────────────────────────────────────────────────────────────────

class DesignationMatchRequest(BaseModel):
    """Request body for designation benchmark matching."""
    resume_id: str = Field(description="ID of the previously uploaded resume file")
    role_id: str = Field(
        description=(
            "Role identifier to match against. "
            "Call GET /api/v1/matches/designations to see available role IDs."
        )
    )


@router.get("/designations", response_model=DesignationListResponse)
def list_available_designations():
    """
    Returns all available curated designation profiles.

    Use the returned role_id values in POST /api/v1/matches/designation.

    DISCLAIMER: Profiles are curated benchmarks, not sourced from any specific
    employer's job description. They represent general market expectations
    for the Indian tech hiring market (2025-2026).
    """
    return designation_matcher_service.get_available_roles()


@router.post("/designation", response_model=DesignationMatchReport)
def match_against_designation(request: DesignationMatchRequest):
    """
    Matches the candidate's uploaded resume against a curated role designation profile.

    Steps:
    1. Loads the uploaded resume file by resume_id.
    2. Parses and extracts structured resume data.
    3. Loads the curated role profile for the given role_id.
    4. Delegates to HybridJobMatcher for scoring and evidence collection.
    5. Returns a DesignationMatchReport with scores, skill gaps, and disclaimer.

    DISCLAIMER: Scores are benchmark indicators only, not employer-specific evaluations.
    """
    # ── 1. Load the resume file ──────────────────────────────────────────────
    matching_files = list(settings.RESUME_STORAGE_DIR.glob(f"{request.resume_id}_*"))
    if not matching_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID '{request.resume_id}' not found. Upload first via POST /api/v1/resumes/upload."
        )

    file_path = matching_files[0]

    try:
        # ── 2. Parse document and extract structured resume ──────────────────
        with open(file_path, "rb") as f:
            content = f.read()
        extraction = DocumentParserService.parse_document(content, file_path.name)

        structured_resume = None
        if extraction_service.client.is_available():
            try:
                structured_resume = extraction_service.extract_from_text(extraction.cleaned_text)
            except Exception:
                structured_resume = None

        if not structured_resume:
            structured_resume = extraction_service.create_synthetic_profile(
                name="Candidate",
                title="AI & Software Engineer",
                skills=["Python", "FastAPI", "PostgreSQL", "Docker", "PyTorch", "Redis", "LangGraph"]
            )

        # ── 3. Run designation match ─────────────────────────────────────────
        return designation_matcher_service.match_against_designation(
            resume=structured_resume,
            role_id=request.role_id,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
