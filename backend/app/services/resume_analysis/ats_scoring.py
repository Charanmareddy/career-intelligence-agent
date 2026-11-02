import re
from typing import Dict, List, Tuple
from app.schemas.resume import DocumentExtractionResult
from app.schemas.structured_resume import StructuredResume
from app.schemas.ats_scoring import (
    ScoringWeightsConfig,
    CategoryScore,
    ATSReadinessReport,
    ResumeRecommendationItem
)

# Common action verbs for achievement scoring
STRONG_ACTION_VERBS = {
    "engineered", "architected", "developed", "built", "designed", "implemented",
    "optimized", "scaled", "automated", "reduced", "increased", "accelerated",
    "led", "directed", "managed", "deployed", "spearheaded", "orchestrated",
    "delivered", "resolved", "integrated", "constructed", "streamlined", "enhanced"
}

FIRST_PERSON_PRONOUNS = {r"\bi\b", r"\bmy\b", r"\bme\b", r"\bmine\b", r"\bwe\b", r"\bour\b", r"\bmy\b"}

class ATSScoringEngine:
    """
    Deterministic mathematical ATS Readiness scoring engine.
    Calculates transparent, versioned category scores without black-box opacity.
    """

    def __init__(self, config: ScoringWeightsConfig = None):
        self.config = config or ScoringWeightsConfig()
        if not self.config.validate_weights():
            raise ValueError("Scoring weights do not sum to 1.0 (100%).")

    def _score_document_parsing(self, extraction: DocumentExtractionResult) -> CategoryScore:
        score = 100.0
        strengths = []
        issues = []
        meta = extraction.metadata

        # Word count check
        if meta.word_count < 150:
            penalty = 40.0
            score -= penalty
            issues.append(f"Very low word count ({meta.word_count} words). ATS engines may flag this as incomplete.")
        elif meta.word_count > 1200:
            penalty = 15.0
            score -= penalty
            issues.append(f"Resume is exceptionally long ({meta.word_count} words). Standard 1-2 page resumes typically range 350-800 words.")
        else:
            strengths.append(f"Optimal document word count ({meta.word_count} words).")

        # Page count check
        if meta.page_count:
            if meta.page_count in (1, 2):
                strengths.append(f"Ideal page count ({meta.page_count} page(s)).")
            elif meta.page_count > 3:
                score -= 15.0
                issues.append(f"High page count ({meta.page_count} pages). Entry and mid-level resumes should be 1-2 pages.")

        # Parsing warnings
        if extraction.warnings:
            for w in extraction.warnings:
                score -= 20.0
                issues.append(f"Parser warning: {w}")
        else:
            strengths.append("Clean document text extraction without character or font corruption.")

        score = max(0.0, min(100.0, score))
        return CategoryScore(
            name="Document Parsing & Compatibility",
            score=round(score, 1),
            weight=self.config.document_parsing,
            weighted_score=round(score * self.config.document_parsing, 2),
            strengths=strengths,
            issues=issues
        )

    def _score_section_completeness(self, resume: StructuredResume) -> CategoryScore:
        score = 0.0
        strengths = []
        issues = []

        # Contact Info (25 pts)
        contact_pts = 0.0
        if resume.contact_info.full_name and resume.contact_info.full_name.lower() not in {"unknown", "n/a", "candidate"}:
            contact_pts += 10.0
        else:
            issues.append("Missing or unverifiable candidate full name.")

        if resume.contact_info.email:
            contact_pts += 5.0
        else:
            issues.append("Missing candidate contact email.")

        if resume.contact_info.phone:
            contact_pts += 5.0
        else:
            issues.append("Missing phone number.")

        if resume.contact_info.linkedin_url or resume.contact_info.github_url:
            contact_pts += 5.0
            strengths.append("Professional profile link (LinkedIn / GitHub) detected.")
        else:
            issues.append("Consider adding a verified LinkedIn or GitHub profile link.")

        score += contact_pts

        # Professional Summary (15 pts)
        if resume.professional_summary and len(resume.professional_summary.split()) >= 15:
            score += 15.0
            strengths.append("Clear professional executive summary present.")
        else:
            issues.append("Missing or very brief professional summary.")

        # Skills section (20 pts)
        total_skills = (
            len(resume.skills.languages) + len(resume.skills.frameworks_and_libraries) +
            len(resume.skills.databases) + len(resume.skills.cloud_and_devops) +
            len(resume.skills.ai_ml_tools)
        )
        if total_skills >= 5:
            score += 20.0
            strengths.append("Dedicated, categorized skills section identified.")
        elif total_skills > 0:
            score += 10.0
            issues.append("Limited technical skills listed (fewer than 5 skills).")
        else:
            issues.append("No technical skills detected.")

        # Experience or Internships (20 pts)
        if resume.work_experience or resume.internships:
            score += 20.0
            strengths.append("Work experience or internship history present.")
        else:
            issues.append("No work experience or internships found.")

        # Education (10 pts)
        if resume.education:
            score += 10.0
            strengths.append("Educational credentials detected.")
        else:
            issues.append("No education section detected.")

        # Projects or Certifications (10 pts)
        if resume.projects or resume.certifications:
            score += 10.0
            strengths.append("Projects or professional certifications present.")
        else:
            issues.append("No projects or certifications detected.")

        score = max(0.0, min(100.0, score))
        return CategoryScore(
            name="Section Completeness",
            score=round(score, 1),
            weight=self.config.section_completeness,
            weighted_score=round(score * self.config.section_completeness, 2),
            strengths=strengths,
            issues=issues
        )

    def _score_skills_presentation(self, resume: StructuredResume) -> CategoryScore:
        score = 0.0
        strengths = []
        issues = []
        skills = resume.skills

        categories_filled = 0
        if skills.languages:
            categories_filled += 1
        if skills.frameworks_and_libraries:
            categories_filled += 1
        if skills.databases:
            categories_filled += 1
        if skills.cloud_and_devops:
            categories_filled += 1
        if skills.ai_ml_tools:
            categories_filled += 1

        total_skills = (
            len(skills.languages) + len(skills.frameworks_and_libraries) +
            len(skills.databases) + len(skills.cloud_and_devops) +
            len(skills.ai_ml_tools) + len(skills.developer_tools)
        )

        # Categorization variety (40 pts)
        if categories_filled >= 4:
            score += 40.0
            strengths.append("Excellent skill taxonomy across languages, frameworks, databases, and infrastructure.")
        elif categories_filled >= 2:
            score += 25.0
            strengths.append("Good skills spread across multiple technical domains.")
        elif categories_filled == 1:
            score += 10.0
            issues.append("Skills are confined to a single narrow category; consider broadening.")
        else:
            issues.append("No categorized technical skills detected.")

        # Skill volume / balance (40 pts)
        if 8 <= total_skills <= 35:
            score += 40.0
            strengths.append(f"Balanced skill inventory count ({total_skills} skills).")
        elif total_skills > 35:
            score += 25.0
            issues.append(f"High skill count ({total_skills} skills). Keyword stuffing risks diluting core competencies.")
        elif total_skills > 0:
            score += 20.0
            issues.append(f"Low skill count ({total_skills} skills). Consider adding tools and frameworks used in projects.")
        else:
            issues.append("Zero technical skills listed.")

        # Soft skills presence (20 pts)
        if skills.soft_skills:
            score += 20.0
            strengths.append("Complementary collaboration or leadership skills included.")
        else:
            score += 10.0  # Optional but recommended

        score = max(0.0, min(100.0, score))
        return CategoryScore(
            name="Skills Presentation",
            score=round(score, 1),
            weight=self.config.skills_presentation,
            weighted_score=round(score * self.config.skills_presentation, 2),
            strengths=strengths,
            issues=issues
        )

    def _score_projects_and_experience(self, resume: StructuredResume) -> CategoryScore:
        score = 0.0
        strengths = []
        issues = []

        total_positions = len(resume.work_experience) + len(resume.internships)
        total_projects = len(resume.projects)

        if total_positions >= 2 or (total_positions >= 1 and total_projects >= 2):
            score += 40.0
            strengths.append(f"Solid depth with {total_positions} work position(s) and {total_projects} project(s).")
        elif total_positions >= 1 or total_projects >= 1:
            score += 25.0
            strengths.append(f"Found {total_positions} position(s) and {total_projects} project(s).")
        else:
            issues.append("Missing both professional work experience and documented project work.")

        # Bullet point verification
        all_bullets = []
        for exp in resume.work_experience:
            all_bullets.extend(exp.responsibilities_and_achievements)
        for proj in resume.projects:
            all_bullets.extend(proj.key_outcomes)

        if len(all_bullets) >= 6:
            score += 35.0
            strengths.append("Detailed descriptive bullets supporting work experience and projects.")
        elif len(all_bullets) >= 2:
            score += 20.0
            issues.append("Limited descriptive bullet points under experience and projects.")
        else:
            issues.append("Work experiences and projects lack descriptive bullet points.")

        # Technologies mapped to experiences/projects
        tech_mapped = any(exp.technologies_used for exp in resume.work_experience) or any(p.technologies_used for p in resume.projects)
        if tech_mapped:
            score += 25.0
            strengths.append("Technologies are explicitly mapped to specific roles and projects.")
        else:
            score += 10.0
            issues.append("Explicitly state which tools and languages were applied within each role or project.")

        score = max(0.0, min(100.0, score))
        return CategoryScore(
            name="Relevant Experience & Projects",
            score=round(score, 1),
            weight=self.config.projects_and_experience,
            weighted_score=round(score * self.config.projects_and_experience, 2),
            strengths=strengths,
            issues=issues
        )

    def _score_achievement_quality(self, resume: StructuredResume) -> CategoryScore:
        score = 0.0
        strengths = []
        issues = []

        bullets = []
        for exp in resume.work_experience:
            bullets.extend(exp.responsibilities_and_achievements)
        for proj in resume.projects:
            bullets.extend(proj.key_outcomes)

        if not bullets:
            return CategoryScore(
                name="Achievement Quality",
                score=0.0,
                weight=self.config.achievement_quality,
                weighted_score=0.0,
                strengths=[],
                issues=["No bullet points available to assess achievement impact."]
            )

        # 1. Action verb analysis (50 pts)
        action_verb_count = 0
        for b in bullets:
            first_word = b.strip().split()[0].lower().rstrip(":,.-") if b.strip() else ""
            if first_word in STRONG_ACTION_VERBS:
                action_verb_count += 1

        action_verb_ratio = action_verb_count / len(bullets)
        if action_verb_ratio >= 0.6:
            score += 50.0
            strengths.append(f"Strong action verbs lead {int(action_verb_ratio*100)}% of bullet statements.")
        elif action_verb_ratio >= 0.3:
            score += 30.0
            strengths.append("Moderate use of active verbs at start of bullet points.")
        else:
            score += 15.0
            issues.append("Many bullet points start with passive language rather than decisive action verbs (e.g. 'Engineered', 'Optimized', 'Architected').")

        # 2. Metric and quantification analysis (50 pts)
        metric_pattern = re.compile(r"(\b\d+%\b|\$\d+|\b\d+x\b|\b\d+\s*(?:ms|seconds|minutes|hours|users|gb|tb|million|k)\b)", re.IGNORECASE)
        metric_count = 0
        for b in bullets:
            if metric_pattern.search(b):
                metric_count += 1

        if metric_count >= 3:
            score += 50.0
            strengths.append(f"High quantification: {metric_count} bullets feature measurable impact metrics (%, scale, latency, ROI).")
        elif metric_count >= 1:
            score += 30.0
            strengths.append("Some quantified achievements detected.")
            issues.append("Quantify more results with measurable outcomes (e.g., 'reduced API latency by 35%').")
        else:
            score += 10.0
            issues.append("No quantified impact metrics found. Resumes with measurable figures score significantly higher with technical recruiters.")

        score = max(0.0, min(100.0, score))
        return CategoryScore(
            name="Achievement Quality",
            score=round(score, 1),
            weight=self.config.achievement_quality,
            weighted_score=round(score * self.config.achievement_quality, 2),
            strengths=strengths,
            issues=issues
        )

    def _score_language_and_clarity(self, resume: StructuredResume) -> CategoryScore:
        score = 100.0
        strengths = []
        issues = []

        bullets = []
        for exp in resume.work_experience:
            bullets.extend(exp.responsibilities_and_achievements)
        for proj in resume.projects:
            bullets.extend(proj.key_outcomes)

        # First person pronoun check
        first_person_violations = 0
        for b in bullets:
            for pattern in FIRST_PERSON_PRONOUNS:
                if re.search(pattern, b, re.IGNORECASE):
                    first_person_violations += 1
                    break

        if first_person_violations == 0:
            strengths.append("Professional third-person perspective maintained; no first-person pronouns (I, my, we).")
        else:
            score -= min(30.0, first_person_violations * 10.0)
            issues.append(f"Found {first_person_violations} instances of first-person pronouns ('I', 'we', 'my'). Use third-person action phrasing.")

        # Length check
        run_on_count = sum(1 for b in bullets if len(b.split()) > 45)
        fragment_count = sum(1 for b in bullets if len(b.split()) < 4)

        if run_on_count > 0:
            score -= min(25.0, run_on_count * 5.0)
            issues.append(f"{run_on_count} bullet(s) are run-on sentences (> 45 words). Keep statements concise (15-30 words).")

        if fragment_count > 0:
            score -= min(15.0, fragment_count * 5.0)
            issues.append(f"{fragment_count} bullet(s) are overly short fragments (< 4 words).")

        if run_on_count == 0 and fragment_count == 0 and bullets:
            strengths.append("Concise, readable bullet point length throughout.")

        score = max(0.0, min(100.0, score))
        return CategoryScore(
            name="Language & Clarity",
            score=round(score, 1),
            weight=self.config.language_and_clarity,
            weighted_score=round(score * self.config.language_and_clarity, 2),
            strengths=strengths,
            issues=issues
        )

    def _score_date_and_formatting(self, resume: StructuredResume) -> CategoryScore:
        score = 100.0
        strengths = []
        issues = []

        dates_found = 0
        missing_dates = 0

        for exp in resume.work_experience:
            if exp.start_date:
                dates_found += 1
            else:
                missing_dates += 1
            if exp.end_date:
                dates_found += 1
            else:
                missing_dates += 1

        for edu in resume.education:
            if edu.graduation_year:
                dates_found += 1
            else:
                missing_dates += 1

        if missing_dates > 0:
            penalty = min(40.0, missing_dates * 10.0)
            score -= penalty
            issues.append(f"Missing date indicators on {missing_dates} position(s) or degree(s).")
        else:
            strengths.append("Complete date coverage for all work experience and educational degrees.")

        # Check year format
        has_valid_years = any(re.search(r"\b(19|20)\d{2}\b", str(exp.start_date or "") + str(exp.end_date or "")) for exp in resume.work_experience)
        if has_valid_years:
            strengths.append("Standard 4-digit chronological year formatting used.")

        score = max(0.0, min(100.0, score))
        return CategoryScore(
            name="Date & Formatting Consistency",
            score=round(score, 1),
            weight=self.config.date_and_formatting,
            weighted_score=round(score * self.config.date_and_formatting, 2),
            strengths=strengths,
            issues=issues
        )

    def evaluate_resume(
        self,
        extraction: DocumentExtractionResult,
        structured_resume: StructuredResume
    ) -> ATSReadinessReport:
        """
        Executes deterministic evaluation across all 7 criteria and synthesizes the ATS report.
        """
        cat1 = self._score_document_parsing(extraction)
        cat2 = self._score_section_completeness(structured_resume)
        cat3 = self._score_skills_presentation(structured_resume)
        cat4 = self._score_projects_and_experience(structured_resume)
        cat5 = self._score_achievement_quality(structured_resume)
        cat6 = self._score_language_and_clarity(structured_resume)
        cat7 = self._score_date_and_formatting(structured_resume)

        categories = {
            "document_parsing": cat1,
            "section_completeness": cat2,
            "skills_presentation": cat3,
            "projects_and_experience": cat4,
            "achievement_quality": cat5,
            "language_and_clarity": cat6,
            "date_and_formatting": cat7,
        }

        total_weighted_score = sum(c.weighted_score for c in categories.values())
        total_score = round(max(0.0, min(100.0, total_weighted_score)), 1)

        # Qualitative level assignment
        if total_score >= 85.0:
            readiness_level = "Exceptional ATS Readiness"
        elif total_score >= 70.0:
            readiness_level = "Strong ATS Readiness"
        elif total_score >= 50.0:
            readiness_level = "Moderate ATS Readiness"
        else:
            readiness_level = "Needs Substantial Improvement"

        summary_strengths = []
        summary_weaknesses = []
        for cat in categories.values():
            if cat.score >= 75.0 and cat.strengths:
                summary_strengths.extend(cat.strengths[:2])
            elif cat.score < 60.0 and cat.issues:
                summary_weaknesses.extend(cat.issues[:2])

        missing_sections = []
        if not structured_resume.professional_summary:
            missing_sections.append("Professional Summary")
        if not (structured_resume.work_experience or structured_resume.internships):
            missing_sections.append("Work Experience / Internships")
        if not structured_resume.projects:
            missing_sections.append("Projects")
        if not structured_resume.certifications:
            missing_sections.append("Certifications")

        return ATSReadinessReport(
            overall_score=total_score,
            readiness_level=readiness_level,
            weights_version=self.config.version,
            category_breakdown=categories,
            summary_strengths=summary_strengths,
            summary_weaknesses=summary_weaknesses,
            missing_sections=missing_sections,
            parsing_warnings=extraction.warnings,
            recommendations=[]  # Populated by Gemini Recommender
        )

ats_scoring_engine = ATSScoringEngine()
