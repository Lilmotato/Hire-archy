# utils/file_reader.py

from io import BytesIO
import docx
import fitz  # PyMuPDF

async def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file."""
    text = ""
    pdf = fitz.open(stream=file_content, filetype="pdf")
    for page in pdf:
        text += page.get_text()
    return text.strip()

async def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file."""
    text = ""
    doc = docx.Document(BytesIO(file_content))
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text.strip()

async def extract_text(file_content: bytes, content_type: str) -> str:
    """Main text extractor based on MIME type."""
    if content_type == "application/pdf":
        return await extract_text_from_pdf(file_content)
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return await extract_text_from_docx(file_content)
    else:
        raise ValueError("Unsupported file type for extraction")
