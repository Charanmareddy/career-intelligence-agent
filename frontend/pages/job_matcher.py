"""
Job Matcher Page — Milestone 5
================================
Two-tab interface:
  Tab 1: JD Match — paste a raw job description to run hybrid JD-resume matching.
  Tab 2: Designation Benchmark — select a curated role profile and benchmark your resume.
"""

import streamlit as st
from frontend.api_client.client import APIClient

st.set_page_config(page_title="Job Matcher | AI Career Intelligence", page_icon="🎯")

client = APIClient()

st.title("🎯 Job Matcher")
st.markdown(
    "Understand how well your resume aligns with a specific job description "
    "or benchmark yourself against a curated role profile."
)
st.divider()

# ─── Sidebar: Resume ID input ─────────────────────────────────────────────────
with st.sidebar:
    st.header("📄 Resume Selection")
    resume_id = st.text_input(
        "Resume ID",
        placeholder="e.g. abc123",
        help="Upload your resume on the Resume Analyzer page first, then paste the Resume ID here.",
    )
    if not resume_id:
        st.warning("Enter a Resume ID to enable matching.")

# ─── Main tabs ────────────────────────────────────────────────────────────────
tab_jd, tab_designation = st.tabs([
    "📝 Job Description Match",
    "🏷️ Designation Benchmark",
])


# ── Tab 1: JD Match ───────────────────────────────────────────────────────────
with tab_jd:
    st.subheader("Job Description Match")
    st.markdown(
        "Paste the full job description text. The engine will extract requirements "
        "using Gemini (with heuristic fallback) and score your resume against them."
    )

    jd_text = st.text_area(
        "Job Description Text",
        height=280,
        placeholder="Paste the complete job description here…",
    )

    if st.button("🔍 Analyze Match", key="btn_jd_match", type="primary"):
        if not resume_id:
            st.error("Please enter your Resume ID in the sidebar first.")
        elif not jd_text.strip():
            st.error("Please paste a job description.")
        else:
            with st.spinner("Analyzing job match…"):
                result = client.post(
                    "/matches/analyze",
                    {"resume_id": resume_id, "jd_text": jd_text},
                )

            if result.get("error"):
                st.error(f"❌ Error: {result['error']}")
            else:
                _render_match_report(result)


# ── Tab 2: Designation Benchmark ──────────────────────────────────────────────
with tab_designation:
    st.subheader("Designation Benchmark")
    st.markdown(
        "Select a target role to benchmark your resume against a curated profile "
        "representing general market expectations."
    )
    st.info(
        "⚠️ **Disclaimer**: Profiles are curated benchmarks, not sourced from any specific "
        "employer's job description. Scores are directional gap indicators only.",
        icon="ℹ️",
    )

    # Load available designations
    with st.spinner("Loading available roles…"):
        designations_data = client.get("/matches/designations")

    if designations_data.get("error"):
        st.error(f"Failed to load designations: {designations_data['error']}")
    else:
        available = designations_data.get("available_designations", [])
        role_options = {d["display_name"]: d["role_id"] for d in available}

        selected_display = st.selectbox(
            "Select Target Role",
            options=list(role_options.keys()),
            help="Choose the designation you are targeting.",
        )
        selected_role_id = role_options.get(selected_display)

        # Show role description
        for d in available:
            if d["role_id"] == selected_role_id:
                st.caption(f"📌 {d['description']}")
                break

        if st.button("📊 Run Designation Match", key="btn_designation_match", type="primary"):
            if not resume_id:
                st.error("Please enter your Resume ID in the sidebar first.")
            else:
                with st.spinner(f"Benchmarking against '{selected_display}'…"):
                    result = client.post(
                        "/matches/designation",
                        {"resume_id": resume_id, "role_id": selected_role_id},
                    )

                if result.get("error"):
                    st.error(f"❌ Error: {result['error']}")
                else:
                    # DesignationMatchReport wraps JobMatchReport inside match_report
                    match_report = result.get("match_report", {})
                    st.markdown(f"### Results for: {result.get('role_display_name', selected_display)}")
                    _render_match_report(match_report)

                    # Show assumptions
                    assumptions = result.get("assumptions_applied", [])
                    if assumptions:
                        with st.expander("📋 Profile Assumptions", expanded=False):
                            for a in assumptions:
                                st.markdown(f"- {a}")

                    st.caption(result.get("disclaimer", ""))


