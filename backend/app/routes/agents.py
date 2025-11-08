from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import asyncio
import sys
from pathlib import Path
import os
from new_agent.tutoring_system import MultiAgentTutoringSystem, SystemConfig
from new_agent.dynamic_learning_planner import DynamicLearningPlanner
from new_agent.interactive_course_creator import InteractiveCourseCreator
try:
    from new_agent.langgraph_course_creator import LangGraphCourseCreator
except Exception:  # pragma: no cover
    LangGraphCourseCreator = None  # type: ignore
from new_agent.models import UserProfile, UserProgress, Lesson

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
lg_course_creator = None
if LangGraphCourseCreator is not None:
    try:
        lg_course_creator = LangGraphCourseCreator(
            api_key=os.getenv("GOOGLE_API_KEY"),
            model="gemini-2.5-flash",
        )
    except Exception:
        lg_course_creator = None

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

class CreateAssessmentRequest(BaseModel):
    lesson_id: str
    difficulty: str = "medium"
    num_questions: int = 5
    question_types: List[str] = ["multiple_choice", "true_false", "short_answer"]

class AssessmentResponse(BaseModel):
    assessment_id: str
    questions: List[Dict[str, Any]]
    time_limit: int
    passing_score: float

class EvaluateAssessmentRequest(BaseModel):
    assessment_id: str
    user_answers: Dict[str, Any]  # question_id -> answer
    user_id: str

class EvaluateAssessmentResponse(BaseModel):
    score: float
    passed: bool
    gaps: List[Dict[str, Any]]
    remedial_content: Dict[str, Any]
    next_steps: List[str]

@router.post("/create-assessment", response_model=AssessmentResponse)
async def create_assessment(request: CreateAssessmentRequest):
    """Create an assessment for a lesson"""
    try:
        # This would integrate with assessment_system.py
        # For now, creating a mock assessment
        assessment_id = f"assessment_{request.lesson_id}_{datetime.now().timestamp()}"
        
        # Generate questions based on difficulty and lesson
        questions = await tutoring_system._generate_assessment_questions(
            request.lesson_id,
            request.difficulty,
            request.num_questions
        )
        
        return AssessmentResponse(
            assessment_id=assessment_id,
            questions=questions,
            time_limit=30,  # minutes
            passing_score=0.7
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate-assessment", response_model=EvaluateAssessmentResponse)
async def evaluate_assessment(request: EvaluateAssessmentRequest):
    """Evaluate assessment and provide gap analysis"""
    try:
        # This would integrate with gap_analysis.py and assessment_system.py
        score, passed = await tutoring_system._evaluate_assessment(
            request.assessment_id,
            request.user_answers
        )
        
        # Get gap analysis
        gaps = await tutoring_system._analyze_learning_gaps(
            request.user_id,
            request.assessment_id,
            request.user_answers
        )
        
        # Get remedial content
        remedial_content = await tutoring_system._generate_remedial_content(gaps)
        
        # Get next steps recommendations
        next_steps = await tutoring_system._get_next_steps_recommendations(
            request.user_id,
            score,
            gaps
        )
        
        return EvaluateAssessmentResponse(
            score=score,
            passed=passed,
            gaps=gaps,
            remedial_content=remedial_content,
            next_steps=next_steps
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
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
        
        # Try LangGraph-based generation first (no hardcoding)
        if lg_course_creator is not None:
            from uuid import uuid4
            goal = f"Learn {request.subject} focusing on {request.topic} with a {request.focus} approach."
            lg = await lg_course_creator.create_course(
                subject=request.subject,
                topic=request.topic,
                weeks=request.weeks,
                focus=request.focus,
                user_profile=user_profile.dict(),
                goal=goal,
            )
            path_id = str(uuid4())
            curriculum = lg.get("curriculum", [])
            learning_path = lg.get("learning_path", {})
            return CourseResponse(
                course_id=path_id,
                curriculum=curriculum,
                learning_path={
                    "path_id": path_id,
                    **learning_path,
                },
                requirements={
                    "subject": request.subject,
                    "topic": request.topic,
                    "weeks": request.weeks,
                    "focus": request.focus,
                    "assessments": request.assessments,
                },
            )

        # Fallback to existing interactive system
        if not course_creator.system:
            await course_creator.initialize_system()
        curriculum = await course_creator.system.create_dynamic_curriculum(
            subject=request.subject,
            level=user_profile.preferred_difficulty,
            duration_weeks=request.weeks,
            user_profile=user_profile
        )
        path_id = await course_creator.system.create_personalized_learning_path(
            user_id=request.user_id,
            user_request=f"Learn {request.subject} focusing on {request.topic} with {request.focus} approach",
            user_profile=user_profile
        )
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
        # Ensure lesson exists before starting session
        lesson = tutoring_system.lessons.get(request.lesson_id)
        if not lesson:
            lesson = Lesson(
                lesson_id=request.lesson_id,
                title=request.session_preferences.get("subject", request.lesson_id) if request.session_preferences else request.lesson_id,
                content="This is an auto-generated lesson placeholder.",
                difficulty=request.session_preferences.get("difficulty", "medium") if request.session_preferences else "medium",
                duration=30,
                learning_objectives=[],
                prerequisites=[]
            )
            tutoring_system.lessons[request.lesson_id] = lesson

        session_id = await tutoring_system.start_learning_session(
            request.user_id,
            request.lesson_id,
            request.session_preferences
        )
        
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


