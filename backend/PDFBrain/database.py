from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import asyncio
from contextlib import asynccontextmanager

from config import settings

# Create engine - Updated for Supabase PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

async def init_db():
    """Initialize database tables"""
    from models import PDFDocument, ChatMessage, Quiz, QuizQuestion
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
