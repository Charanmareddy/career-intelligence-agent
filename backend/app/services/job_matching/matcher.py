import re
from typing import List, Dict, Tuple, Optional
from rapidfuzz import fuzz
from app.schemas.structured_resume import StructuredResume
from app.schemas.ats_scoring import ATSReadinessReport
from app.schemas.job_matching import (
    ExtractedJobRequirements,
    SkillMatchItem,
    MatchScoringWeights,
    JobMatchReport
)

# Canonical ontology alias dictionary
TECH_ONTOLOGY: Dict[str, List[str]] = {
    "python": ["python3", "py", "python programming"],
    "fastapi": ["fast api", "rest api", "starlette", "asgi"],
    "postgresql": ["postgres", "psql", "postgresql db", "rdbms"],
    "docker": ["containerization", "containers", "dockerfile", "docker-compose"],
    "kubernetes": ["k8s", "container orchestration", "helm"],
    "pytorch": ["torch", "deep learning", "neural networks"],
    "tensorflow": ["tf", "keras", "deep learning"],
    "langchain": ["langchain core", "llm framework"],
    "langgraph": ["agentic workflows", "multi-agent", "graph orchestration"],
    "aws": ["amazon web services", "ec2", "s3", "lambda"],
    "gcp": ["google cloud", "google cloud platform", "vertex ai"],
    "redis": ["in-memory cache", "redis cache", "redis queue"],
    "git": ["version control", "github", "gitlab"],
    "sql": ["structured query language", "relational database", "mysql", "sqlite"]
}

