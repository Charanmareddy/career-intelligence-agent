import hashlib
import re
import io
from pathlib import Path
from typing import Tuple, List, Optional
import pymupdf as fitz
from docx import Document
from app.schemas.resume import DocumentExtractionResult, DocumentMetadata

class DocumentParserService:
    """
    Deterministic Document Parser Service for PDF and DOCX files.
    Extracts text, normalizes characters, generates metadata, and flags extraction warnings.
    """

    @staticmethod
    def calculate_sha256(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def validate_magic_bytes(content: bytes, extension: str) -> bool:
        ext = extension.lower().strip()
        if ext == ".pdf":
            return content.startswith(b"%PDF-")
        elif ext == ".docx":
            # DOCX is a zip container starting with PK\x03\x04
            return content.startswith(b"PK\x03\x04")
        return False

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans and normalizes extracted resume text.
        Removes null bytes and non-printable control chars, standardizes line breaks and whitespace.
        """
        if not text:
            return ""
        # Remove null bytes and non-printable characters (except \n, \r, \t)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
        # Normalize carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Replace 3 or more consecutive newlines with 2 newlines (preserve paragraphs)
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Normalize multiple horizontal spaces/tabs
        text = re.sub(r"[ \t]{2,}", " ", text)
        return text.strip()

    @classmethod
    def extract_from_pdf(cls, file_bytes: bytes) -> Tuple[str, int, List[str]]:
        warnings: List[str] = []
        full_text_parts: List[str] = []
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            page_count = len(doc)
            
            if page_count == 0:
                warnings.append("PDF document has 0 pages.")
                return "", 0, warnings

            for page_num in range(page_count):
                page = doc[page_num]
                page_text = page.get_text("text")
                if page_text.strip():
                    full_text_parts.append(page_text.strip())

            doc.close()
            extracted_text = "\n\n".join(full_text_parts)

            if not extracted_text.strip():
                warnings.append(
                    "No extractable text found in PDF. The document may be scanned or image-based."
                )

            return extracted_text, page_count, warnings

        except Exception as e:
            raise ValueError(f"Failed to parse PDF document: {str(e)}")

    @classmethod
    def extract_from_docx(cls, file_bytes: bytes) -> Tuple[str, int, List[str]]:
        warnings: List[str] = []
        try:
            doc = Document(io.BytesIO(file_bytes))
            parts: List[str] = []

            # Extract paragraphs
            for para in doc.paragraphs:
                p_text = para.text.strip()
                if p_text:
                    parts.append(p_text)

            # Extract table contents
            for table in doc.tables:
                for row in table.rows:
                    row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_cells:
                        parts.append(" | ".join(row_cells))

            extracted_text = "\n\n".join(parts)
            if not extracted_text.strip():
                warnings.append("No extractable text found in DOCX file.")

            return extracted_text, 1, warnings

        except Exception as e:
            raise ValueError(f"Failed to parse DOCX document: {str(e)}")

    @classmethod
    def parse_document(cls, file_bytes: bytes, filename: str) -> DocumentExtractionResult:
        file_path = Path(filename)
        ext = file_path.suffix.lower()

        if ext not in {".pdf", ".docx"}:
            raise ValueError(f"Unsupported file format '{ext}'. Only .pdf and .docx are supported.")

        if not cls.validate_magic_bytes(file_bytes, ext):
            raise ValueError(f"File magic bytes mismatch for extension '{ext}'. File may be corrupt or misnamed.")

        sha256 = cls.calculate_sha256(file_bytes)
        file_size = len(file_bytes)

        if ext == ".pdf":
            raw_text, page_count, warnings = cls.extract_from_pdf(file_bytes)
        else:
            raw_text, page_count, warnings = cls.extract_from_docx(file_bytes)

        cleaned = cls.clean_text(raw_text)
        words = len(cleaned.split()) if cleaned else 0
        chars = len(cleaned)

        if words < 20 and not warnings:
            warnings.append("Document text contains under 20 words; resume content appears minimal or unparsed.")

        metadata = DocumentMetadata(
            filename=filename,
            file_size_bytes=file_size,
            file_extension=ext,
            page_count=page_count,
            character_count=chars,
            word_count=words,
            sha256_hash=sha256
        )

        return DocumentExtractionResult(
            success=True,
            raw_text=raw_text,
            cleaned_text=cleaned,
            metadata=metadata,
            warnings=warnings
        )
