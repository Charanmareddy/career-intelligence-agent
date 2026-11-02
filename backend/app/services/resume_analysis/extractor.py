import re
from typing import Dict, Any, List, Optional
from app.schemas.structured_resume import (
    StructuredResume,
    ContactInformation,
    SkillsInventory,
    WorkExperienceItem,
    ProjectItem,
    EducationItem,
    CertificationItem
)
from app.integrations.gemini.client import gemini_client, GeminiResumeExtractionClient

class StructuredResumeExtractionService:
    """
    Coordinates AI-driven structured extraction and deterministic post-validation.
    """

    def __init__(self, client: Optional[GeminiResumeExtractionClient] = None):
        self.client = client or gemini_client

    @staticmethod
    def _validate_email(email: Optional[str]) -> bool:
        if not email:
            return False
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return bool(re.match(pattern, email.strip()))

    def post_validate_and_sanitize(self, data: StructuredResume) -> StructuredResume:
        """
        Runs deterministic checks on extracted candidate data and appends validation notes.
        """
        notes = list(data.extraction_notes)

        # Check contact info
        if not data.contact_info.full_name or data.contact_info.full_name.lower() in {"unknown", "n/a", "candidate"}:
            notes.append("Warning: Candidate full name could not be reliably determined.")

        if not data.contact_info.email:
            notes.append("Notice: No email address detected in resume.")
        elif not self._validate_email(data.contact_info.email):
            notes.append(f"Notice: Email '{data.contact_info.email}' may be formatted irregularly.")

        if not data.contact_info.phone:
            notes.append("Notice: No phone number detected in resume.")

        # Check skills presentation
        total_skills = (
            len(data.skills.languages) +
            len(data.skills.frameworks_and_libraries) +
            len(data.skills.databases) +
            len(data.skills.cloud_and_devops) +
            len(data.skills.ai_ml_tools)
        )
        if total_skills == 0:
            notes.append("Warning: No categorized technical skills were extracted.")

        # Check experience & projects
        if not data.work_experience and not data.internships and not data.projects:
            notes.append("Warning: No work experience, internships, or projects detected.")

        if not data.education:
            notes.append("Notice: No formal education or degree history detected.")

        data.extraction_notes = notes
        return data

    def extract_from_text(self, cleaned_text: str) -> StructuredResume:
        """
        Extracts structured resume using Gemini, then validates and annotates with notes.
        """
        if not cleaned_text or len(cleaned_text.strip()) < 20:
            raise ValueError("Resume text is too brief or empty for structured extraction.")

        structured = self.client.extract_structured_resume(cleaned_text)
        return self.post_validate_and_sanitize(structured)

    @classmethod
    def create_synthetic_profile(cls, name: str, title: str, skills: List[str]) -> StructuredResume:
        """
        Deterministic mock generator for offline unit testing without external API calls.
        """
        return StructuredResume(
            contact_info=ContactInformation(
                full_name=name,
                email=f"{name.lower().replace(' ', '.')}@example.com",
                phone="+91 9876543210",
                location="Bengaluru, India",
                linkedin_url=f"https://linkedin.com/in/{name.lower().replace(' ', '')}",
                github_url=f"https://github.com/{name.lower().replace(' ', '')}"
            ),
            professional_summary=f"Experienced {title} with expertise in building scalable AI and backend systems.",
            skills=SkillsInventory(
                languages=[s for s in skills if s in {"Python", "SQL", "JavaScript", "TypeScript", "C++", "Java"}],
                frameworks_and_libraries=[s for s in skills if s in {"FastAPI", "PyTorch", "Django", "React", "Transformers"}],
                databases=[s for s in skills if s in {"PostgreSQL", "Redis", "MongoDB"}],
                cloud_and_devops=[s for s in skills if s in {"Docker", "AWS", "Git", "Kubernetes", "Linux"}],
                ai_ml_tools=[s for s in skills if s in {"LangGraph", "LangChain", "Hugging Face", "Scikit-Learn", "Gemini API"}]
            ),
            work_experience=[
                WorkExperienceItem(
                    job_title=title,
                    company="Tech Corp India",
                    location="Bengaluru, India",
                    start_date="Jan 2023",
                    end_date="Present",
                    is_current=True,
                    responsibilities_and_achievements=[
                        "Engineered high-throughput REST APIs and AI pipelines reducing latency by 35%",
                        "Led multi-agent system design for enterprise document intelligence workflows"
                    ],
                    technologies_used=skills[:4]
                )
            ],
            education=[
                EducationItem(
                    institution="National Institute of Technology",
                    degree="B.Tech",
                    field_of_study="Computer Science and Engineering",
                    start_year="2019",
                    graduation_year="2023",
                    grade_or_gpa="8.8 / 10.0"
                )
            ],
            certifications=[
                CertificationItem(
                    name="Google Cloud Professional Data Engineer",
                    issuing_organization="Google Cloud",
                    issue_date="2024"
                )
            ]
        )

extraction_service = StructuredResumeExtractionService()