class HybridJobMatcher:
    """
    Deterministic Hybrid Job Matching Engine.
    Combines exact token matching, ontology alias expansion, RapidFuzz token distance,
    and verified resume evidence grounding.
    """

    def __init__(self, weights: Optional[MatchScoringWeights] = None):
        self.weights = weights or MatchScoringWeights()
        if not self.weights.validate_weights():
            raise ValueError("Match scoring weights do not sum to 1.0 (100%).")

    @classmethod
    def _normalize_token(cls, token: str) -> str:
        return re.sub(r"[^\w\s]", "", token.strip().lower())

    @classmethod
    def _collect_resume_evidence(cls, resume: StructuredResume) -> List[Tuple[str, str, str]]:
        """
        Gathers all text from resume with source section context.
        Returns tuples of (canonical_text, raw_evidence, section_name).
        """
        evidence_corpus: List[Tuple[str, str, str]] = []

        # Skills inventory
        for lang in resume.skills.languages:
            evidence_corpus.append((lang.lower(), f"Language: {lang}", "skills"))
        for fw in resume.skills.frameworks_and_libraries:
            evidence_corpus.append((fw.lower(), f"Framework: {fw}", "skills"))
        for db in resume.skills.databases:
            evidence_corpus.append((db.lower(), f"Database: {db}", "skills"))
        for cd in resume.skills.cloud_and_devops:
            evidence_corpus.append((cd.lower(), f"DevOps: {cd}", "skills"))
        for ai in resume.skills.ai_ml_tools:
            evidence_corpus.append((ai.lower(), f"AI Tool: {ai}", "skills"))
        for dt in resume.skills.developer_tools:
            evidence_corpus.append((dt.lower(), f"Tool: {dt}", "skills"))

        # Work experience bullets & tools
        for exp in resume.work_experience:
            for b in exp.responsibilities_and_achievements:
                evidence_corpus.append((b.lower(), f"{exp.company} ({exp.job_title}): {b}", "work_experience"))
            for t in exp.technologies_used:
                evidence_corpus.append((t.lower(), f"{exp.company} tech: {t}", "work_experience"))

        # Projects
        for p in resume.projects:
            evidence_corpus.append((p.description.lower(), f"Project '{p.project_title}': {p.description}", "projects"))
            for out in p.key_outcomes:
                evidence_corpus.append((out.lower(), f"Project '{p.project_title}': {out}", "projects"))
            for t in p.technologies_used:
                evidence_corpus.append((t.lower(), f"Project '{p.project_title}' tech: {t}", "projects"))

        # Education & Certifications
        for edu in resume.education:
            evidence_corpus.append((f"{edu.degree} {edu.field_of_study}".lower(), f"{edu.degree} in {edu.field_of_study} ({edu.institution})", "education"))
        for cert in resume.certifications:
            evidence_corpus.append((cert.name.lower(), f"Cert: {cert.name} ({cert.issuing_organization})", "certifications"))

        return evidence_corpus

    def match_skill(
        self,
        skill_req: str,
        evidence_corpus: List[Tuple[str, str, str]],
        is_mandatory: bool = True
    ) -> SkillMatchItem:
        req_norm = self._normalize_token(skill_req)
        aliases = TECH_ONTOLOGY.get(req_norm, [])

        best_score = 0.0
        best_match_term = None
        best_evidence = None
        best_section = None

        for text_lower, raw_evidence, section in evidence_corpus:
            # 1. Exact match
            if req_norm in text_lower:
                return SkillMatchItem(
                    requirement=skill_req,
                    match_status="MATCHED",
                    matched_term=skill_req,
                    similarity_score=100.0,
                    is_mandatory=is_mandatory,
                    supporting_evidence=raw_evidence,
                    source_section=section
                )

            # 2. Ontology alias check
            for alias in aliases:
                if alias in text_lower:
                    return SkillMatchItem(
                        requirement=skill_req,
                        match_status="MATCHED",
                        matched_term=alias.title(),
                        similarity_score=95.0,
                        is_mandatory=is_mandatory,
                        supporting_evidence=raw_evidence,
                        source_section=section
                    )

            # 3. Fuzzy partial ratio
            fuzzy_ratio = fuzz.partial_ratio(req_norm, text_lower)
            if fuzzy_ratio > best_score:
                best_score = fuzzy_ratio
                best_match_term = skill_req
                best_evidence = raw_evidence
                best_section = section

        # Threshold categorization
        if best_score >= 85.0:
            status = "MATCHED"
        elif best_score >= 65.0:
            status = "PARTIALLY_MATCHED"
        else:
            status = "MISSING"

        return SkillMatchItem(
            requirement=skill_req,
            match_status=status,
            matched_term=best_match_term if status != "MISSING" else None,
            similarity_score=round(best_score, 1),
            is_mandatory=is_mandatory,
            supporting_evidence=best_evidence if status != "MISSING" else None,
            source_section=best_section if status != "MISSING" else None
        )

    def evaluate_job_match(
        self,
        resume: StructuredResume,
        jd: ExtractedJobRequirements,
        ats_report: Optional[ATSReadinessReport] = None
    ) -> JobMatchReport:
        evidence_corpus = self._collect_resume_evidence(resume)

        matched_skills: List[SkillMatchItem] = []
        partially_matched: List[SkillMatchItem] = []
        missing_skills: List[SkillMatchItem] = []

        # Evaluate Mandatory Skills
        mandatory_hits = 0
        for skill in jd.mandatory_skills:
            item = self.match_skill(skill, evidence_corpus, is_mandatory=True)
            if item.match_status == "MATCHED":
                matched_skills.append(item)
                mandatory_hits += 1
            elif item.match_status == "PARTIALLY_MATCHED":
                partially_matched.append(item)
                mandatory_hits += 0.5
            else:
                missing_skills.append(item)

        # Evaluate Preferred Skills
        preferred_hits = 0
        for skill in jd.preferred_skills:
            item = self.match_skill(skill, evidence_corpus, is_mandatory=False)
            if item.match_status == "MATCHED":
                matched_skills.append(item)
                preferred_hits += 1
            elif item.match_status == "PARTIALLY_MATCHED":
                partially_matched.append(item)
                preferred_hits += 0.5
            else:
                missing_skills.append(item)

        m_rate = (mandatory_hits / len(jd.mandatory_skills)) if jd.mandatory_skills else 1.0
        p_rate = (preferred_hits / len(jd.preferred_skills)) if jd.preferred_skills else 1.0

        # Weighted Score Computation
        # 1. Required skills (25%)
        score_required_skills = m_rate * 100.0

        # 2. Experience & projects (20%)
        exp_score = 0.0
        candidate_years = len(resume.work_experience) * 1.5 + len(resume.internships) * 0.5
        required_years = jd.experience_years_required or 1.0
        if candidate_years >= required_years:
            exp_score = 100.0
        else:
            exp_score = (candidate_years / required_years) * 100.0

        # 3. Keyword coverage (15%)
        total_jd_keywords = len(jd.mandatory_skills) + len(jd.preferred_skills)
        matched_count = len(matched_skills) + 0.5 * len(partially_matched)
        keyword_score = (matched_count / total_jd_keywords * 100.0) if total_jd_keywords else 100.0

        # 4. Technical and domain alignment (15%)
        domain_matches = sum(1 for d in jd.domain_knowledge if any(d.lower() in t[0] for t in evidence_corpus))
        domain_score = (domain_matches / len(jd.domain_knowledge) * 100.0) if jd.domain_knowledge else 80.0

        # 5. Responsibilities evidence (10%)
        resp_score = min(100.0, len(matched_skills) * 20.0)

        # 6. Education and certifications (10%)
        edu_score = 100.0 if resume.education else 50.0

        # 7. ATS readability (5%)
        ats_score = ats_report.overall_score if ats_report else 85.0

        overall_score = (
            score_required_skills * self.weights.required_skills_and_qualifications +
            exp_score * self.weights.relevant_experience_and_projects +
            keyword_score * self.weights.keyword_coverage +
            domain_score * self.weights.technical_and_domain_alignment +
            resp_score * self.weights.responsibilities_evidence +
            edu_score * self.weights.education_and_certifications +
            ats_score * self.weights.ats_readability
        )
        overall_score = round(max(0.0, min(100.0, overall_score)), 1)

        # Qualitative Tier
        if overall_score >= 85.0:
            tier = "High Match (Strong Candidate)"
        elif overall_score >= 70.0:
            tier = "Good Match"
        elif overall_score >= 50.0:
            tier = "Moderate Match"
        else:
            tier = "Low Match (Skill Gaps Identified)"

        # Tailoring recommendations
        recs: List[str] = []
        if missing_skills:
            missing_names = ", ".join(item.requirement for item in missing_skills[:4])
            recs.append(f"Highlight any experience or coursework related to missing requirements: {missing_names}.")
        if partially_matched:
            partial_names = ", ".join(item.requirement for item in partially_matched[:3])
            recs.append(f"Make usage of partially matched skills explicit in your project descriptions: {partial_names}.")
        if exp_score < 70.0 and jd.experience_years_required:
            recs.append(f"Position emphasizes {jd.experience_years_required} years experience. Foreground hands-on technical ownership to offset tenure.")

        return JobMatchReport(
            job_title=jd.job_title,
            overall_match_score=overall_score,
            match_tier=tier,
            weights_version=self.weights.version,
            mandatory_skills_match_rate=round(m_rate * 100.0, 1),
            preferred_skills_match_rate=round(p_rate * 100.0, 1),
            matched_skills=matched_skills,
            partially_matched_skills=partially_matched,
            missing_skills=missing_skills,
            experience_alignment={
                "candidate_experience_indicator": f"{candidate_years:.1f} years equivalent",
                "jd_required": f"{required_years:.1f} years"
            },
            education_alignment={
                "candidate_degrees": ", ".join(e.degree for e in resume.education) if resume.education else "None listed",
                "jd_requirement": jd.education_level_required or "Not specified"
            },
            tailoring_recommendations=recs
        )

job_matcher = HybridJobMatcher()
