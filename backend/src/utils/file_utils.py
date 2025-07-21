import os
from typing import Dict, Any

def get_file_summary(file: Dict[str, Any]) -> str:
    """
    Generates a concise summary of an uploaded file.
    """
    filename = file.get("filename", "Unknown file")
    content = file.get("content", b"")
    
    # In a real system, this would use a proper content extraction
    # library like agentic-doc to get the text from PDFs, DOCX, etc.
    # For now, we'll just use the first 200 characters of the content.
    
    try:
        # Attempt to decode as text
        text_content = content.decode('utf-8', errors='ignore')
        summary = text_content[:200]
    except (UnicodeDecodeError, AttributeError):
        # Handle binary files
        summary = f"[Binary file, {len(content)} bytes]"

    return f"File: {filename}, Summary: {summary}..."
