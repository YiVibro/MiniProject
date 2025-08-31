import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from models import Quiz, QuizQuestion, PDFDocument
from schemas import QuizGenerationRequest, QuestionType
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

class QuizGeneratorService:
    def __init__(self):
        pass
    
    async def generate_quiz(self, request: QuizGenerationRequest, db: Session) -> Quiz:
        """Generate a complete quiz from PDF content"""
        
        # Get the PDF document
        document = db.query(PDFDocument).filter(PDFDocument.id == request.document_id).first()
        if not document:
            raise ValueError("PDF document not found")
        
        if not document or not document.extracted_text:
            raise ValueError("No text content available for quiz generation")
        
        # Generate questions using Gemini
        try:
            question_types_str = [qt.value for qt in request.question_types]
            questions_data = await gemini_service.generate_quiz_questions(
                text=str(document.extracted_text),
                num_questions=request.num_questions,
                question_types=question_types_str,
                difficulty=request.difficulty
            )
            
            if not questions_data:
                raise ValueError("Failed to generate quiz questions")
            
            # Create quiz record
            quiz_title = f"Quiz: {document.original_filename}"
            quiz_description = f"Generated quiz from {document.original_filename} with {len(questions_data)} questions"
            
            quiz = Quiz(
                document_id=request.document_id,
                title=quiz_title,
                description=quiz_description,
                total_questions=len(questions_data)
            )
            
            db.add(quiz)
            db.flush()  # Get quiz ID
            
            # Create question records
            for i, q_data in enumerate(questions_data):
                question = QuizQuestion(
                    quiz_id=quiz.id,
                    question_type=q_data.get("question_type", "mcq"),
                    question_text=q_data.get("question_text", ""),
                    correct_answer=q_data.get("correct_answer", ""),
                    options=q_data.get("options", []) if q_data.get("question_type") == "mcq" else None,
                    explanation=q_data.get("explanation", ""),
                    order_index=i + 1
                )
                db.add(question)
            
            db.commit()
            db.refresh(quiz)
            
            logger.info(f"Generated quiz with {len(questions_data)} questions for document {request.document_id}")
            return quiz
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error generating quiz: {str(e)}")
            raise Exception(f"Failed to generate quiz: {str(e)}")
    
    def get_quiz_by_id(self, quiz_id: int, db: Session) -> Quiz:
        """Get quiz with all questions"""
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            raise ValueError("Quiz not found")
        return quiz
    
    def get_quizzes_by_document(self, document_id: int, db: Session) -> List[Quiz]:
        """Get all quizzes for a document"""
        return db.query(Quiz).filter(Quiz.document_id == document_id).all()
    
    def delete_quiz(self, quiz_id: int, db: Session) -> bool:
        """Delete a quiz and all its questions"""
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            return False
        
        db.delete(quiz)
        db.commit()
        return True
    
    def validate_quiz_request(self, request: QuizGenerationRequest) -> List[str]:
        """Validate quiz generation request and return list of errors"""
        errors = []
        
        if request.num_questions < 1 or request.num_questions > 20:
            errors.append("Number of questions must be between 1 and 20")
        
        if not request.question_types:
            errors.append("At least one question type must be specified")
        
        valid_question_types = {qt.value for qt in QuestionType}
        for qt in request.question_types:
            if qt.value not in valid_question_types:
                errors.append(f"Invalid question type: {qt.value}")
        
        if request.difficulty not in ["easy", "medium", "hard"]:
            errors.append("Difficulty must be 'easy', 'medium', or 'hard'")
        
        return errors

# Global instance
quiz_generator = QuizGeneratorService()
