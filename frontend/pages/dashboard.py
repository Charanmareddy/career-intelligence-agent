import streamlit as st
import sys
from pathlib import Path

# Add frontend dir to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api_client.client import api_client

st.title("🎯 AI Career Intelligence Agent")
st.caption("AI-Powered Career Progression & Intelligence Platform — Phase 1: Core AI Intelligence Engine")

health = api_client.check_health()
col1, col2, col3 = st.columns(3)

with col1:
    if health.get("status") == "healthy":
        st.success("🟢 Backend API: Connected")
    else:
        st.warning("🟡 Backend API: Disconnected / Start FastAPI on :8000")

with col2:
    st.info("📦 Phase: Phase 1 (Deterministic Workflows)")

with col3:
    st.metric(label="Active Mode", value="Resume Intelligence")

st.markdown("---")
st.subheader("Platform Workflow Overview")
st.markdown("""
1. **Resume Analyzer**: Upload PDF or DOCX resumes. Validates magic bytes, extracts text, cleans formatting, and generates metadata.
2. **ATS Readiness Scoring**: Deterministic multi-category scoring (parsing, completeness, skills, experience, language).
3. **Job Description Matcher**: Compare your parsed resume against full JDs or curated designation benchmarks.
4. **Career Profile**: View and calibrate your persistent candidate profile and skills inventory.
""")
