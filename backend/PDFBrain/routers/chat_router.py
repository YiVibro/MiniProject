import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import PDFDocument, ChatMessage
from schemas import ChatRequest, ChatResponse, ChatHistoryResponse, ContentRequest, ContentResponse
from services.gemini_service import gemini_service
from services.pdf_processor import pdf_processor

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Ask a question about a PDF document"""
    try:
        # Get the document
        document = db.query(PDFDocument).filter(PDFDocument.id == request.document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not document or not document.extracted_text:
            raise HTTPException(status_code=422, detail="No text content available for this document")
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get recent chat history for context
        chat_history = db.query(ChatMessage).filter(
            ChatMessage.document_id == request.document_id,
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp.desc()).limit(5).all()
        
        # Convert to list of dicts for the AI service
        history_dicts = [
            {
                "user_message": msg.user_message,
                "ai_response": msg.ai_response
            }
            for msg in reversed(chat_history)  # Reverse to get chronological order
        ]
        
        # Get AI response
        truncated_content = pdf_processor.truncate_text_for_ai(str(document.extracted_text))
        ai_response = await gemini_service.answer_question(
            question=request.message,
            context=truncated_content,
            chat_history=history_dicts
        )
        
        # Save chat message
        chat_message = ChatMessage(
            document_id=request.document_id,
            session_id=session_id,
            user_message=request.message,
            ai_response=ai_response
        )
        
        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)
        
        logger.info(f"Answered question for document {request.document_id}, session {session_id}")
        
        return ChatResponse(
            success=True,
            response=ai_response,
            session_id=session_id,
            document_id=request.document_id,
            timestamp=chat_message.timestamp or datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")

@router.get("/history/{document_id}/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    document_id: int,
    session_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get chat history for a specific document and session"""
    
    # Verify document exists
    document = db.query(PDFDocument).filter(PDFDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get chat messages
    messages = db.query(ChatMessage).filter(
        ChatMessage.document_id == document_id,
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.timestamp.asc()).offset(skip).limit(limit).all()
    
    # Count total messages
    total_count = db.query(ChatMessage).filter(
        ChatMessage.document_id == document_id,
        ChatMessage.session_id == session_id
    ).count()
    
    # Format messages
    formatted_messages = [
        {
            "id": msg.id,
            "user_message": msg.user_message,
            "ai_response": msg.ai_response,
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in messages
    ]
    
    return ChatHistoryResponse(
        messages=formatted_messages,
        total_count=total_count
    )

@router.get("/sessions/{document_id}")
async def get_chat_sessions(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get all chat sessions for a document"""
    
    # Verify document exists
    document = db.query(PDFDocument).filter(PDFDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get distinct session IDs with message counts
    from sqlalchemy import func
    sessions = db.query(
        ChatMessage.session_id,
        func.count(ChatMessage.id).label('message_count'),
        func.max(ChatMessage.timestamp).label('last_activity')
    ).filter(
        ChatMessage.document_id == document_id
    ).group_by(ChatMessage.session_id).all()
    
    return {
        "document_id": document_id,
        "sessions": [
            {
                "session_id": session.session_id,
                "message_count": session.message_count,
                "last_activity": session.last_activity.isoformat()
            }
            for session in sessions
        ]
    }

@router.post("/manipulate", response_model=ContentResponse)
async def manipulate_content(
    request: ContentRequest,
    db: Session = Depends(get_db)
):
    """Manipulate document content (summarize, explain, restructure)"""
    try:
        # Get the document
        document = db.query(PDFDocument).filter(PDFDocument.id == request.document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not document or not document.extracted_text:
            raise HTTPException(status_code=422, detail="No text content available for this document")
        
        # Truncate content for AI processing
        truncated_content = pdf_processor.truncate_text_for_ai(str(document.extracted_text))
        
        # Process content
        result = await gemini_service.manipulate_content(
            text=truncated_content,
            operation=request.operation,
            custom_prompt=request.custom_prompt
        )
        
        logger.info(f"Content manipulation '{request.operation}' completed for document {request.document_id}")
        
        return ContentResponse(
            success=True,
            result=result,
            operation=request.operation
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in content manipulation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process content: {str(e)}")

@router.delete("/sessions/{document_id}/{session_id}")
async def delete_chat_session(
    document_id: int,
    session_id: str,
    db: Session = Depends(get_db)
):
    """Delete all messages in a chat session"""
    
    # Verify document exists
    document = db.query(PDFDocument).filter(PDFDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete messages
    deleted_count = db.query(ChatMessage).filter(
        ChatMessage.document_id == document_id,
        ChatMessage.session_id == session_id
    ).delete()
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Deleted {deleted_count} messages from session {session_id}"
    }
