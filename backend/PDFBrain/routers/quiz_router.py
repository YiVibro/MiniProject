import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import PDFDocument, Quiz
from schemas import QuizGenerationRequest, QuizGenerationResponse, QuizResponse
from services.quiz_generator import quiz_generator

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate", response_model=QuizGenerationResponse)
async def generate_quiz(
    request: QuizGenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate a quiz from PDF content"""
    try:
        # Validate request
        errors = quiz_generator.validate_quiz_request(request)
        if errors:
            raise HTTPException(status_code=422, detail=f"Validation errors: {', '.join(errors)}")
        
        # Verify document exists
        document = db.query(PDFDocument).filter(PDFDocument.id == request.document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Generate quiz
        quiz = await quiz_generator.generate_quiz(request, db)
        
        logger.info(f"Generated quiz {quiz.id} for document {request.document_id}")
        
        return QuizGenerationResponse(
            success=True,
            message=f"Quiz generated successfully with {quiz.total_questions} questions",
            quiz=QuizResponse.from_orm(quiz)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@router.get("/quiz/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific quiz with all questions"""
    try:
        quiz = quiz_generator.get_quiz_by_id(quiz_id, db)
        return QuizResponse.from_orm(quiz)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve quiz: {str(e)}")

@router.get("/document/{document_id}/quizzes", response_model=List[QuizResponse])
async def get_document_quizzes(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get all quizzes for a specific document"""
    
    # Verify document exists
    document = db.query(PDFDocument).filter(PDFDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        quizzes = quiz_generator.get_quizzes_by_document(document_id, db)
        return [QuizResponse.from_orm(quiz) for quiz in quizzes]
        
    except Exception as e:
        logger.error(f"Error retrieving quizzes for document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve quizzes: {str(e)}")

@router.delete("/quiz/{quiz_id}")
async def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db)
):
    """Delete a quiz and all its questions"""
    try:
        success = quiz_generator.delete_quiz(quiz_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        return {
            "success": True,
            "message": f"Quiz {quiz_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting quiz {quiz_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete quiz: {str(e)}")

@router.get("/")
async def list_all_quizzes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all quizzes with basic information"""
    
    quizzes = db.query(Quiz).offset(skip).limit(limit).all()
    
    return {
        "quizzes": [
            {
                "id": quiz.id,
                "title": quiz.title,
                "document_id": quiz.document_id,
                "total_questions": quiz.total_questions,
                "created_at": quiz.created_at.isoformat(),
                "document_filename": quiz.document.original_filename if quiz.document else "Unknown"
            }
            for quiz in quizzes
        ],
        "total_count": db.query(Quiz).count()
    }

@router.get("/quiz/{quiz_id}/questions")
async def get_quiz_questions_only(
    quiz_id: int,
    db: Session = Depends(get_db)
):
    """Get only the questions for a quiz (useful for taking the quiz)"""
    try:
        quiz = quiz_generator.get_quiz_by_id(quiz_id, db)
        
        questions = [
            {
                "id": q.id,
                "question_type": q.question_type,
                "question_text": q.question_text,
                "options": q.options if q.question_type == "mcq" else None,
                "order_index": q.order_index
            }
            for q in sorted(quiz.questions, key=lambda x: x.order_index)
        ]
        
        return {
            "quiz_id": quiz.id,
            "title": quiz.title,
            "questions": questions
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving quiz questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve quiz questions: {str(e)}")
