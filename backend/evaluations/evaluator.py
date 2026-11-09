"""
Phase 1 Evaluation Engine
=========================

Executes the Phase 1 Evaluation Gate across:
1. ATS Readiness Scoring Engine
2. Job Description Matching Engine
3. Designation Benchmark Matching Engine

Evaluates all 5 synthetic benchmark profiles against target roles and real-world JDs,
producing structured evaluation reports with statistical metrics.
"""

from typing import Dict, Any, List
from app.services.resume_analysis.ats_scoring import ATSScoringEngine
from app.services.job_matching.matcher import HybridJobMatcher
from app.services.job_matching.designation_matcher import DesignationMatcherService
from app.services.job_matching.jd_extractor import JobDescriptionExtractorService
from evaluations.evaluation_dataset import load_all_evaluation_profiles


SAMPLE_AI_ENGINEER_JD = """
Job Title: AI Engineer (0-3 years experience)
Company: NextGen AI Solutions
Location: Bengaluru, India

About the Role:
We are seeking an AI Engineer to design, build, and deploy production machine learning
models and generative AI applications.

Mandatory Requirements:
- 1+ years of experience in Python programming.
- Hands-on experience with PyTorch or TensorFlow.
- Experience building and deploying REST APIs using FastAPI.
- Familiarity with Git, Docker, and relational databases (PostgreSQL or SQL).

Preferred Qualifications:
- Experience with Hugging Face, LangChain, or LLM application development.
- Knowledge of MLOps, MLflow, or cloud deployments (AWS/GCP).
- Strong computer science fundamentals and problem-solving skills.
"""


SAMPLE_PYTHON_BACKEND_JD = """
Job Title: Backend Python Engineer (2-5 years experience)
Company: CloudScale Enterprise
Location: Hyderabad, India

About the Role:
Looking for a Backend Developer to engineer scalable APIs and distributed systems.

Mandatory Requirements:
- 2+ years of production experience in Python.
- Strong hands-on experience with FastAPI or Django.
- Solid understanding of PostgreSQL and database optimization.
- Familiarity with Redis, message queues, and Docker.

Preferred Qualifications:
- Experience with Kubernetes and CI/CD pipelines.
- Knowledge of Celery, async programming, and microservices architecture.
"""


class Phase1EvaluationGateRunner:
    """
    Automated evaluation runner for Phase 1.
    Executes ATS scoring, JD matching, and Designation matching across all 5 benchmark resumes.
    """

    def __init__(self):
        self.ats_engine = ATSScoringEngine()
        self.matcher = HybridJobMatcher()
        self.designation_service = DesignationMatcherService(matcher=self.matcher)
        self.jd_extractor = JobDescriptionExtractorService()

    def run_full_evaluation(self) -> Dict[str, Any]:
        """
        Runs comprehensive evaluation and returns metrics, score tables, and validation flags.
        """
        profiles = load_all_evaluation_profiles()
        extracted_ai_jd = self.jd_extractor.extract_requirements(SAMPLE_AI_ENGINEER_JD)
        extracted_backend_jd = self.jd_extractor.extract_requirements(SAMPLE_PYTHON_BACKEND_JD)

        results: Dict[str, Any] = {
            "ats_readiness": {},
            "jd_matching_ai_engineer": {},
            "jd_matching_backend_engineer": {},
            "designation_benchmarks": {},
            "monotonicity_checks": {},
            "summary_metrics": {},
        }

        # 1. ATS Scoring Evaluation
        for name, (doc_result, resume) in profiles.items():
            report = self.ats_engine.evaluate_resume(doc_result, resume)
            results["ats_readiness"][name] = {
                "overall_score": report.overall_score,
                "readiness_level": report.readiness_level,
                "strengths_count": len(report.summary_strengths),
                "weaknesses_count": len(report.summary_weaknesses),
                "category_scores": {k: v.score for k, v in report.category_breakdown.items()},
            }

        # 2. JD Matching Evaluation (AI Engineer JD & Backend JD)
        for name, (_, resume) in profiles.items():
            ai_match = self.matcher.evaluate_job_match(resume, extracted_ai_jd)
            backend_match = self.matcher.evaluate_job_match(resume, extracted_backend_jd)

            results["jd_matching_ai_engineer"][name] = {
                "overall_match_score": ai_match.overall_match_score,
                "match_tier": ai_match.match_tier,
                "mandatory_skills_match_rate": ai_match.mandatory_skills_match_rate,
                "matched_count": len(ai_match.matched_skills),
                "missing_count": len(ai_match.missing_skills),
            }

            results["jd_matching_backend_engineer"][name] = {
                "overall_match_score": backend_match.overall_match_score,
                "match_tier": backend_match.match_tier,
                "mandatory_skills_match_rate": backend_match.mandatory_skills_match_rate,
                "matched_count": len(backend_match.matched_skills),
                "missing_count": len(backend_match.missing_skills),
            }

        # 3. Designation Matching Evaluation across all 7 curated roles
        available_roles = [d["role_id"] for d in self.designation_service.get_available_roles().available_designations]
        matrix = {}
        for role_id in available_roles:
            matrix[role_id] = {}
            for name, (_, resume) in profiles.items():
                desig_report = self.designation_service.match_against_designation(resume, role_id)
                matrix[role_id][name] = {
                    "score": desig_report.match_report.overall_match_score,
                    "tier": desig_report.match_report.match_tier,
                }
        results["designation_benchmarks"] = matrix

        # 4. Monotonicity & Quality Checks
        ats_scores = results["ats_readiness"]
        ai_scores = results["jd_matching_ai_engineer"]

        # Strong candidate must outscore moderate and weak candidate
        ats_monotonic = (
            ats_scores["strong_ai"]["overall_score"] > ats_scores["moderate_python"]["overall_score"] > ats_scores["weak_sparse"]["overall_score"]
        )
        ai_jd_monotonic = (
            ai_scores["strong_ai"]["overall_match_score"] > ai_scores["moderate_python"]["overall_match_score"] > ai_scores["weak_sparse"]["overall_match_score"]
        )

        results["monotonicity_checks"] = {
            "ats_monotonicity_passed": ats_monotonic,
            "ai_jd_matching_monotonicity_passed": ai_jd_monotonic,
            "experienced_outscores_fresher_on_backend_jd": (
                results["jd_matching_backend_engineer"]["experienced_arch"]["overall_match_score"]
                > results["jd_matching_backend_engineer"]["fresh_ds"]["overall_match_score"]
            ),
        }

        # 5. Summary Metrics
        results["summary_metrics"] = {
            "total_benchmark_profiles": len(profiles),
            "total_designations_evaluated": len(available_roles),
            "total_matrix_combinations": len(profiles) * len(available_roles),
            "all_monotonicity_passed": all(results["monotonicity_checks"].values()),
        }

        return results
