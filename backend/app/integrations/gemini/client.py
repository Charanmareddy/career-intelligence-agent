import json
import logging
from typing import Optional
from google import genai
from google.genai import types
from app.core.config import settings
from app.schemas.structured_resume import StructuredResume

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_RESUME_EXTRACTION = """
You are an expert AI Resume Parsing and Candidate Information Extraction engine.
Your task is to analyze the provided raw resume text and extract all factual candidate information into the exact structured schema provided.

STRICT FACTUAL ACCURACY RULES:
1. Extract ONLY information explicitly stated in the text.
2. DO NOT invent, assume, extrapolate, or hallucinate any skills, dates, companies, metrics, or degrees.
3. If an item (such as phone number, GPA, or certification ID) is missing, leave it as null or empty list.
4. Categorize skills appropriately into programming languages, frameworks, databases, cloud/devops, and AI/ML tools.
5. In work experiences and projects, preserve technical metrics (e.g., 'reduced latency by 40%') accurately.
6. If dates are approximate or written in non-standard format, preserve the text as stated.
"""

class GeminiResumeExtractionClient:
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = settings.GEMINI_API_KEY

        self.model_name = model_name or settings.DEFAULT_GEMINI_MODEL
        self._client: Optional[genai.Client] = None
        
        # Only initialize if valid non-empty, non-placeholder API key
        if self.api_key and self.api_key.strip() and self.api_key != "your-gemini-api-key-here":
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {e}")
                self._client = None
        else:
            self._client = None

    def is_available(self) -> bool:
        return self._client is not None

    def extract_structured_resume(self, resume_text: str) -> StructuredResume:
        """
        Invokes Gemini API with strict Pydantic response schema to extract candidate data.
        If API key is not configured, raises an actionable ValueError.
        """
        if not self.is_available():
            raise ValueError(
                "Gemini API key is not configured or client failed to initialize. "
                "Please configure GEMINI_API_KEY in your .env file."
            )

        prompt = f"Extract all candidate information from the following resume text:\n\n---\n{resume_text}\n---"

        try:
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT_RESUME_EXTRACTION,
                    response_mime_type="application/json",
                    response_schema=StructuredResume,
                    temperature=0.0,
                )
            )

            response_json = json.loads(response.text)
            return StructuredResume.model_validate(response_json)

        except Exception as e:
            logger.error(f"Gemini structured extraction failed: {str(e)}")
            raise RuntimeError(f"Gemini structured extraction error: {str(e)}")

gemini_client = GeminiResumeExtractionClient()
