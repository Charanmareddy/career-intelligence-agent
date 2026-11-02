"""
Designation Matcher Service
============================

Matches a candidate's structured resume against curated role profiles
to produce a benchmark-style designation match report.

Architecture Decision:
    This service converts a RoleProfile into an ExtractedJobRequirements object
    and delegates matching entirely to the existing HybridJobMatcher.
    This means:
    - Zero duplication of matching logic.
    - Designation matching automatically benefits from any improvements to HybridJobMatcher.
    - Role profile curation is the only designation-specific concern.

DISCLAIMER: All scores are based on platform-curated role profiles representing
general market expectations. They are NOT sourced from any specific employer's
job description. Scores are indicative benchmarks for skill gap identification only.
"""

import logging
from typing import List, Optional

from app.schemas.structured_resume import StructuredResume
from app.schemas.job_matching import ExtractedJobRequirements
from app.schemas.designation_matching import (
    RoleProfile,
    DesignationMatchReport,
    DesignationListResponse,
)
from app.services.job_matching.matcher import HybridJobMatcher
from app.services.job_matching.role_profiles import ROLE_PROFILES

logger = logging.getLogger(__name__)


def _role_profile_to_job_requirements(profile: RoleProfile) -> ExtractedJobRequirements:
    """
    Convert a RoleProfile into ExtractedJobRequirements so HybridJobMatcher can
    process it without modification.

    Mapping logic:
        - mandatory_skills → mandatory_skills (hard requirements for HybridJobMatcher)
        - preferred_skills → preferred_skills
        - preferred_experience_years → experience_years_required (target bar)
        - domain_knowledge → domain_knowledge
        - education_signals → education_level_required (joined as readable string)
        - display_name → job_title
        - description → key_responsibilities[0]
    """
    education_signal = (
        ", ".join(profile.education_signals) if profile.education_signals else None
    )
    return ExtractedJobRequirements(
        job_title=profile.display_name,
        company_name=None,
        experience_years_required=profile.preferred_experience_years,
        education_level_required=education_signal,
        mandatory_skills=profile.mandatory_skills,
        preferred_skills=profile.preferred_skills,
        key_responsibilities=[profile.description],
        domain_knowledge=profile.domain_knowledge,
    )


class DesignationMatcherService:
    """
    Service that matches a candidate's resume against curated role designation profiles.

    This service reuses HybridJobMatcher for all scoring and evidence collection.
    The only designation-specific logic is:
    1. Loading the correct role profile by role_id.
    2. Converting it to ExtractedJobRequirements.
    3. Wrapping the result in a DesignationMatchReport with metadata and disclaimer.

    Example usage:
        service = DesignationMatcherService()
        available = service.get_available_roles()
        report = service.match_against_designation(resume, "ai_engineer")
    """

    def __init__(self, matcher: Optional[HybridJobMatcher] = None):
        """
        Args:
            matcher: Optional HybridJobMatcher instance for dependency injection
                     (used in tests to inject controlled matchers).
                     Defaults to the module-level singleton.
        """
        self._matcher = matcher or HybridJobMatcher()
        self._profiles = ROLE_PROFILES

    def get_available_roles(self) -> DesignationListResponse:
        """
        Returns the list of available curated designation profiles.

        Returns:
            DesignationListResponse with role ids, names, and descriptions.
        """
        designations = [
            {
                "role_id": profile.role_id,
                "display_name": profile.display_name,
                "description": profile.description,
                "version": profile.version,
            }
            for profile in self._profiles.values()
        ]
        return DesignationListResponse(
            available_designations=designations,
            total=len(designations),
        )

    def match_against_designation(
        self,
        resume: StructuredResume,
        role_id: str,
    ) -> DesignationMatchReport:
        """
        Matches the candidate's structured resume against the curated profile
        for the specified role_id.

        Args:
            resume: The candidate's extracted, structured resume data.
            role_id: The role identifier (e.g., "ai_engineer", "data_scientist").
                     Must be one of the keys in ROLE_PROFILES.

        Returns:
            DesignationMatchReport containing the full match result, score,
            evidence, skill gaps, and the disclaimer.

        Raises:
            ValueError: If role_id is not found in available profiles.
        """
        profile = self._profiles.get(role_id)
        if not profile:
            available = ", ".join(self._profiles.keys())
            raise ValueError(
                f"Unknown role_id '{role_id}'. "
                f"Available designations: {available}"
            )

        logger.info(
            "Starting designation match: candidate='%s', role='%s' (v%s)",
            resume.contact_info.full_name,
            profile.display_name,
            profile.version,
        )

        # Convert RoleProfile → ExtractedJobRequirements for HybridJobMatcher
        job_requirements = _role_profile_to_job_requirements(profile)

        # Delegate all matching logic to HybridJobMatcher
        match_report = self._matcher.evaluate_job_match(resume, job_requirements)

        logger.info(
            "Designation match complete: role='%s', score=%.1f, tier='%s'",
            profile.display_name,
            match_report.overall_match_score,
            match_report.match_tier,
        )

        return DesignationMatchReport(
            role_id=profile.role_id,
            role_display_name=profile.display_name,
            role_version=profile.version,
            role_description=profile.description,
            match_report=match_report,
            assumptions_applied=profile.assumptions,
        )

    def get_role_profile(self, role_id: str) -> RoleProfile:
        """
        Returns the raw RoleProfile for a given role_id.
        Useful for displaying profile details before running a match.

        Raises:
            ValueError: If role_id is not found.
        """
        profile = self._profiles.get(role_id)
        if not profile:
            available = ", ".join(self._profiles.keys())
            raise ValueError(
                f"Unknown role_id '{role_id}'. Available: {available}"
            )
        return profile


# Module-level singleton
designation_matcher_service = DesignationMatcherService()
