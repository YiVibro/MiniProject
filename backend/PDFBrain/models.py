from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON,
    BigInteger, SmallInteger, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String)
    description = Column(Text)

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
