# AI Career Intelligence Agent

An enterprise-grade, production AI career platform built across two phases:
**Resume Analysis → ATS Scoring → Job Matching → Proactive Discovery → Notification → Application Preparation → Tracking.**

---

## Architecture Overview

- **Presentation Layer**: Streamlit multi-page UI (`st.navigation`, `st.Page`).
- **API & Core Layer**: FastAPI (`/api/v1`) with Pydantic v2 schemas and validation.
- **AI Engine**: Official Google GenAI SDK (`google-genai`) with structured JSON schema outputs (`temperature=0.0`).
- **Scoring Engine**: Deterministic, 7-category weighted mathematical model ($100\%$ total weight).
- **Document Parser**: PyMuPDF (`fitz`) for PDF & `python-docx` for DOCX with magic-byte validation and character normalization.
- **Testing & Watchdog**: Pytest with `pytest-timeout` watchdog monitoring.

---

## Current Status: Phase 1 — Core AI Intelligence Engine

- [x] **Milestone 1**: Project Foundation, Architecture Specifications (`docs/architecture/`), PDF/DOCX Parser, Secure Storage.
- [x] **Milestone 2**: Gemini Structured Information Extraction, Typed Pydantic Schemas, Post-Validation Sanitizer.
- [x] **Milestone 3**: Deterministic 7-Category ATS Readiness Scoring Engine & Evidence-Backed Recommendation Generator.
- [x] **23/23 Automated Tests Passing** (`pytest -v --timeout=15`).
- [ ] **Milestone 4**: Job Description Extraction & Hybrid JD-Resume Matching Engine.
- [ ] **Milestone 5**: Benchmark Role Designation Matching.
- [ ] **Milestone 6**: Phase 1 Evaluation Gate.

---

## Quickstart

### 1. Configure Environment
```bash
cp .env.example .env
# Add your GEMINI_API_KEY
```

### 2. Run Tests
```powershell
$env:PYTHONPATH="backend"
pytest backend/tests -v --timeout=15
```

### 3. Start FastAPI Backend
```bash
uvicorn app.main:app --app-dir backend --reload --port 8000
```

### 4. Start Streamlit Frontend
```bash
streamlit run frontend/streamlit_app.py
```
