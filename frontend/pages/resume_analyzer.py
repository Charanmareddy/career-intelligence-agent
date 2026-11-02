import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api_client.client import api_client

st.title("📄 Resume Analyzer & Structured Intelligence")
st.markdown("Upload your resume (**PDF** or **DOCX**) to extract text, inspect ATS formatting, and extract structured candidate profiles via Gemini.")

uploaded_file = st.file_uploader("Select Resume", type=["pdf", "docx"])

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    file_name = uploaded_file.name
    mime_type = uploaded_file.type or "application/octet-stream"

    st.write(f"📁 Selected file: **{file_name}** ({len(file_bytes) / 1024:.1f} KB)")

    col_btn1, col_btn2 = st.columns([1, 1])

    with col_btn1:
        extract_text_clicked = st.button("1. Extract Raw Document Text", type="secondary")

    if extract_text_clicked or "current_resume" in st.session_state:
        if extract_text_clicked:
            with st.spinner("Validating document and extracting text via FastAPI backend..."):
                try:
                    res = api_client.upload_resume(file_name, file_bytes, mime_type)
                    st.session_state["current_resume"] = res
                    st.success("Document successfully uploaded and parsed!")
                except Exception as e:
                    st.error(f"Extraction failed: {str(e)}")

        if "current_resume" in st.session_state:
            res = st.session_state["current_resume"]
            resume_id = res.get("resume_id")
            extraction = res.get("extraction", {})
            metadata = extraction.get("metadata", {})
            warnings = extraction.get("warnings", [])

            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Word Count", metadata.get("word_count", 0))
            m2.metric("Character Count", metadata.get("character_count", 0))
            m3.metric("Pages / Sections", metadata.get("page_count", 1))
            m4.metric("Format", metadata.get("file_extension", "").upper())

            if warnings:
                st.warning("⚠️ **Document Warnings:**")
                for w in warnings:
                    st.markdown(f"- {w}")

            tab_text, tab_structured = st.tabs(["Cleaned Document Text", "Structured Candidate Intelligence"])

            with tab_text:
                cleaned_text = extraction.get("cleaned_text", "")
                st.text_area("Extracted Resume Text", value=cleaned_text, height=300)
                with st.expander("Technical Metadata"):
                    st.json(metadata)

            with tab_structured:
                st.markdown("#### Gemini Structured Information Extraction")
                st.caption("Converts unstructured resume text into validated, typed candidate intelligence (skills, experiences, projects, education).")

                if st.button("Run Gemini Structured Extraction", type="primary", key="btn_structured"):
                    with st.spinner("Invoking Gemini structured extraction engine with Pydantic validation..."):
                        try:
                            structured_data = api_client.extract_structured_resume(resume_id)
                            st.session_state["structured_data"] = structured_data
                            st.success("Structured extraction completed!")
                        except Exception as e:
                            st.error(f"AI Extraction failed: {str(e)}")

                if "structured_data" in st.session_state:
                    data = st.session_state["structured_data"]
                    contact = data.get("contact_info", {})
                    skills = data.get("skills", {})

                    st.subheader(f"👤 {contact.get('full_name', 'Candidate')}")
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"📧 **Email:** {contact.get('email') or 'N/A'}")
                    c2.write(f"📱 **Phone:** {contact.get('phone') or 'N/A'}")
                    c3.write(f"📍 **Location:** {contact.get('location') or 'N/A'}")

                    if data.get("professional_summary"):
                        st.markdown(f"**Professional Summary:**\n> {data['professional_summary']}")

                    st.markdown("---")
                    st.subheader("🛠️ Categorized Skills Inventory")
                    sk_cols = st.columns(3)
                    with sk_cols[0]:
                        st.markdown("**Languages**")
                        for l in skills.get("languages", []):
                            st.markdown(f"- `{l}`")
                        st.markdown("**Databases**")
                        for d in skills.get("databases", []):
                            st.markdown(f"- `{d}`")
                    with sk_cols[1]:
                        st.markdown("**Frameworks & Libraries**")
                        for f in skills.get("frameworks_and_libraries", []):
                            st.markdown(f"- `{f}`")
                        st.markdown("**Cloud & DevOps**")
                        for c in skills.get("cloud_and_devops", []):
                            st.markdown(f"- `{c}`")
                    with sk_cols[2]:
                        st.markdown("**AI / ML Tools**")
                        for a in skills.get("ai_ml_tools", []):
                            st.markdown(f"- `{a}`")
                        st.markdown("**Soft Skills**")
                        for s in skills.get("soft_skills", []):
                            st.markdown(f"- `{s}`")

                    st.markdown("---")
                    st.subheader("💼 Work Experience & Projects")
                    exp_tab, proj_tab, edu_tab = st.tabs(["Experience", "Projects", "Education & Certifications"])
                    
                    with exp_tab:
                        work_exp = data.get("work_experience", [])
                        if not work_exp:
                            st.info("No formal work experience detected.")
                        for exp in work_exp:
                            st.markdown(f"**{exp.get('job_title')}** at *{exp.get('company')}* ({exp.get('start_date', '')} - {exp.get('end_date', '')})")
                            for bullet in exp.get("responsibilities_and_achievements", []):
                                st.markdown(f"- {bullet}")
                            if exp.get("technologies_used"):
                                st.caption("Technologies: " + ", ".join(exp.get("technologies_used")))
                            st.markdown("---")

                    with proj_tab:
                        projects = data.get("projects", [])
                        if not projects:
                            st.info("No projects listed.")
                        for p in projects:
                            st.markdown(f"**{p.get('project_title')}**")
                            st.write(p.get("description", ""))
                            for out in p.get("key_outcomes", []):
                                st.markdown(f"- {out}")
                            if p.get("technologies_used"):
                                st.caption("Tech: " + ", ".join(p.get("technologies_used")))
                            st.markdown("---")

                    with edu_tab:
                        for edu in data.get("education", []):
                            st.markdown(f"🎓 **{edu.get('degree')}** in {edu.get('field_of_study')} - *{edu.get('institution')}* ({edu.get('graduation_year')})")
                        for cert in data.get("certifications", []):
                            st.markdown(f"📜 **{cert.get('name')}** — {cert.get('issuing_organization')} ({cert.get('issue_date')})")

                    if data.get("extraction_notes"):
                        st.markdown("#### ℹ️ Quality & Validation Notes")
                        for note in data.get("extraction_notes"):
                            st.markdown(f"- {note}")
