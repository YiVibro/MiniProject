import os
import uuid
from typing import Tuple, Optional
import PyPDF2
import pdfplumber
from fastapi import UploadFile, HTTPException
import logging

from config import settings

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS
    
    async def save_uploaded_file(self, file: UploadFile) -> Tuple[str, str]:
        """Save uploaded PDF file and return filename and file path"""
        
        # Validate file extension
        if not file.filename or not any(file.filename.lower().endswith(ext) for ext in self.allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Supported formats: {', '.join(self.allowed_extensions)}"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > self.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {self.max_file_size / 1024 / 1024:.1f}MB"
            )
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename or "")[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # Save file
        try:
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            logger.info(f"File saved: {file_path}")
            return unique_filename, file_path
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save uploaded file")
    
    def extract_text_from_pdf(self, file_path: str) -> Tuple[str, int]:
        """Extract text from PDF file using multiple methods for better compatibility"""
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        text = ""
        page_count = 0
        
        # Try pdfplumber first (better for complex layouts)
        try:
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if text.strip():
                    logger.info(f"Successfully extracted text using pdfplumber: {len(text)} characters")
                    return text.strip(), page_count
                    
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {str(e)}")
        
        # Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if text.strip():
                    logger.info(f"Successfully extracted text using PyPDF2: {len(text)} characters")
                    return text.strip(), page_count
                    
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {str(e)}")
        
        # If both methods fail
        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from PDF. The file may be corrupted, password-protected, or contain only images."
            )
        
        return text.strip(), page_count
    
    def validate_extracted_text(self, text: str) -> bool:
        """Validate that extracted text is meaningful"""
        if len(text.strip()) < 50:
            return False
        
        # Check if text contains mostly readable characters
        readable_chars = sum(1 for c in text if c.isalnum() or c.isspace() or c in '.,!?;:')
        ratio = readable_chars / len(text) if text else 0
        
        return ratio > 0.7  # At least 70% readable characters
    
    def truncate_text_for_ai(self, text: str) -> str:
        """Truncate text to fit within AI model limits"""
        max_length = settings.MAX_CONTENT_LENGTH
        
        if len(text) <= max_length:
            return text
        
        # Try to truncate at sentence boundaries
        sentences = text[:max_length].split('.')
        if len(sentences) > 1:
            # Remove the last incomplete sentence
            truncated = '.'.join(sentences[:-1]) + '.'
            return truncated
        
        # If no sentence boundaries, truncate at word boundaries
        words = text[:max_length].split(' ')
        if len(words) > 1:
            truncated = ' '.join(words[:-1])
            return truncated
        
        # Last resort: hard truncate
        return text[:max_length]
    
    def cleanup_file(self, file_path: str) -> bool:
        """Remove uploaded file from filesystem"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
                return True
        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {str(e)}")
        return False

# Global instance
pdf_processor = PDFProcessor()
