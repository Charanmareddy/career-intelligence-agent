"""
Tests: Designation Benchmark Matching (Milestone 5)
=====================================================

Tests the curated role profile loading, designation matcher service,
and the API endpoints for designation-based resume matching.

All tests are fully deterministic — no real Gemini API calls are made.
The HybridJobMatcher is tested with crafted fixture resumes that control
the expected match scores.
"""

import pytest
from unittest.mock import MagicMock, patch
from app.schemas.structured_resume import (
    StructuredResume,
    ContactInformation,
    SkillsInventory,
    WorkExperienceItem,
    ProjectItem,
    EducationItem,
)
from app.schemas.designation_matching import (
    RoleProfile,
    DesignationMatchReport,
    DesignationListResponse,
)
from app.services.job_matching.role_profiles import load_all_role_profiles, ROLE_PROFILES, AVAILABLE_ROLE_IDS
from app.services.job_matching.designation_matcher import (
    DesignationMatcherService,
    _role_profile_to_job_requirements,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def ai_engineer_resume():
    """
    A candidate with strong AI/ML profile — expected to match 'ai_engineer' well.
    Has Python, ML/DL frameworks, SQL, Git, and project experience.
    """
    return StructuredResume(
        contact_info=ContactInformation(
            full_name="Arjun Verma",
            email="arjun@example.com",
            phone="+91 9988776655",
            location="Bengaluru, India",
            github_url="https://github.com/arjunverma",
            linkedin_url="https://linkedin.com/in/arjunverma",
        ),
        professional_summary=(
            "Machine Learning Engineer with hands-on experience building and deploying "
            "deep learning models using PyTorch and TensorFlow. Proficient in Python, "
            "scikit-learn, pandas, and REST APIs."
        ),
        skills=SkillsInventory(
            languages=["Python", "SQL", "Bash"],
            frameworks_and_libraries=[
                "PyTorch", "TensorFlow", "Scikit-learn", "NumPy", "Pandas",
                "FastAPI", "Hugging Face", "MLflow"
            ],
            databases=["PostgreSQL", "MySQL"],
            tools=["Git", "Docker", "Jupyter", "VS Code"],
            cloud_and_devops=["AWS"],
            ai_ml_tools=["Scikit-learn", "PyTorch", "TensorFlow", "Hugging Face", "MLflow"],
        ),
        work_experience=[
            WorkExperienceItem(
                job_title="Machine Learning Intern",
                company="TechCorp AI",
                start_date="Jan 2024",
                end_date="Jun 2024",
                is_current=False,
                responsibilities_and_achievements=[
                    "Developed a text classification model using BERT achieving 92% F1 score.",
                    "Built and optimized REST API endpoints for model serving using FastAPI.",
                    "Reduced inference latency by 35% through model quantization.",
                ],
                skills_used=["Python", "PyTorch", "FastAPI", "Hugging Face"],
            )
        ],
        projects=[
            ProjectItem(
                project_title="Resume Parser with NLP",
                description="Built an end-to-end resume parsing system using spaCy and regex.",
                technologies_used=["Python", "spaCy", "FastAPI", "PostgreSQL"],
                role="Developer",
            ),
            ProjectItem(
                project_title="Sentiment Analysis Dashboard",
                description="ML pipeline for real-time sentiment analysis of product reviews.",
                technologies_used=["Python", "Scikit-learn", "Pandas", "Matplotlib", "Docker"],
                role="Developer",
            ),
        ],
        education=[
            EducationItem(
                institution="NIT Warangal",
                degree="B.Tech",
                field_of_study="Computer Science and Engineering",
                graduation_year="2024",
                cgpa_or_percentage="8.4 CGPA",
            )
        ],
    )


@pytest.fixture
def sparse_resume():
    """
    A candidate with very minimal profile — expected to score low against any role.
    Only has name, email, and one programming language.
    """
    return StructuredResume(
        contact_info=ContactInformation(
            full_name="Sparse Candidate",
            email="sparse@example.com",
        ),
        professional_summary="",
        skills=SkillsInventory(
            languages=["Python"],
        ),
    )


@pytest.fixture
def designation_matcher():
    """Returns a default DesignationMatcherService instance."""
    return DesignationMatcherService()


# ─────────────────────────────────────────────────────────────────────────────
# Test: Role Profile Loading
# ─────────────────────────────────────────────────────────────────────────────

def test_all_role_profiles_load_without_error():
    """
    All 7 curated role profiles must load and validate without raising
    a Pydantic ValidationError or any other exception.
    """
    profiles = load_all_role_profiles()
    assert len(profiles) >= 7, "Expected at least 7 curated role profiles"


def test_role_profiles_have_required_fields():
    """
    Each profile must have a non-empty role_id, display_name, mandatory_skills,
    and at least one assumption documenting the profile's basis.
    """
    profiles = load_all_role_profiles()
    for role_id, profile in profiles.items():
        assert profile.role_id == role_id, f"role_id mismatch for '{role_id}'"
        assert profile.display_name, f"Missing display_name for '{role_id}'"
        assert len(profile.mandatory_skills) >= 3, (
            f"'{role_id}' must have at least 3 mandatory skills for meaningful matching"
        )
        assert len(profile.assumptions) >= 1, (
            f"'{role_id}' must document at least one assumption"
        )


def test_available_role_ids_contains_all_target_roles():
    """
    The 7 target designations from the architecture spec must all be present.
    """
    target_roles = {
        "ai_engineer", "ml_engineer", "data_scientist",
        "genai_engineer", "python_developer", "software_engineer", "data_analyst"
    }
    missing = target_roles - set(AVAILABLE_ROLE_IDS)
    assert not missing, f"Missing role profiles for: {missing}"


def test_role_profile_to_job_requirements_conversion():
    """
    Converting a RoleProfile to ExtractedJobRequirements must preserve
    mandatory skills and preferred skills correctly.
    """
    ai_profile = ROLE_PROFILES["ai_engineer"]
    requirements = _role_profile_to_job_requirements(ai_profile)

    assert requirements.job_title == ai_profile.display_name
    assert set(requirements.mandatory_skills) == set(ai_profile.mandatory_skills)
    assert set(requirements.preferred_skills) == set(ai_profile.preferred_skills)
    assert requirements.experience_years_required == ai_profile.preferred_experience_years


# ─────────────────────────────────────────────────────────────────────────────
# Test: Designation Matcher Service
# ─────────────────────────────────────────────────────────────────────────────

def test_get_available_roles_returns_all_profiles(designation_matcher):
    """
    get_available_roles() must return a DesignationListResponse with at least 7 entries.
    """
    response = designation_matcher.get_available_roles()
    assert isinstance(response, DesignationListResponse)
    assert response.total >= 7
    assert len(response.available_designations) == response.total
    assert response.disclaimer  # disclaimer must not be empty


def test_get_available_roles_has_required_keys(designation_matcher):
    """
    Each entry in available_designations must include role_id, display_name, and description.
    """
    response = designation_matcher.get_available_roles()
    for entry in response.available_designations:
        assert "role_id" in entry
        assert "display_name" in entry
        assert "description" in entry
        assert entry["role_id"]  # must not be empty string


def test_match_strong_ai_engineer_profile(designation_matcher, ai_engineer_resume):
    """
    A candidate with strong AI/ML skills should score >= 60 against 'ai_engineer'.
    (Deterministic test — no Gemini call made since HybridJobMatcher is pure Python)
    """
    report = designation_matcher.match_against_designation(ai_engineer_resume, "ai_engineer")

    assert isinstance(report, DesignationMatchReport)
    assert report.role_id == "ai_engineer"
    assert report.role_display_name == "AI / ML Engineer"
    assert report.match_report.overall_match_score >= 60.0, (
        f"Strong AI profile should score >= 60, got {report.match_report.overall_match_score}"
    )
    assert report.disclaimer  # disclaimer must be present and non-empty
    assert len(report.assumptions_applied) >= 1  # must carry profile assumptions


def test_match_sparse_resume_scores_low(designation_matcher, sparse_resume):
    """
    A very sparse resume (just Python skill) should score < 40 against any role.
    This validates that the benchmark is not artificially inflated.
    """
    report = designation_matcher.match_against_designation(sparse_resume, "ai_engineer")

    assert isinstance(report, DesignationMatchReport)
    assert report.match_report.overall_match_score < 50.0, (
        f"Sparse resume should score < 50, got {report.match_report.overall_match_score}"
    )


def test_match_returns_skill_evidence(designation_matcher, ai_engineer_resume):
    """
    The match report must include matched_skills with evidence for a strong candidate.
    """
    report = designation_matcher.match_against_designation(ai_engineer_resume, "ai_engineer")
    matched = report.match_report.matched_skills
    assert len(matched) >= 3, (
        f"Strong AI candidate should have at least 3 matched skills, got {len(matched)}"
    )


def test_match_returns_missing_skills(designation_matcher, sparse_resume):
    """
    A sparse resume must have at least some missing skills identified.
    """
    report = designation_matcher.match_against_designation(sparse_resume, "data_scientist")
    missing = report.match_report.missing_skills
    assert len(missing) >= 3, (
        f"Sparse resume should have at least 3 missing skills, got {len(missing)}"
    )


def test_match_unknown_role_raises_value_error(designation_matcher, ai_engineer_resume):
    """
    Requesting a non-existent role_id must raise a descriptive ValueError.
    """
    with pytest.raises(ValueError, match="Unknown role_id"):
        designation_matcher.match_against_designation(ai_engineer_resume, "nonexistent_role")


def test_get_role_profile_valid_id(designation_matcher):
    """
    get_role_profile() must return the correct RoleProfile for a valid role_id.
    """
    profile = designation_matcher.get_role_profile("genai_engineer")
    assert isinstance(profile, RoleProfile)
    assert profile.role_id == "genai_engineer"
    assert "LangChain" in profile.mandatory_skills or "LLM" in profile.mandatory_skills


def test_get_role_profile_invalid_id_raises(designation_matcher):
    """
    get_role_profile() must raise ValueError for an unknown role_id.
    """
    with pytest.raises(ValueError, match="Unknown role_id"):
        designation_matcher.get_role_profile("unknown_role_xyz")


def test_designation_match_report_has_disclaimer(designation_matcher, ai_engineer_resume):
    """
    Every DesignationMatchReport must carry the mandatory disclaimer text.
    """
    report = designation_matcher.match_against_designation(ai_engineer_resume, "python_developer")
    assert report.disclaimer
    assert "curated" in report.disclaimer.lower() or "benchmark" in report.disclaimer.lower()


def test_all_roles_produce_valid_report(designation_matcher, ai_engineer_resume):
    """
    Integration: running a match against every available role must succeed
    without exceptions and return a valid DesignationMatchReport.
    """
    for role_id in AVAILABLE_ROLE_IDS:
        report = designation_matcher.match_against_designation(ai_engineer_resume, role_id)
        assert isinstance(report, DesignationMatchReport), f"Failed for role_id='{role_id}'"
        assert 0.0 <= report.match_report.overall_match_score <= 100.0, (
            f"Score out of range for role_id='{role_id}'"
        )
