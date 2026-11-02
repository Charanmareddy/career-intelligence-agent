import pytest
from app.schemas.resume import DocumentExtractionResult, DocumentMetadata
from app.schemas.structured_resume import (
    StructuredResume,
    ContactInformation,
    SkillsInventory,
    WorkExperienceItem,
    ProjectItem,
    EducationItem,
    CertificationItem
)
from app.schemas.ats_scoring import ScoringWeightsConfig, ATSReadinessReport
from app.services.resume_analysis.ats_scoring import ATSScoringEngine
from app.services.resume_analysis.recommender import ResumeRecommendationService

@pytest.fixture
def sample_complete_resume():
    return StructuredResume(
        contact_info=ContactInformation(
            full_name="Charan Mareddy",
            email="charan@example.com",
            phone="+91 9999999999",
            location="Bengaluru, India",
            github_url="https://github.com/charan"
        ),
        professional_summary=(
            "Accomplished Senior AI Engineer with over 4 years of experience architecting and deploying "
            "reliable, high-throughput machine learning pipelines, multi-agent systems, and production REST backends."
        ),
        skills=SkillsInventory(
            languages=["Python", "SQL", "C++"],
            frameworks_and_libraries=["FastAPI", "PyTorch", "Transformers"],
            databases=["PostgreSQL", "Redis"],
            cloud_and_devops=["Docker", "AWS", "Git"],
            ai_ml_tools=["LangGraph", "Gemini API", "Scikit-Learn"],
            soft_skills=["Agile", "Technical Leadership"]
        ),
        work_experience=[
            WorkExperienceItem(
                job_title="Senior AI Engineer",
                company="Antigravity Systems",
                location="Bengaluru",
                start_date="2022",
                end_date="Present",
                is_current=True,
                responsibilities_and_achievements=[
                    "Engineered multi-agent orchestration pipelines reducing task completion latency by 45%",
                    "Architected high-throughput FastAPI REST backends serving 500k daily requests",
                    "Optimized transformer inference pipelines cutting memory footprint by 30%"
                ],
                technologies_used=["Python", "FastAPI", "PyTorch", "PostgreSQL"]
            )
        ],
        projects=[
            ProjectItem(
                project_title="AI Career Intelligence Agent",
                description="Modular enterprise agent platform for career progression and automated matching.",
                technologies_used=["FastAPI", "PyTorch", "LangGraph", "Docker"],
                key_outcomes=[
                    "Scaled retrieval accuracy to 94% across 10,000 synthetic test benchmarks"
                ]
            )
        ],
        education=[
            EducationItem(
                institution="SJCIT",
                degree="B.Tech",
                field_of_study="Computer Science & Engineering",
                graduation_year="2023",
                grade_or_gpa="8.9 / 10.0"
            )
        ],
        certifications=[
            CertificationItem(
                name="Professional Machine Learning Engineer",
                issuing_organization="Google Cloud",
                issue_date="2024"
            )
        ]
    )

@pytest.fixture
def sample_extraction_result():
    return DocumentExtractionResult(
        document_id="doc-123",
        success=True,
        raw_text="...",
        cleaned_text="Charan Mareddy ... Senior AI Engineer ...",
        metadata=DocumentMetadata(
            filename="charan_resume.pdf",
            file_size_bytes=50000,
            file_extension=".pdf",
            page_count=1,
            character_count=2500,
            word_count=450,
            sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ),
        warnings=[]
    )

def test_scoring_weights_validation():
    valid_config = ScoringWeightsConfig()
    assert valid_config.validate_weights() is True

    with pytest.raises(ValueError, match="Scoring weights do not sum to 1.0"):
        invalid_config = ScoringWeightsConfig(document_parsing=0.50)
        ATSScoringEngine(config=invalid_config)

def test_document_parsing_score(sample_extraction_result):
    engine = ATSScoringEngine()
    score = engine._score_document_parsing(sample_extraction_result)
    assert score.score >= 90.0
    assert score.weight == 0.20
    assert score.weighted_score > 0.0

def test_section_completeness_complete_vs_sparse(sample_complete_resume):
    engine = ATSScoringEngine()
    score_full = engine._score_section_completeness(sample_complete_resume)
    assert score_full.score >= 90.0

    sparse = StructuredResume(
        contact_info=ContactInformation(full_name="Jane Doe"),
        skills=SkillsInventory(),
        work_experience=[]
    )
    score_sparse = engine._score_section_completeness(sparse)
    assert score_sparse.score < 40.0
    assert "Missing candidate contact email" in " ".join(score_sparse.issues)

def test_skills_presentation_categorization(sample_complete_resume):
    engine = ATSScoringEngine()
    score = engine._score_skills_presentation(sample_complete_resume)
    assert score.score >= 80.0
    assert "taxonomy" in " ".join(score.strengths).lower()

def test_achievement_quality_action_verbs_and_metrics(sample_complete_resume):
    engine = ATSScoringEngine()
    score = engine._score_achievement_quality(sample_complete_resume)
    assert score.score >= 80.0
    assert any("quantif" in s.lower() or "metric" in s.lower() for s in score.strengths)

def test_language_and_clarity_pronoun_penalties(sample_complete_resume):
    engine = ATSScoringEngine()
    # Resume without pronouns
    score_clean = engine._score_language_and_clarity(sample_complete_resume)
    assert score_clean.score == 100.0

    # Inject first person pronouns
    sample_complete_resume.work_experience[0].responsibilities_and_achievements.append("I managed my team to deploy our app.")
    score_pronoun = engine._score_language_and_clarity(sample_complete_resume)
    assert score_pronoun.score < 100.0
    assert "first-person" in " ".join(score_pronoun.issues).lower()

def test_end_to_end_evaluate_resume(sample_extraction_result, sample_complete_resume):
    engine = ATSScoringEngine()
    report = engine.evaluate_resume(sample_extraction_result, sample_complete_resume)

    assert 0.0 <= report.overall_score <= 100.0
    assert report.overall_score >= 80.0
    assert "ATS Readiness" in report.readiness_level
    assert len(report.category_breakdown) == 7
    assert len(report.summary_strengths) > 0

def test_recommendation_generation_fallback(sample_extraction_result, sample_complete_resume):
    engine = ATSScoringEngine()
    report = engine.evaluate_resume(sample_extraction_result, sample_complete_resume)
    
    recommender = ResumeRecommendationService()
    recs = recommender.generate_recommendations(sample_complete_resume, report)

    assert isinstance(recs, list)
    assert len(recs) >= 1
    for r in recs:
        assert r.category is not None
        assert r.suggested_improvement is not None
