import requests
from typing import Dict, Any, Optional

BACKEND_URL = "http://localhost:8000"

class BackendAPIClient:
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip("/")

    def check_health(self) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            if resp.status_code == 200:
                return resp.json()
            return {"status": "unhealthy", "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}

    def get_supported_formats(self) -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/api/v1/resumes/supported-formats", timeout=5)
        resp.raise_for_status()
        return resp.json()

    def upload_resume(self, file_name: str, file_bytes: bytes, mime_type: str) -> Dict[str, Any]:
        files = {"file": (file_name, file_bytes, mime_type)}
        resp = requests.post(f"{self.base_url}/api/v1/resumes/upload", files=files, timeout=30)
        if resp.status_code != 200:
            error_detail = resp.json().get("detail", "Upload failed")
            raise RuntimeError(f"Error {resp.status_code}: {error_detail}")
        return resp.json()

    def extract_structured_resume(self, resume_id: str) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/api/v1/resumes/{resume_id}/extract-structure", timeout=60)
        if resp.status_code != 200:
            error_detail = resp.json().get("detail", "Structured extraction failed")
            raise RuntimeError(f"Error {resp.status_code}: {error_detail}")
        return resp.json()

api_client = BackendAPIClient()