# ─── Shared render function ───────────────────────────────────────────────────
def _render_match_report(report: dict):
    """Renders a JobMatchReport dict as a structured Streamlit UI."""
    score = report.get("overall_match_score", 0)
    tier = report.get("match_tier", "Unknown")
    job_title = report.get("job_title", "")

    # Score metric row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Overall Match", f"{score:.1f}%")
    col2.metric("Match Tier", tier)
    col3.metric(
        "Mandatory Skills",
        f"{report.get('mandatory_skills_match_rate', 0):.1f}%",
    )
    col4.metric(
        "Preferred Skills",
        f"{report.get('preferred_skills_match_rate', 0):.1f}%",
    )

    # Score bar
    st.progress(min(int(score), 100))

    st.divider()

    # Skills breakdown
    col_left, col_right = st.columns(2)

    with col_left:
        matched = report.get("matched_skills", [])
        partial = report.get("partially_matched_skills", [])
        st.markdown(f"#### ✅ Matched Skills ({len(matched)})")
        if matched:
            for skill in matched:
                evidence = skill.get("supporting_evidence", "")
                badge = "🔑" if skill.get("is_mandatory") else "⭐"
                st.markdown(
                    f"{badge} **{skill['requirement']}** — *{skill.get('matched_term', skill['requirement'])}*"
                )
                if evidence:
                    st.caption(f"   Evidence: {evidence[:120]}…" if len(evidence) > 120 else f"   Evidence: {evidence}")
        else:
            st.caption("No skills directly matched.")

        if partial:
            st.markdown(f"#### 🟡 Partial Matches ({len(partial)})")
            for skill in partial:
                st.markdown(f"- **{skill['requirement']}** ≈ {skill.get('matched_term', '?')} ({skill.get('similarity_score', 0):.0f}%)")

    with col_right:
        missing = report.get("missing_skills", [])
        st.markdown(f"#### ❌ Missing Skills ({len(missing)})")
        if missing:
            mandatory_missing = [s for s in missing if s.get("is_mandatory")]
            optional_missing = [s for s in missing if not s.get("is_mandatory")]
            if mandatory_missing:
                st.markdown("**Critical gaps (mandatory):**")
                for skill in mandatory_missing:
                    st.markdown(f"- 🔴 {skill['requirement']}")
            if optional_missing:
                st.markdown("**Preferred gaps:**")
                for skill in optional_missing[:5]:
                    st.markdown(f"- 🟠 {skill['requirement']}")
        else:
            st.success("No missing skills — strong match!")

    st.divider()

    # Experience & Education alignment
    exp_align = report.get("experience_alignment", {})
    edu_align = report.get("education_alignment", {})
    if exp_align or edu_align:
        st.markdown("#### 📊 Alignment Details")
        col_a, col_b = st.columns(2)
        if exp_align:
            with col_a:
                st.markdown("**Experience**")
                for k, v in exp_align.items():
                    st.caption(f"{k}: {v}")
        if edu_align:
            with col_b:
                st.markdown("**Education**")
                for k, v in edu_align.items():
                    st.caption(f"{k}: {v}")

    # Tailoring recommendations
    recs = report.get("tailoring_recommendations", [])
    if recs:
        with st.expander("💡 Tailoring Recommendations", expanded=True):
            for r in recs:
                st.markdown(f"- {r}")

    # Disclaimer
    disclaimer = report.get("disclaimer", "")
    if disclaimer:
        st.caption(f"ℹ️ {disclaimer}")
