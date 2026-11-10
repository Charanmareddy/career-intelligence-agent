import requests
from typing import Dict, Any, Optional

BACKEND_URL = "http://localhost:8000"

class BackendAPIClient:
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip("/")

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, timeout: int = 15) -> Dict[str, Any]:
        """Generic GET helper targeting the FastAPI backend."""
        path = endpoint if endpoint.startswith("/api/v1") else f"/api/v1{endpoint if endpoint.startswith('/') else '/' + endpoint}"
        url = f"{self.base_url}{path}"
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
            return {"error": resp.json().get("detail", f"HTTP {resp.status_code}")}
        except Exception as e:
            return {"error": str(e)}

    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None, timeout: int = 60) -> Dict[str, Any]:
        """Generic POST helper targeting the FastAPI backend."""
        path = endpoint if endpoint.startswith("/api/v1") else f"/api/v1{endpoint if endpoint.startswith('/') else '/' + endpoint}"
        url = f"{self.base_url}{path}"
        try:
            resp = requests.post(url, json=json, files=files, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
            return {"error": resp.json().get("detail", f"HTTP {resp.status_code}")}
        except Exception as e:
            return {"error": str(e)}

    def check_health(self) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            if resp.status_code == 200:
                return resp.json()
            return {"status": "unhealthy", "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}

    def get_supported_formats(self) -> Dict[str, Any]:
        return self.get("/resumes/supported-formats")

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


# Alias for backward and forward compatibility
APIClient = BackendAPIClient
api_client = BackendAPIClient()
