import io
import pytest
import fitz  # PyMuPDF
from docx import Document
from app.services.document_parser.parser import DocumentParserService

def create_synthetic_pdf(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def create_synthetic_docx(paragraphs: list, table_data: list = None) -> bytes:
    doc = Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    if table_data:
        table = doc.add_table(rows=len(table_data), cols=len(table_data[0]))
        for r_idx, row in enumerate(table_data):
            for c_idx, cell_value in enumerate(row):
                table.cell(r_idx, c_idx).text = cell_value
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def test_pdf_extraction_success():
    sample_text = "John Doe\nSenior AI Engineer with 5 years experience in Python, FastAPI, and PyTorch."
    pdf_bytes = create_synthetic_pdf(sample_text)
    
    result = DocumentParserService.parse_document(pdf_bytes, "john_doe_resume.pdf")
    
    assert result.success is True
    assert "John Doe" in result.cleaned_text
    assert "Senior AI Engineer" in result.cleaned_text
    assert result.metadata.page_count == 1
    assert result.metadata.word_count > 10
    assert len(result.metadata.sha256_hash) == 64

def test_docx_extraction_success():
    paragraphs = [
        "Jane Smith",
        "Machine Learning Specialist with expertise in LLMs, LangGraph, and PostgreSQL."
    ]
    table = [["Education", "B.Tech Computer Science"], ["Year", "2024"]]
    docx_bytes = create_synthetic_docx(paragraphs, table)
    
    result = DocumentParserService.parse_document(docx_bytes, "jane_resume.docx")
    
    assert result.success is True
    assert "Jane Smith" in result.cleaned_text
    assert "B.Tech Computer Science" in result.cleaned_text
    assert result.metadata.file_extension == ".docx"
    assert result.metadata.word_count > 5

def test_magic_bytes_validation_failure():
    fake_content = b"This is just raw text, not a valid PDF header"
    with pytest.raises(ValueError, match="File magic bytes mismatch"):
        DocumentParserService.parse_document(fake_content, "fake_resume.pdf")

def test_unsupported_file_extension():
    fake_content = b"%PDF-1.4 dummy"
    with pytest.raises(ValueError, match="Unsupported file format"):
        DocumentParserService.parse_document(fake_content, "resume.txt")

def test_clean_text_normalization():
    dirty = "Line 1\x00\x05\r\n\r\n\r\nLine 2     with   spaces"
    cleaned = DocumentParserService.clean_text(dirty)
    assert "\x00" not in cleaned
    assert "\r" not in cleaned
    assert "     " not in cleaned
    assert "Line 1\n\nLine 2 with spaces" == cleaned
