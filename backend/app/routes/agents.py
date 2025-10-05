from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import asyncio
import sys
from pathlib import Path

# Add new_agent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "new_agent"))

from tutoring_system import MultiAgentTutoringSystem, SystemConfig
from dynamic_learning_planner import DynamicLearningPlanner
from interactive_course_creator import InteractiveCourseCreator
from models import UserProfile, UserProgress, Lesson

router = APIRouter(prefix="/api/agents", tags=["agents"])

# Initialize the tutoring system
config = SystemConfig(
    llm_provider="google",
    llm_api_key="AIzaSyCKe9J2cwEzVnsp-MNU-xJxf255_hWAVzE",
    llm_model="gemini-pro",
    enable_analytics=True,
    enable_gap_analysis=True,
    enable_learning_curves=True,
    enable_mdp_recommendations=True
)

tutoring_system = MultiAgentTutoringSystem(config)
learning_planner = DynamicLearningPlanner()
course_creator = InteractiveCourseCreator()

# Request/Response Models
class CreateLearningPlanRequest(BaseModel):
    user_id: str
    user_request: str
    preferences: Optional[Dict[str, Any]] = None

class LearningPlanResponse(BaseModel):
    path_id: str
    requirements: Dict[str, Any]
    curriculum: List[Dict[str, Any]]
    timeline: str
    goals: List[str]

class CreateCourseRequest(BaseModel):
    user_id: str
    subject: str
    topic: str
    weeks: int
    focus: str
    assessments: bool
    user_profile: Dict[str, Any]

class CourseResponse(BaseModel):
    course_id: str
    curriculum: List[Dict[str, Any]]
    learning_path: Dict[str, Any]
    requirements: Dict[str, Any]

class ProgressTrackingRequest(BaseModel):
    user_id: str
    activity: str
    data: Dict[str, Any]

class ProgressResponse(BaseModel):
    progress: Dict[str, Any]
    plan_status: Dict[str, Any]
    recommendations: List[str]

class LearningSessionRequest(BaseModel):
    user_id: str
    lesson_id: str
    session_preferences: Optional[Dict[str, Any]] = None

class LearningSessionResponse(BaseModel):
    session_id: str
    lesson: Dict[str, Any]
    adaptive_content: Dict[str, Any]
    recommendations: List[str]

