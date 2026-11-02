import json
import logging
from typing import List, Optional
from pydantic import BaseModel
from google.genai import types
from app.schemas.structured_resume import StructuredResume
from app.schemas.ats_scoring import ATSReadinessReport, ResumeRecommendationItem
from app.integrations.gemini.client import gemini_client, GeminiResumeExtractionClient

logger = logging.getLogger(__name__)

class RecommendationResponseSchema(BaseModel):
    recommendations: List[ResumeRecommendationItem]

SYSTEM_PROMPT_RECOMMENDER = """
You are a Senior Technical Resume Coach and ATS Optimization Specialist.
Your task is to provide actionable, truthful, evidence-backed resume recommendations to improve the candidate's ATS readiness and technical appeal.

STRICT GROUNDING & ETHICAL RULES:
1. NEVER invent, fabricate, or extrapolate new job titles, companies, certifications, degrees, or unevidenced skills.
2. When improving experience or project bullet points:
   - Transform passive phrasing into strong action verbs (e.g. 'Helped with API' -> 'Engineered high-throughput REST APIs').
   - Recommend templates for where the candidate should insert their own real numbers/metrics (e.g. '[X]% reduction in latency').
   - Keep suggested bullet points concise (15-30 words).
3. If the professional summary is missing or weak, draft a tailored 2-sentence summary strictly based on the candidate's actual extracted skills and experience.
4. Ensure the output strictly conforms to the provided schema.
"""

class ResumeRecommendationService:
    def __init__(self, client: Optional[GeminiResumeExtractionClient] = None):
        self.client = client or gemini_client

    def generate_recommendations(
        self,
        structured_resume: StructuredResume,
        ats_report: ATSReadinessReport
    ) -> List[ResumeRecommendationItem]:
        """
        Generates targeted improvements using Gemini based on identified scoring weaknesses.
        Falls back to deterministic rule-based recommendations if Gemini is offline or unavailable.
        """
        # If Gemini is not available, generate deterministic fallback recommendations
        if not self.client.is_available():
            return self._generate_deterministic_fallback(structured_resume, ats_report)

        weaknesses_context = "\n".join(f"- {w}" for w in ats_report.summary_weaknesses)
        issues_context = []
        for cat_name, cat in ats_report.category_breakdown.items():
            if cat.issues:
                issues_context.append(f"{cat.name}: {'; '.join(cat.issues)}")
        issues_summary = "\n".join(issues_context)

        prompt = (
            f"Candidate Name: {structured_resume.contact_info.full_name}\n"
            f"ATS Readiness Score: {ats_report.overall_score}/100 ({ats_report.readiness_level})\n"
            f"Identified Scoring Issues:\n{issues_summary}\n\n"
            f"Extracted Resume Data:\n{structured_resume.model_dump_json(indent=2)}\n\n"
            f"Generate 3-6 high-impact, truthful, evidence-backed recommendations targeting the weakest categories."
        )

        try:
            response = self.client._client.models.generate_content(
                model=self.client.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT_RECOMMENDER,
                    response_mime_type="application/json",
                    response_schema=RecommendationResponseSchema,
                    temperature=0.2,
                )
            )

            data = json.loads(response.text)
            parsed = RecommendationResponseSchema.model_validate(data)
            return parsed.recommendations

        except Exception as e:
            logger.warning(f"Gemini recommendation generation failed: {e}. Falling back to deterministic rules.")
            return self._generate_deterministic_fallback(structured_resume, ats_report)

    def _generate_deterministic_fallback(
        self,
        resume: StructuredResume,
        report: ATSReadinessReport
    ) -> List[ResumeRecommendationItem]:
        """
        Deterministic, rule-based fallback recommendations for testing and offline modes.
        """
        recs = []

        # Professional Summary check
        if not resume.professional_summary or len(resume.professional_summary.split()) < 15:
            top_skills = (resume.skills.languages[:2] + resume.skills.frameworks_and_libraries[:2])
            skills_str = ", ".join(top_skills) if top_skills else "modern software engineering"
            recs.append(ResumeRecommendationItem(
                category="Section Completeness",
                target_section="Professional Summary",
                original_text=resume.professional_summary,
                suggested_improvement=(
                    f"Results-driven Software Engineer with demonstrated experience in {skills_str}. "
                    "Specialized in architecting reliable backend services and scalable applications."
                ),
                rationale="A strong 2-3 sentence executive summary immediately signals core technical domains to recruiters and ATS parsers."
            ))

        # Achievement Quality check
        for exp in resume.work_experience:
            for bullet in exp.responsibilities_and_achievements[:2]:
                if not any(char.isdigit() for char in bullet):
                    recs.append(ResumeRecommendationItem(
                        category="Achievement Quality",
                        target_section=f"Work Experience ({exp.company})",
                        original_text=bullet,
                        suggested_improvement=(
                            f"{bullet} — resulting in a [X]% increase in operational efficiency / [Y] ms reduction in processing latency."
                        ),
                        rationale="Adding quantified performance metrics or business outcomes elevates ordinary task descriptions into verifiable achievements.",
                        is_impact_enhancement=True
                    ))
                    break

        # Project technologies check
        for proj in resume.projects:
            if not proj.technologies_used:
                recs.append(ResumeRecommendationItem(
                    category="Relevant Experience & Projects",
                    target_section=f"Project: {proj.project_title}",
                    original_text=proj.description,
                    suggested_improvement=f"Explicitly list the tech stack (e.g., Python, PostgreSQL, Docker) used to build {proj.project_title}.",
                    rationale="ATS engines match specific technology keywords against role requirements within project contexts."
                ))

        # Skills categorization check
        if report.category_breakdown.get("skills_presentation", {}).score < 70.0:
            recs.append(ResumeRecommendationItem(
                category="Skills Presentation",
                target_section="Technical Skills",
                original_text=None,
                suggested_improvement="Organize your skills into distinct sub-categories: Programming Languages, Frameworks & Libraries, Databases, Cloud & DevOps, and Developer Tools.",
                rationale="Categorized skills enable human recruiters and ATS keyword scanners to rapidly index technical competencies."
            ))

        return recs

recommendation_service = ResumeRecommendationService()
