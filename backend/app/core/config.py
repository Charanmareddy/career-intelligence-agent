from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Career Intelligence Agent"
    API_V1_STR: str = "/api/v1"
    
    # Storage settings
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STORAGE_DIR: Path = BASE_DIR.parent / "storage"
    RESUME_STORAGE_DIR: Path = STORAGE_DIR / "resumes"
    
    # Upload constraints
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx"}
    ALLOWED_MIME_TYPES: set = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/octet-stream"
    }
    
    # Gemini API settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DEFAULT_GEMINI_MODEL: str = "gemini-2.5-flash"
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
settings.RESUME_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
