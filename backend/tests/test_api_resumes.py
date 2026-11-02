import io
import fitz
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

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Phase 1" in data["phase"]

def test_supported_formats_endpoint():
    response = client.get("/api/v1/resumes/supported-formats")
    assert response.status_code == 200
    data = response.json()
    assert ".pdf" in data["allowed_extensions"]
    assert ".docx" in data["allowed_extensions"]
    assert data["max_size_mb"] == 10

def test_upload_resume_valid_pdf():
    pdf_bytes = create_synthetic_pdf("Alice Wonderland\nGenerative AI Engineer\nSkills: Python, Gemini, LangGraph")
    file_payload = {"file": ("alice_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    
    response = client.post("/api/v1/resumes/upload", files=file_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "alice_resume.pdf"
    assert "resume_id" in data
    assert data["extraction"]["success"] is True
    assert "Alice Wonderland" in data["extraction"]["cleaned_text"]
    assert data["extraction"]["metadata"]["page_count"] == 1

def test_upload_resume_invalid_extension():
    file_payload = {"file": ("malicious_script.sh", io.BytesIO(b"echo 'hack'"), "application/x-sh")}
    response = client.post("/api/v1/resumes/upload", files=file_payload)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_upload_resume_corrupt_content():
    # Misnamed file with invalid magic bytes
    file_payload = {"file": ("corrupt.pdf", io.BytesIO(b"not a pdf"), "application/pdf")}
    response = client.post("/api/v1/resumes/upload", files=file_payload)
    assert response.status_code == 422
    assert "magic bytes mismatch" in response.json()["detail"]
