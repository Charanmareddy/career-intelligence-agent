import pytest
from unittest.mock import MagicMock
from app.schemas.structured_resume import (
    StructuredResume,
    ContactInformation,
    SkillsInventory,
    WorkExperienceItem,
    ProjectItem,
    EducationItem,
    CertificationItem
)
from app.services.resume_analysis.extractor import StructuredResumeExtractionService
from app.integrations.gemini.client import GeminiResumeExtractionClient

def test_structured_resume_schema_instantiation():
    resume = StructuredResume(
        contact_info=ContactInformation(
            full_name="Charan Mareddy",
            email="charan@example.com",
            phone="+91 9999999999",
            location="Bengaluru, India",
            github_url="https://github.com/charan"
        ),
        professional_summary="AI Engineer specialized in Agentic workflows and LLM applications.",
        skills=SkillsInventory(
            languages=["Python", "SQL"],
            frameworks_and_libraries=["FastAPI", "PyTorch"],
            databases=["PostgreSQL", "Redis"],
            cloud_and_devops=["Docker", "AWS"],
            ai_ml_tools=["LangGraph", "Gemini API"]
        ),
        work_experience=[
            WorkExperienceItem(
                job_title="AI Solutions Architect",
                company="Antigravity Corp",
                location="Bengaluru",
                start_date="2023",
                end_date="Present",
                is_current=True,
                responsibilities_and_achievements=[
                    "Designed high-performance multi-agent architectures reducing manual task time by 60%"
                ],
                technologies_used=["Python", "FastAPI", "LangGraph"]
            )
        ],
        education=[
            EducationItem(
                institution="SJCIT",
                degree="B.E.",
                field_of_study="Computer Science & Engineering",
                graduation_year="2024"
            )
        ],
        certifications=[
            CertificationItem(
                name="TensorFlow Developer Certificate",
                issuing_organization="Google",
                issue_date="2023"
            )
        ],
        achievements=["Published research paper on multi-agent task planning"]
    )

    assert resume.contact_info.full_name == "Charan Mareddy"
    assert len(resume.skills.languages) == 2
    assert resume.work_experience[0].company == "Antigravity Corp"
    assert len(resume.education) == 1

def test_post_validate_and_sanitize_missing_contact():
    resume = StructuredResume(
        contact_info=ContactInformation(full_name="Unknown"),
        skills=SkillsInventory(),
        work_experience=[],
        projects=[]
    )
    service = StructuredResumeExtractionService()
    validated = service.post_validate_and_sanitize(resume)

    notes_text = " ".join(validated.extraction_notes)
    assert "Candidate full name could not be reliably determined" in notes_text
    assert "No email address detected" in notes_text
    assert "No phone number detected" in notes_text
    assert "No categorized technical skills were extracted" in notes_text
    assert "No work experience, internships, or projects detected" in notes_text

def test_extract_from_text_rejects_empty_input():
    service = StructuredResumeExtractionService()
    with pytest.raises(ValueError, match="Resume text is too brief or empty"):
        service.extract_from_text("Too short")

def test_extract_from_text_with_mocked_gemini():
    mock_gemini_client = MagicMock(spec=GeminiResumeExtractionClient)
    synthetic = StructuredResumeExtractionService.create_synthetic_profile(
        name="Aarav Sharma",
        title="GenAI Developer",
        skills=["Python", "FastAPI", "PyTorch", "PostgreSQL", "Docker", "LangGraph"]
    )
    mock_gemini_client.extract_structured_resume.return_value = synthetic

    service = StructuredResumeExtractionService(client=mock_gemini_client)
    sample_text = (
        "Aarav Sharma\nGenAI Developer\n"
        "Experience in Python, FastAPI, PyTorch, LangGraph, and PostgreSQL. "
        "Built multi-agent systems and deployed scalable backend services."
    )
    result = service.extract_from_text(sample_text)

    assert result.contact_info.full_name == "Aarav Sharma"
    assert "Python" in result.skills.languages
    assert "FastAPI" in result.skills.frameworks_and_libraries
    assert result.work_experience[0].job_title == "GenAI Developer"
    assert mock_gemini_client.extract_structured_resume.called

def test_missing_api_key_raises_actionable_error():
    # Client with no api key configured
    unconfigured_client = GeminiResumeExtractionClient(api_key="")
    assert unconfigured_client.is_available() is False

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        unconfigured_client.extract_structured_resume("Valid resume text for testing here...")
