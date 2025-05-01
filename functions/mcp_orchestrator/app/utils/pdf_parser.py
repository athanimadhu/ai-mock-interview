import io
import requests
from PyPDF2 import PdfReader
import re

def parse_pdf_from_url(url: str) -> str:
    """Download and parse a PDF file from a URL."""
    try:
        # Download the PDF
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Create a file-like object from the content
        pdf_file = io.BytesIO(response.content)
        
        # Parse the PDF
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        return text
    except Exception as e:
        raise Exception(f"Failed to parse PDF from URL: {str(e)}")

def parse_pdf_to_text(pdf_content: bytes) -> str:
    """Parse PDF content to text."""
    try:
        pdf_file = io.BytesIO(pdf_content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise Exception(f"Failed to parse PDF: {str(e)}")

def clean_resume_text(text: str) -> str:
    """Clean and normalize resume text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters
    text = re.sub(r'[^\w\s.,;:-]', '', text)
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text.strip() 