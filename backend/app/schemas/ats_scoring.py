from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ScoringWeightsConfig(BaseModel):
    version: str = "1.0.0"
    document_parsing: float = Field(default=0.20, description="Document parsing and compatibility weight")
    section_completeness: float = Field(default=0.15, description="Section completeness weight")
    skills_presentation: float = Field(default=0.15, description="Skills presentation and structure weight")
    projects_and_experience: float = Field(default=0.15, description="Relevant projects and work experience weight")
    achievement_quality: float = Field(default=0.15, description="Action-oriented achievement and impact quality weight")
    language_and_clarity: float = Field(default=0.10, description="Language, readability, and clarity weight")
    date_and_formatting: float = Field(default=0.10, description="Date and formatting consistency weight")

    def validate_weights(self) -> bool:
        total = (
            self.document_parsing +
            self.section_completeness +
            self.skills_presentation +
            self.projects_and_experience +
            self.achievement_quality +
            self.language_and_clarity +
            self.date_and_formatting
        )
        return abs(total - 1.0) < 1e-4

class CategoryScore(BaseModel):
    name: str
    score: float = Field(ge=0.0, le=100.0, description="Category score out of 100")
    weight: float = Field(ge=0.0, le=1.0, description="Assigned category weight")
    weighted_score: float = Field(description="Score scaled by weight")
    strengths: List[str] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)

class ResumeRecommendationItem(BaseModel):
    category: str
    target_section: str
    original_text: Optional[str] = None
    suggested_improvement: str
    rationale: str
    is_impact_enhancement: bool = False

class ATSReadinessReport(BaseModel):
    overall_score: float = Field(ge=0.0, le=100.0, description="Overall weighted ATS readiness score")
    readiness_level: str = Field(description="Qualitative level: Needs Improvement, Moderate, Strong, Exceptional")
    weights_version: str = "1.0.0"
    category_breakdown: Dict[str, CategoryScore]
    summary_strengths: List[str] = Field(default_factory=list)
    summary_weaknesses: List[str] = Field(default_factory=list)
    missing_sections: List[str] = Field(default_factory=list)
    parsing_warnings: List[str] = Field(default_factory=list)
    recommendations: List[ResumeRecommendationItem] = Field(default_factory=list)
    disclaimer: str = (
        "This ATS readiness assessment is our proprietary, deterministic engineering evaluation based "
        "on document structure, clarity, and industry best practices. It does not represent an official score "
        "or hiring guarantee from any specific employer's Applicant Tracking System."
    )
