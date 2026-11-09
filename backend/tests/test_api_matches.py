"""
Tests: Job Matching and Designation Matching API Endpoints
============================================================
Tests the FastAPI endpoints in backend/app/api/v1/matches.py.
"""

import io
import fitz
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def create_synthetic_pdf(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.fixture
def uploaded_resume_id():
    """Uploads a test resume and returns the resume_id."""
    content = (
        "Devika Sharma\n"
        "AI / ML Engineer\n"
        "devika@example.com | +91 9876543210 | Bengaluru\n\n"
        "Professional Summary:\n"
        "Machine Learning Engineer with 2 years of experience building and deploying "
        "production ML models using Python, PyTorch, and FastAPI.\n\n"
        "Skills:\n"
        "Python, PyTorch, TensorFlow, Scikit-learn, Pandas, NumPy, SQL, FastAPI, Docker, Git\n\n"
        "Work Experience:\n"
        "ML Engineer at AlphaTech (Jan 2023 - Present)\n"
        "- Built NLP classification pipeline with BERT achieving 94% accuracy.\n"
        "- Deployed FastAPI inference service reducing latency by 40%.\n\n"
        "Education:\n"
        "B.Tech in Computer Science, IIT Madras, 2023\n"
    )
    pdf_bytes = create_synthetic_pdf(content)
    file_payload = {"file": ("devika_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    res = client.post("/api/v1/resumes/upload", files=file_payload)
    assert res.status_code == 200
    return res.json()["resume_id"]


def test_extract_jd_endpoint_empty():
    res = client.post("/api/v1/matches/extract-jd", json={"jd_text": ""})
    assert res.status_code == 400
    assert "required" in res.json()["detail"].lower()


def test_extract_jd_endpoint_success():
    jd = (
        "Senior Python Developer\n"
        "We are looking for a Python Developer with 3+ years experience.\n"
        "Mandatory skills: Python, FastAPI, PostgreSQL, Docker.\n"
        "Preferred: Redis, Celery, AWS.\n"
        "Responsibilities: Build scalable microservices and APIs."
    )
    res = client.post("/api/v1/matches/extract-jd", json={"jd_text": jd})
    assert res.status_code == 200
    data = res.json()
    assert "job_title" in data
    assert len(data["mandatory_skills"]) > 0


def test_list_designations_endpoint():
    res = client.get("/api/v1/matches/designations")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 7
    role_ids = [d["role_id"] for d in data["available_designations"]]
    assert "ai_engineer" in role_ids
    assert "data_scientist" in role_ids
    assert data["disclaimer"]


def test_match_designation_not_found_resume():
    res = client.post(
        "/api/v1/matches/designation",
        json={"resume_id": "nonexistent_id_123", "role_id": "ai_engineer"},
    )
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_match_designation_invalid_role(uploaded_resume_id):
    res = client.post(
        "/api/v1/matches/designation",
        json={"resume_id": uploaded_resume_id, "role_id": "invalid_unknown_role"},
    )
    assert res.status_code == 400
    assert "unknown role_id" in res.json()["detail"].lower()


def test_match_designation_success(uploaded_resume_id):
    res = client.post(
        "/api/v1/matches/designation",
        json={"resume_id": uploaded_resume_id, "role_id": "ai_engineer"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["role_id"] == "ai_engineer"
    assert "match_report" in data
    assert 0.0 <= data["match_report"]["overall_match_score"] <= 100.0
    assert data["disclaimer"]


def test_analyze_job_match_success(uploaded_resume_id):
    jd = (
        "AI Engineer\n"
        "Requirements:\n"
        "- Strong Python programming skills\n"
        "- Experience with PyTorch and Machine Learning\n"
        "- REST API development with FastAPI\n"
    )
    res = client.post(
        "/api/v1/matches/analyze",
        json={"resume_id": uploaded_resume_id, "jd_text": jd},
    )
    assert res.status_code == 200
    data = res.json()
    assert "overall_match_score" in data
    assert 0.0 <= data["overall_match_score"] <= 100.0
    assert len(data["matched_skills"]) > 0
