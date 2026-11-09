"""
Phase 1 Evaluation Gate Tests
==============================

Automated verification of the Phase 1 Evaluation Gate:
- Evaluates the 5 synthetic benchmark resumes.
- Verifies score monotonicity (Strong > Moderate > Weak).
- Tests ATS readiness calibration and weakness identification.
- Tests JD matching against realistic AI Engineer and Backend roles.
- Tests Designation benchmark matching across all 7 curated roles (35 combinations).
- Confirms fresh-graduate fairness (internships + projects recognize competency).
"""

import pytest
from evaluations.evaluation_dataset import load_all_evaluation_profiles
from evaluations.evaluator import Phase1EvaluationGateRunner


@pytest.fixture(scope="module")
def eval_runner():
    return Phase1EvaluationGateRunner()


@pytest.fixture(scope="module")
def eval_results(eval_runner):
    return eval_runner.run_full_evaluation()


def test_evaluation_dataset_profiles_valid():
    """All 5 benchmark profiles must load without schema or validation errors."""
    profiles = load_all_evaluation_profiles()
    assert len(profiles) == 5
    for name, (doc_result, resume) in profiles.items():
        assert doc_result.success is True
        assert resume.contact_info.full_name
        assert len(resume.skills.languages) > 0


def test_ats_score_monotonicity(eval_results):
    """
    ATS Readiness score must strictly order:
    Strong AI Engineer > Moderate Python Dev > Weak Sparse Candidate
    """
    ats = eval_results["ats_readiness"]
    strong = ats["strong_ai"]["overall_score"]
    moderate = ats["moderate_python"]["overall_score"]
    weak = ats["weak_sparse"]["overall_score"]

    assert strong > moderate > weak, (
        f"Monotonicity failed: Strong({strong}) > Moderate({moderate}) > Weak({weak})"
    )
    assert strong >= 80.0, f"Strong profile must achieve >= 80 ATS readiness, got {strong}"
    assert weak < 60.0, f"Weak profile must score < 60 ATS readiness, got {weak}"


def test_weak_profile_identifies_penalties(eval_results):
    """Weak profile must trigger specific penalties in ATS evaluation."""
    ats = eval_results["ats_readiness"]["weak_sparse"]
    assert ats["weaknesses_count"] > 0
    # Language clarity or sections should be low
    assert ats["category_scores"]["language_and_clarity"] < 100.0


def test_ai_engineer_jd_matching(eval_results):
    """
    AI Engineer JD match must rank Strong AI candidate higher than Moderate Python candidate,
    and higher than Weak candidate.
    """
    jd_ai = eval_results["jd_matching_ai_engineer"]
    strong = jd_ai["strong_ai"]["overall_match_score"]
    mod = jd_ai["moderate_python"]["overall_match_score"]
    weak = jd_ai["weak_sparse"]["overall_match_score"]

    assert strong > mod > weak, (
        f"JD AI monotonicity failed: Strong({strong}) > Mod({mod}) > Weak({weak})"
    )
    assert strong >= 70.0, f"Strong AI candidate should score >= 70 on AI JD, got {strong}"
    assert jd_ai["strong_ai"]["matched_count"] >= 3


def test_backend_engineer_jd_matching(eval_results):
    """
    Experienced Backend Architect must achieve top match score on Backend Engineer JD.
    """
    jd_back = eval_results["jd_matching_backend_engineer"]
    arch = jd_back["experienced_arch"]["overall_match_score"]
    fresher = jd_back["fresh_ds"]["overall_match_score"]

    assert arch > fresher, (
        f"Experienced architect ({arch}) must outscore fresher data scientist ({fresher}) on backend JD"
    )
    assert arch >= 75.0, f"Backend architect should score >= 75 on Backend JD, got {arch}"


def test_designation_benchmarks_all_roles(eval_results):
    """
    All 5 profiles across all 7 curated designations (35 combinations)
    must produce valid scores between 0 and 100.
    """
    benchmarks = eval_results["designation_benchmarks"]
    assert len(benchmarks) == 7

    for role_id, candidate_scores in benchmarks.items():
        assert len(candidate_scores) == 5
        for cand_name, data in candidate_scores.items():
            score = data["score"]
            assert 0.0 <= score <= 100.0, (
                f"Score out of range for {cand_name} on {role_id}: {score}"
            )
            assert any(
                t in data["tier"]
                for t in ["High Match", "Good Match", "Moderate Match", "Low Match"]
            ), f"Unexpected match tier: {data['tier']}"


def test_fresh_graduate_fairness(eval_results):
    """
    Fresh Graduate with Data Science capstone projects and internship
    must achieve a competitive score (>= 60) on the 'data_scientist' designation.
    """
    ds_scores = eval_results["designation_benchmarks"]["data_scientist"]
    fresh_ds_score = ds_scores["fresh_ds"]["score"]

    assert fresh_ds_score >= 60.0, (
        f"Fresh Graduate Data Scientist should score >= 60 on Data Scientist designation, got {fresh_ds_score}"
    )


def test_evaluation_gate_summary_and_monotonicity(eval_results):
    """Overall summary metrics must confirm all monotonicity tests passed."""
    checks = eval_results["monotonicity_checks"]
    assert checks["ats_monotonicity_passed"] is True
    assert checks["ai_jd_matching_monotonicity_passed"] is True
    assert checks["experienced_outscores_fresher_on_backend_jd"] is True

    summary = eval_results["summary_metrics"]
    assert summary["all_monotonicity_passed"] is True
    assert summary["total_matrix_combinations"] == 35
