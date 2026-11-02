import pytest
from app.schemas.structured_resume import (
    StructuredResume,
    ContactInformation,
    SkillsInventory,
    WorkExperienceItem,
    ProjectItem,
    EducationItem
)
from app.schemas.job_matching import (
    ExtractedJobRequirements,
    MatchScoringWeights,
    JobMatchReport
)
from app.services.job_matching.matcher import HybridJobMatcher
from app.services.job_matching.jd_extractor import JobDescriptionExtractorService

@pytest.fixture
def candidate_resume():
    return StructuredResume(
        contact_info=ContactInformation(
            full_name="Charan Mareddy",
            email="charan@example.com"
        ),
        professional_summary="AI Engineer specializing in Python, FastAPI, and PyTorch backend systems.",
        skills=SkillsInventory(
            languages=["Python", "SQL"],
            frameworks_and_libraries=["FastAPI", "PyTorch"],
            databases=["PostgreSQL", "Redis"],
            cloud_and_devops=["Docker", "AWS"],
            ai_ml_tools=["LangGraph", "LangChain"]
        ),
        work_experience=[
            WorkExperienceItem(
                job_title="AI Engineer",
                company="Antigravity",
                start_date="2022",
                end_date="Present",
                is_current=True,
                responsibilities_and_achievements=[
                    "Built asynchronous FastAPI pipelines and integrated PostgreSQL databases with high concurrency"
                ],
                technologies_used=["Python", "FastAPI", "PostgreSQL", "Docker"]
            )
        ],
        projects=[
            ProjectItem(
                project_title="Distributed Job Matcher",
                description="Engineered high-throughput resume to job matching engine with PyTorch and Redis.",
                technologies_used=["PyTorch", "Redis"],
                key_outcomes=["Achieved sub-50ms matching latency"]
            )
        ],
        education=[
            EducationItem(
                institution="SJCIT",
                degree="B.Tech",
                field_of_study="Computer Science & Engineering",
                graduation_year="2023"
            )
        ]
    )

@pytest.fixture
def target_jd():
    return ExtractedJobRequirements(
        job_title="Senior AI Backend Engineer",
        company_name="Tech Scaleup",
        experience_years_required=2.0,
        education_level_required="B.Tech Computer Science",
        mandatory_skills=["Python", "FastAPI", "Postgres", "Docker"],
        preferred_skills=["PyTorch", "Kubernetes", "Redis"],
        key_responsibilities=[
            "Design and scale backend REST APIs.",
            "Deploy machine learning inference workloads."
        ],
        domain_knowledge=["Artificial Intelligence", "Cloud Infrastructure"]
    )

def test_match_scoring_weights_validation():
    valid = MatchScoringWeights()
    assert valid.validate_weights() is True

    with pytest.raises(ValueError, match="Match scoring weights do not sum to 1.0"):
        invalid = MatchScoringWeights(required_skills_and_qualifications=0.80)
        HybridJobMatcher(weights=invalid)

def test_evidence_collection(candidate_resume):
    matcher = HybridJobMatcher()
    evidence = matcher._collect_resume_evidence(candidate_resume)
    assert len(evidence) >= 10
    
    # Check section tags exist
    sections = {item[2] for item in evidence}
    assert "skills" in sections
    assert "work_experience" in sections
    assert "projects" in sections
    assert "education" in sections

def test_exact_and_alias_skill_matching(candidate_resume):
    matcher = HybridJobMatcher()
    evidence = matcher._collect_resume_evidence(candidate_resume)

    # 1. Exact match
    match_python = matcher.match_skill("Python", evidence, is_mandatory=True)
    assert match_python.match_status == "MATCHED"
    assert match_python.similarity_score == 100.0
    assert "Python" in match_python.supporting_evidence

    # 2. Ontology alias match (Postgres -> PostgreSQL)
    match_postgres = matcher.match_skill("Postgres", evidence, is_mandatory=True)
    assert match_postgres.match_status == "MATCHED"
    assert match_postgres.similarity_score >= 90.0
    assert "PostgreSQL" in match_postgres.supporting_evidence

def test_missing_skill_detection(candidate_resume):
    matcher = HybridJobMatcher()
    evidence = matcher._collect_resume_evidence(candidate_resume)

    match_k8s = matcher.match_skill("Kubernetes", evidence, is_mandatory=False)
    assert match_k8s.match_status == "MISSING"
    assert match_k8s.supporting_evidence is None

def test_evaluate_job_match_scoring(candidate_resume, target_jd):
    matcher = HybridJobMatcher()
    report = matcher.evaluate_job_match(candidate_resume, target_jd)

    assert isinstance(report, JobMatchReport)
    assert 0.0 <= report.overall_match_score <= 100.0
    assert report.mandatory_skills_match_rate == 100.0  # Python, FastAPI, Postgres, Docker all matched
    assert report.overall_match_score >= 70.0
    assert "Good Match" in report.match_tier
    assert len(report.matched_skills) >= 4
    assert any(s.requirement == "Kubernetes" for s in report.missing_skills)
    assert len(report.tailoring_recommendations) >= 1

def test_jd_extractor_service_heuristic():
    service = JobDescriptionExtractorService()
    sample_jd_text = (
        "We are hiring a Senior AI Engineer at Tech Corp. "
        "Must have 3 years experience with Python, FastAPI, Docker, and PyTorch. "
        "Knowledge of Kubernetes and Redis is preferred. "
        "You will design scalable cloud APIs and lead ML deployments."
    )
    result = service.extract_requirements(sample_jd_text)

    assert "AI" in result.job_title or "Engineer" in result.job_title
    assert "Python" in result.mandatory_skills
    assert len(result.mandatory_skills) >= 2
    assert len(result.key_responsibilities) >= 1
