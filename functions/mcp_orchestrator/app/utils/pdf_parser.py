from PyPDF2 import PdfReader
from typing import Optional
import io

async def parse_pdf_to_text(file: bytes) -> str:
    """
    Parse a PDF file and extract its text content.
    
    Args:
        file (bytes): The PDF file in bytes
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        # Create a PDF reader object
        pdf_reader = PdfReader(io.BytesIO(file))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
            
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error parsing PDF: {str(e)}")

def clean_resume_text(text: str) -> str:
    """
    Clean and normalize resume text.
    
    Args:
        text (str): Raw text from PDF
        
    Returns:
        str: Cleaned and normalized text
    """
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Basic cleaning
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = text.replace("\t", " ")
    
    return text.strip() 