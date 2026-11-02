from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid

class DocumentMetadata(BaseModel):
    filename: str
    file_size_bytes: int
    file_extension: str
    page_count: Optional[int] = None
    character_count: int
    word_count: int
    sha256_hash: str

class DocumentExtractionResult(BaseModel):
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    success: bool
    raw_text: str
    cleaned_text: str
    metadata: DocumentMetadata
    warnings: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ResumeUploadResponse(BaseModel):
    resume_id: str
    filename: str
    file_size_bytes: int
    message: str
    extraction: Optional[DocumentExtractionResult] = None
