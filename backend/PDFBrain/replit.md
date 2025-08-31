# PDF Knowledge Bot

## Overview

PDF Knowledge Bot is an AI-powered web application that allows users to upload PDF documents and interact with them through natural language. The system extracts text from PDFs, generates summaries, enables Q&A conversations, and creates interactive quizzes based on the document content. Built with FastAPI backend and vanilla JavaScript frontend, it leverages Google's Gemini AI for intelligent document processing and conversation capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: FastAPI with async/await support for high-performance API endpoints
- **Database**: SQLAlchemy ORM with configurable database support (SQLite default, PostgreSQL ready)
- **API Structure**: Modular router-based architecture with separate endpoints for PDF processing, chat functionality, and quiz generation
- **Service Layer**: Separated business logic into dedicated services (GeminiService, PDFProcessor, QuizGenerator)
- **Configuration**: Environment-based configuration management with validation

### Frontend Architecture
- **Technology Stack**: Vanilla JavaScript with Bootstrap 5 for responsive UI
- **Architecture Pattern**: Single-page application with tab-based navigation
- **State Management**: Class-based JavaScript architecture with centralized state handling
- **UI Components**: Modular component structure for upload, document management, chat, and quiz interfaces

### Data Storage Design
- **Document Storage**: File system storage for uploaded PDFs with UUID-based naming
- **Database Schema**: Relational design with four main entities:
  - PDFDocument: Stores document metadata and extracted text
  - ChatMessage: Maintains conversation history with session tracking
  - Quiz: Manages quiz metadata and question relationships
  - QuizQuestion: Stores individual quiz questions with multiple choice support

### AI Integration Architecture
- **Primary AI Service**: Google Gemini API for text processing and generation
- **Processing Pipeline**: Text extraction → Summary generation → Conversational AI responses
- **Content Limits**: Configurable text truncation for AI processing efficiency
- **Question Types**: Support for multiple choice, true/false, and fill-in-the-blank questions

### File Processing System
- **PDF Processing**: Dual-library approach using PyPDF2 and pdfplumber for robust text extraction
- **Upload Validation**: File type, size, and content validation with configurable limits
- **Storage Management**: Organized file storage with cleanup capabilities
- **Text Processing**: Content validation and AI-optimized text preparation

## External Dependencies

### AI Services
- **Google Gemini API**: Primary AI service for document summarization, question answering, and quiz generation
- **Model Selection**: Uses gemini-2.5-flash for standard operations and gemini-2.5-pro for complex tasks

### Database Systems
- **SQLAlchemy**: Database ORM with support for multiple database backends
- **Default Database**: SQLite for development with PostgreSQL production readiness

### PDF Processing Libraries
- **PyPDF2**: Primary PDF text extraction library
- **pdfplumber**: Secondary extraction library for enhanced text processing capabilities

### Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive design and UI components
- **Font Awesome**: Icon library for enhanced user interface elements

### Python Core Dependencies
- **FastAPI**: Modern web framework with automatic API documentation
- **Uvicorn**: ASGI server for running the FastAPI application
- **Pydantic**: Data validation and serialization using Python type hints