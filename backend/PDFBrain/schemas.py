from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class QuestionType(str, Enum):
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"

# PDF Document schemas
class PDFDocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    page_count: Optional[int]
    upload_time: datetime
    summary: Optional[str]
    
    class Config:
        from_attributes = True

class PDFUploadResponse(BaseModel):
    success: bool
    message: str
    document: Optional[PDFDocumentResponse] = None

# Chat schemas
class ChatRequest(BaseModel):
    document_id: int
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    success: bool
    response: str
    session_id: str
    document_id: int
    timestamp: datetime

class ChatHistoryResponse(BaseModel):
    messages: List[dict]
    total_count: int

# Content manipulation schemas
class ContentRequest(BaseModel):
    document_id: int
    operation: str = Field(..., description="summarize, explain, or restructure")
    custom_prompt: Optional[str] = None

class ContentResponse(BaseModel):
    success: bool
    result: str
    operation: str

# Quiz schemas
class QuizQuestionResponse(BaseModel):
    id: int
    question_type: QuestionType
    question_text: str
    correct_answer: str
    options: Optional[List[str]] = None
    explanation: Optional[str] = None
    order_index: int
    
    class Config:
        from_attributes = True

class QuizResponse(BaseModel):
    id: int
    document_id: int
    title: str
    description: Optional[str]
    created_at: datetime
    total_questions: int
    questions: List[QuizQuestionResponse] = []
    
    class Config:
        from_attributes = True

class QuizGenerationRequest(BaseModel):
    document_id: int
    num_questions: int = Field(default=5, ge=1, le=20)
    question_types: List[QuestionType] = Field(default=[QuestionType.MCQ])
    difficulty: str = Field(default="medium", description="easy, medium, or hard")
    focus_topics: Optional[List[str]] = None

class QuizGenerationResponse(BaseModel):
    success: bool
    message: str
    quiz: Optional[QuizResponse] = None

# General response schemas
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[str] = None

class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
