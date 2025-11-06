
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import asyncio

from new_agent.dynamic_lesson_generator import create_dynamic_curriculum
from new_agent.models import Lesson

router = APIRouter()

class CourseRequest(BaseModel):
    subject: str
    level: str
    duration_weeks: int

@router.post("/generate-course", response_model=List[Lesson])
async def generate_course(request: CourseRequest):
    """
    Generates a dynamic course curriculum based on user input.
    """
    try:
        curriculum = await create_dynamic_curriculum(
            subject=request.subject,
            level=request.level,
            duration_weeks=request.duration_weeks
        )
        return curriculum
    except Exception as e:
        # Log the exception for debugging
        print(f"Error generating course: {e}")
        # Re-raise or return a custom error response
        raise

