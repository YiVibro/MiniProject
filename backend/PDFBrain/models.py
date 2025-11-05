from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON,
    BigInteger, SmallInteger, Numeric, Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String)
    description = Column(Text)

class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user_id = Column(Integer, ForeignKey("user_profiles.id"))

    user = relationship("UserProfile", back_populates="learning_paths")


class SessionData(Base):
    __tablename__ = "session_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(BigInteger, ForeignKey("lessons.id"), nullable=True)
    session_token = Column(String(255), unique=True, nullable=False)
    data = Column(JSON, nullable=True)  # stores chat context, answers, metadata, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="sessions")
    lesson = relationship("Lesson", backref="sessions")


class ConceptMastery(Base):
    __tablename__ = "concept_mastery"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    concept_name = Column(String(255), nullable=False)
    mastery_level = Column(Float, default=0.0)  # e.g., 0.0 - 1.0
    last_assessed = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="concept_mastery")


class PerformanceMetrics(Base):
    __tablename__ = "performance_metrics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(BigInteger, ForeignKey("lessons.id"), nullable=True)
    average_score = Column(Float, default=0.0)
    quizzes_attempted = Column(Integer, default=0)
    total_correct = Column(Integer, default=0)
    total_incorrect = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="performance_metrics")
    lesson = relationship("Lesson", backref="performance_metrics")

class MDPRecommendation:
    def __init__(self, recommendation_id=None, strategy=None, confidence=None):
        self.recommendation_id = recommendation_id
        self.strategy = strategy
        self.confidence = confidence


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    preferences = Column(Text, nullable=True)
    learning_paths = relationship("LearningPath", back_populates="user")

class GapAnalysisResult(Base):
    __tablename__ = "gap_analysis_results"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    concept_name = Column(String(255), nullable=False)
    knowledge_gap = Column(Float, default=0.0)  # 0.0 means none, 1.0 means major gap
    recommended_resources = Column(JSON, nullable=True)  # e.g., {"videos": [...], "articles": [...]}
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="gap_analysis_results")
class LearningCurveData(Base):
    __tablename__ = "learning_curve_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    concept_name = Column(String(255), nullable=False)
    attempt_number = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    improvement_rate = Column(Float, default=0.0)  # e.g. percent change from previous attempt

    user = relationship("User", backref="learning_curve_data")

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    duration = Column(Integer)
    difficulty = Column(String)
    learning_objectives = Column(JSON)
    prerequisites = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('pdf_documents.id'), nullable=False)
    session_id = Column(String, nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    document = relationship("PDFDocument")

class PDFChunk(Base):
    __tablename__ = 'pdf_chunks'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    upload_id = Column(BigInteger, ForeignKey('uploads.id'), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Text)  # Placeholder for USER-DEFINED
    created_at = Column(DateTime(timezone=True), default=func.now())
    upload = relationship("Upload")

class PDFDocument(Base):
    __tablename__ = 'pdf_documents'
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    extracted_text = Column(Text)
    summary = Column(Text)
    upload_time = Column(DateTime, default=func.now())
    file_size = Column(Integer, nullable=False)
    page_count = Column(Integer)

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    embedding = Column(Text) # Placeholder for USER-DEFINED

class QAHistory(Base):
    __tablename__ = 'qa_history'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    upload_id = Column(BigInteger, ForeignKey('uploads.id'))
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    user = relationship("User")
    upload = relationship("Upload")

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    lesson_id = Column(BigInteger, ForeignKey("lessons.id"), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # list of possible answers
    correct_answer = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship (optional)
    lesson = relationship("Lesson", backref="assessments")

class TestResult(Base):
    __tablename__ = "test_results"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    assessment_id = Column(BigInteger, ForeignKey("assessments.id"), nullable=False)
    score = Column(Float, nullable=False)
    total_score = Column(Float, nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships (optional)
    user = relationship("User", backref="test_results")
    assessment = relationship("Assessment", backref="test_results")

class QuestionAttempt(Base):
    __tablename__ = 'question_attempts'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    quiz_id = Column(BigInteger, ForeignKey('quizzes.id'), nullable=False)
    question_id = Column(BigInteger, ForeignKey('quiz_questions.id'), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    answered_at = Column(DateTime(timezone=True), default=func.now())
    user_answer = Column(Text)
    user = relationship("User")
    quiz = relationship("Quiz")
    question = relationship("QuizQuestion")

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)
    topic_tag = Column(String)
    correct_answer = Column(Text, nullable=False)
    options = Column(Text)
    points = Column(Integer)
    quiz = relationship("Quiz")

class QuizProgress(Base):
    __tablename__ = 'quiz_progress'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    quiz_id = Column(BigInteger, ForeignKey('quizzes.id'), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    completed_at = Column(DateTime(timezone=True), default=func.now())
    percentage_score = Column(Numeric)
    time_spent_minutes = Column(Integer)
    user = relationship("User")
    quiz = relationship("Quiz")

class QuizQuestion(Base):
    __tablename__ = 'quiz_questions'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    quiz_id = Column(BigInteger, ForeignKey('quizzes.id'), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON)
    correct_answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    question_type = Column(String)
    explanation = Column(Text)
    order_index = Column(Integer)
    quiz = relationship("Quiz")

class Quiz(Base):
    __tablename__ = 'quizzes'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    category_id = Column(BigInteger, ForeignKey('categories.id'))
    title = Column(String)
    total_questions = Column(SmallInteger)
    document_id = Column(Integer, ForeignKey('pdf_documents.id'))
    description = Column(Text)
    category = relationship("Category")
    document = relationship("PDFDocument")

class Upload(Base):
    __tablename__ = 'uploads'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(BigInteger, ForeignKey('users.id'))
    file_name = Column(String)
    file_url = Column(Text)
    user = relationship("User")

class UserProgress(Base):
    __tablename__ = 'user_progress'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    category_id = Column(BigInteger, ForeignKey('categories.id'))
    total_quizzes = Column(Integer, default=0)
    completed_quizzes = Column(Integer, default=0)
    average_score = Column(Numeric, default=0.00)
    progress_percent = Column(Numeric, default=0.00)
    last_updated = Column(DateTime(timezone=True), default=func.now())
    course_name = Column(String)
    user = relationship("User")
    category = relationship("Category")

class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String, default='')
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    profile_pic = Column(Text, default='')

    sessions = relationship("SessionData", back_populates="user")
