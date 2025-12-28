"""
PDF text extraction utility.
Extracts text content from PDF files, excluding all metadata.
"""
import fitz  # PyMuPDF
from typing import Optional


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text content from PDF bytes, excluding metadata.
    
    Args:
        pdf_bytes: PDF file content as bytes
        
    Returns:
        str: Extracted text content from the PDF
        
    Raises:
        ValueError: If the PDF cannot be processed or is invalid
        Exception: If there's an error reading the PDF
    """
    try:
        # Open PDF from bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Extract text from all pages
        text_parts = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text:
                text_parts.append(text)
        
        doc.close()
        
        # Join all pages with newlines
        extracted_text = "\n\n".join(text_parts)
        
        # Clean up the text (remove excessive whitespace but preserve structure)
        extracted_text = "\n".join(line.strip() for line in extracted_text.split("\n") if line.strip())
        
        if not extracted_text:
            raise ValueError("No text content found in PDF")
        
        return extracted_text
        
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {str(e)}")

