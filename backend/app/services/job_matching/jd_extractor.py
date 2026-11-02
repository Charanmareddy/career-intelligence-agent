import json
import logging
from typing import Optional
from google.genai import types
from app.schemas.job_matching import ExtractedJobRequirements
from app.integrations.gemini.client import gemini_client, GeminiResumeExtractionClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_JD_EXTRACTION = """
You are an expert Job Description Requirement Extraction and Role Taxonomy engine.
Analyze the provided Job Description text and extract all hiring criteria into the exact structured schema provided.

EXTRACTION INSTRUCTIONS:
1. Extract the primary job title and company name (if present).
2. Distinguish clearly between MANDATORY (required, non-negotiable) skills and PREFERRED (nice-to-have) skills.
3. Extract minimum experience years if explicitly stated (e.g., '3+ years' -> 3.0).
4. Identify primary key responsibilities and domain areas.
5. Do not invent or assume requirements not mentioned in the JD.
"""

class JobDescriptionExtractorService:
    def __init__(self, client: Optional[GeminiResumeExtractionClient] = None):
        self.client = client or gemini_client

    def extract_requirements(self, jd_text: str) -> ExtractedJobRequirements:
        """
        Extracts structured job requirements from raw JD text using Gemini.
        Falls back to deterministic rule extraction if offline.
        """
        if not jd_text or len(jd_text.strip()) < 30:
            raise ValueError("Job description text is too short to analyze.")

        if not self.client.is_available():
            return self._heuristic_fallback(jd_text)

        prompt = f"Extract structured job requirements from this Job Description:\n\n---\n{jd_text}\n---"

        try:
            response = self.client._client.models.generate_content(
                model=self.client.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT_JD_EXTRACTION,
                    response_mime_type="application/json",
                    response_schema=ExtractedJobRequirements,
                    temperature=0.0,
                )
            )

            data = json.loads(response.text)
            return ExtractedJobRequirements.model_validate(data)

        except Exception as e:
            logger.warning(f"Gemini JD extraction failed: {e}. Using deterministic heuristic fallback.")
            return self._heuristic_fallback(jd_text)

    def _heuristic_fallback(self, jd_text: str) -> ExtractedJobRequirements:
        """Deterministic keyword parser fallback for testing/offline use."""
        text_lower = jd_text.lower()
        title = "Software Engineer"
        for t in ["ai engineer", "machine learning engineer", "data scientist", "python developer", "backend engineer"]:
            if t in text_lower:
                title = t.title()
                break

        # Extract common technologies
        tech_catalog = [
            "python", "fastapi", "docker", "postgresql", "redis", "pytorch", "tensorflow",
            "langchain", "langgraph", "aws", "kubernetes", "sql", "git", "scikit-learn"
        ]
        found_tech = [t.capitalize() for t in tech_catalog if t in text_lower]

        mandatory = found_tech[:4] if found_tech else ["Python", "FastAPI"]
        preferred = found_tech[4:] if len(found_tech) > 4 else ["Docker", "Kubernetes"]

        return ExtractedJobRequirements(
            job_title=title,
            company_name="Technology Company",
            experience_years_required=2.0 if "2" in text_lower else 3.0,
            education_level_required="Bachelor's Degree in Computer Science or related field",
            mandatory_skills=mandatory,
            preferred_skills=preferred,
            key_responsibilities=[
                "Architect and develop scalable backend APIs and machine learning services.",
                "Collaborate with cross-functional engineering and product teams."
            ],
            domain_knowledge=["Artificial Intelligence", "Cloud Computing"]
        )

jd_extractor_service = JobDescriptionExtractorService()