# Endpoints
@router.post("/create-learning-plan", response_model=LearningPlanResponse)
async def create_learning_plan(request: CreateLearningPlanRequest):
    """Create a personalized learning plan based on user request"""
    try:
        plan = await learning_planner.create_learning_plan(
            request.user_id, 
            request.user_request
        )
        
        return LearningPlanResponse(
            path_id=plan["path_id"],
            requirements=plan["requirements"],
            curriculum=plan["curriculum"],
            timeline=plan["timeline"],
            goals=plan["goals"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-course", response_model=CourseResponse)
async def create_course(request: CreateCourseRequest):
    """Create a dynamic course based on user requirements"""
    try:
        # Create user profile from request
        user_profile = UserProfile(
            user_id=request.user_id,
            name=request.user_profile.get("name", "Learner"),
            email=request.user_profile.get("email", f"{request.user_id}@example.com"),
            learning_style=request.user_profile.get("learning_style", "balanced"),
            preferred_difficulty=request.user_profile.get("preferred_difficulty", "intermediate"),
            available_time=request.user_profile.get("available_time", 60),
            learning_goals=request.user_profile.get("learning_goals", ["Master the subject"]),
            interests=request.user_profile.get("interests", [])
        )
        
        # Initialize course creator if needed
        if not course_creator.system:
            await course_creator.initialize_system()
        
        # Create course
        curriculum = await course_creator.system.create_dynamic_curriculum(
            subject=request.subject,
            level=user_profile.preferred_difficulty,
            duration_weeks=request.weeks,
            user_profile=user_profile
        )
        
        # Create learning path
        path_id = await course_creator.system.create_personalized_learning_path(
            user_id=request.user_id,
            user_request=f"Learn {request.subject} focusing on {request.topic} with {request.focus} approach",
            user_profile=user_profile
        )
        
        # Get learning path details
        learning_path = course_creator.system.learning_paths.get(path_id, {})
        
        return CourseResponse(
            course_id=path_id,
            curriculum=[{
                "id": lesson.lesson_id,
                "title": lesson.title,
                "difficulty": lesson.difficulty,
                "duration": lesson.duration,
                "content": lesson.content[:200] + "..." if len(lesson.content) > 200 else lesson.content,
                "learning_objectives": lesson.learning_objectives,
                "prerequisites": lesson.prerequisites
            } for lesson in curriculum],
            learning_path={
                "path_id": path_id,
                "title": learning_path.get("title", f"{request.subject} Course"),
                "description": learning_path.get("description", ""),
                "estimated_duration": learning_path.get("estimated_duration", 0),
                "difficulty_progression": learning_path.get("difficulty_progression", []),
                "milestones": learning_path.get("milestones", [])
            },
            requirements={
                "subject": request.subject,
                "topic": request.topic,
                "weeks": request.weeks,
                "focus": request.focus,
                "assessments": request.assessments
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track-progress", response_model=ProgressResponse)
async def track_progress(request: ProgressTrackingRequest):
    """Track user progress and get recommendations"""
    try:
        result = await learning_planner.track_progress(
            request.user_id,
            request.activity,
            request.data
        )
        
        return ProgressResponse(
            progress=result["progress"],
            plan_status=result["plan_status"],
            recommendations=result["recommendations"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-learning-session", response_model=LearningSessionResponse)
async def start_learning_session(request: LearningSessionRequest):
    """Start a learning session with adaptive content"""
    try:
        session_id = await tutoring_system.start_learning_session(
            request.user_id,
            request.lesson_id,
            request.session_preferences
        )
        
        # Get lesson details
        lesson = tutoring_system.lessons.get(request.lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        # Get adaptive content
        adaptive_content = await tutoring_system._create_adaptive_content(
            lesson,
            "medium",  # Default difficulty
            request.session_preferences or {}
        )
        
        return LearningSessionResponse(
            session_id=session_id,
            lesson={
                "id": lesson.lesson_id,
                "title": lesson.title,
                "content": lesson.content,
                "difficulty": lesson.difficulty,
                "duration": lesson.duration,
                "learning_objectives": lesson.learning_objectives,
                "prerequisites": lesson.prerequisites
            },
            adaptive_content=adaptive_content,
            recommendations=[]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning-plan-status/{user_id}")
async def get_learning_plan_status(user_id: str):
    """Get current status of user's learning plan"""
    try:
        status = await learning_planner.get_learning_plan_status(user_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-interaction")
async def process_user_interaction(
    session_id: str,
    interaction_type: str,
    interaction_data: Dict[str, Any]
):
    """Process user interaction during learning session"""
    try:
        result = await tutoring_system.process_user_interaction(
            session_id,
            interaction_type,
            interaction_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/end-learning-session/{session_id}")
async def end_learning_session(session_id: str):
    """End a learning session and get summary"""
    try:
        summary = await tutoring_system.end_learning_session(session_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-status")
async def get_system_status():
    """Get system status and metrics"""
    try:
        status = tutoring_system.get_system_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-subjects")
async def get_available_subjects():
    """Get list of available subjects for course creation"""
    return {
        "subjects": [
            "Python Programming",
            "JavaScript",
            "Machine Learning",
            "Web Development",
            "Data Science",
            "Computer Science",
            "Mathematics",
            "Physics",
            "Chemistry",
            "Biology",
            "History",
            "Literature",
            "Psychology",
            "Economics",
            "Philosophy"
        ]
    }

@router.get("/learning-styles")
async def get_learning_styles():
    """Get available learning styles"""
    return {
        "styles": [
            {"value": "visual", "label": "Visual", "description": "Learn through diagrams, charts, and visual aids"},
            {"value": "auditory", "label": "Auditory", "description": "Learn through listening and verbal explanations"},
            {"value": "kinesthetic", "label": "Kinesthetic", "description": "Learn through hands-on activities and movement"},
            {"value": "analytical", "label": "Analytical", "description": "Learn through detailed analysis and logical structure"},
            {"value": "practical", "label": "Practical", "description": "Learn through real-world applications"},
            {"value": "balanced", "label": "Balanced", "description": "Mix of all learning styles"}
        ]
    }

@router.get("/difficulty-levels")
async def get_difficulty_levels():
    """Get available difficulty levels"""
    return {
        "levels": [
            {"value": "beginner", "label": "Beginner", "description": "New to the subject"},
            {"value": "intermediate", "label": "Intermediate", "description": "Some experience"},
            {"value": "advanced", "label": "Advanced", "description": "Experienced learner"}
        ]
    }
