import streamlit as st

st.set_page_config(
    page_title="AI Career Intelligence Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Phase 1 Pages
dashboard_page = st.Page("pages/dashboard.py", title="Dashboard", icon="📊", default=True)
resume_analyzer_page = st.Page("pages/resume_analyzer.py", title="Resume Analyzer", icon="📄")
job_matcher_page = st.Page("pages/job_matcher.py", title="Job Matcher", icon="🎯")
career_profile_page = st.Page("pages/career_profile.py", title="Career Profile", icon="👤")

pg = st.navigation({
    "Phase 1 Core Engine": [dashboard_page, resume_analyzer_page, job_matcher_page, career_profile_page]
})

pg.run()
