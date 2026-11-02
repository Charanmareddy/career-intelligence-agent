from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class ExtractedJobRequirements(BaseModel):
    job_title: str = Field(description="Extracted or normalized job title")
    company_name: Optional[str] = Field(default=None, description="Company name if mentioned")
    experience_years_required: Optional[float] = Field(default=None, description="Minimum years of experience required")
    education_level_required: Optional[str] = Field(default=None, description="Minimum degree required (e.g. B.Tech, Master's)")
    mandatory_skills: List[str] = Field(default_factory=list, description="Non-negotiable mandatory skills/technologies")
    preferred_skills: List[str] = Field(default_factory=list, description="Nice-to-have or preferred technical skills")
    key_responsibilities: List[str] = Field(default_factory=list, description="Primary duties and responsibilities")
    domain_knowledge: List[str] = Field(default_factory=list, description="Domain areas (e.g. Fintech, NLP, Healthcare)")

class SkillMatchItem(BaseModel):
    requirement: str
    match_status: str = Field(description="MATCHED, PARTIALLY_MATCHED, MISSING")
    matched_term: Optional[str] = None
    similarity_score: float = Field(ge=0.0, le=100.0)
    is_mandatory: bool = True
    supporting_evidence: Optional[str] = None
    source_section: Optional[str] = None  # skills, work_experience, projects, education

class MatchScoringWeights(BaseModel):
    version: str = "1.0.0"
    required_skills_and_qualifications: float = Field(default=0.25)
    relevant_experience_and_projects: float = Field(default=0.20)
    keyword_coverage: float = Field(default=0.15)
    technical_and_domain_alignment: float = Field(default=0.15)
    responsibilities_evidence: float = Field(default=0.10)
    education_and_certifications: float = Field(default=0.10)
    ats_readability: float = Field(default=0.05)

    def validate_weights(self) -> bool:
        total = (
            self.required_skills_and_qualifications +
            self.relevant_experience_and_projects +
            self.keyword_coverage +
            self.technical_and_domain_alignment +
            self.responsibilities_evidence +
            self.education_and_certifications +
            self.ats_readability
        )
        return abs(total - 1.0) < 1e-4

class JobMatchReport(BaseModel):
    job_title: str
    overall_match_score: float = Field(ge=0.0, le=100.0)
    match_tier: str = Field(description="High Match, Good Match, Moderate Match, Low Match")
    weights_version: str = "1.0.0"
    mandatory_skills_match_rate: float
    preferred_skills_match_rate: float
    matched_skills: List[SkillMatchItem] = Field(default_factory=list)
    partially_matched_skills: List[SkillMatchItem] = Field(default_factory=list)
    missing_skills: List[SkillMatchItem] = Field(default_factory=list)
    experience_alignment: Dict[str, str] = Field(default_factory=dict)
    education_alignment: Dict[str, str] = Field(default_factory=dict)
    tailoring_recommendations: List[str] = Field(default_factory=list)
    disclaimer: str = (
        "This job compatibility score is our internal deterministic match assessment. "
        "It does not guarantee employer interview selection."
    )
