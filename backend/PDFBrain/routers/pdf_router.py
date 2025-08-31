import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import PDFDocument
from schemas import PDFUploadResponse, PDFDocumentResponse, SuccessResponse
from services.pdf_processor import pdf_processor
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a PDF file"""
    try:
        # Save uploaded file
        filename, file_path = await pdf_processor.save_uploaded_file(file)
        
        # Extract text from PDF
        extracted_text, page_count = pdf_processor.extract_text_from_pdf(file_path)
        
        # Validate extracted text
        if not pdf_processor.validate_extracted_text(extracted_text):
            pdf_processor.cleanup_file(file_path)
            raise HTTPException(
                status_code=422,
                detail="Extracted text appears to be invalid or insufficient for processing"
            )
        
        # Generate summary
        try:
            truncated_text = pdf_processor.truncate_text_for_ai(extracted_text)
            summary = await gemini_service.generate_summary(truncated_text)
        except Exception as e:
            logger.warning(f"Failed to generate summary: {str(e)}")
            summary = None
        
        # Create database record
        document = PDFDocument(
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            extracted_text=extracted_text,
            summary=summary,
            file_size=len(extracted_text.encode('utf-8')),
            page_count=page_count
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        logger.info(f"Successfully processed PDF: {file.filename} (ID: {document.id})")
        
        return PDFUploadResponse(
            success=True,
            message="PDF uploaded and processed successfully",
            document=PDFDocumentResponse.from_orm(document)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

@router.get("/documents", response_model=List[PDFDocumentResponse])
async def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get list of uploaded PDF documents"""
    documents = db.query(PDFDocument).offset(skip).limit(limit).all()
    return [PDFDocumentResponse.from_orm(doc) for doc in documents]

@router.get("/documents/{document_id}", response_model=PDFDocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get specific PDF document details"""
    document = db.query(PDFDocument).filter(PDFDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return PDFDocumentResponse.from_orm(document)

@router.delete("/documents/{document_id}", response_model=SuccessResponse)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete a PDF document and its file"""
    document = db.query(PDFDocument).filter(PDFDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Clean up file
    pdf_processor.cleanup_file(str(document.file_path))
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    return SuccessResponse(
        message=f"Document '{document.original_filename}' deleted successfully"
    )

@router.get("/documents/{document_id}/content")
async def get_document_content(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get the extracted text content of a document"""
    document = db.query(PDFDocument).filter(PDFDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "document_id": document.id,
        "filename": document.original_filename,
        "content": document.extracted_text,
        "summary": document.summary
    }
