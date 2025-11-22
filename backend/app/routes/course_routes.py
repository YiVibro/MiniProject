# app/routes/course_routes.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import os
import uuid
from datetime import datetime
import traceback
import asyncio

router = APIRouter(prefix="/api/courses", tags=["courses"])

# Initialize the course creator
course_creator = None

try:
    from new_agent.interactive_course_creator import InteractiveCourseCreator, get_course_creator
    from new_agent.models import UserProfile, Lesson, LearningPath, UserProgress
    from new_agent.assessment_system import AssessmentSystem
    from new_agent.real_llm_service import RealLLMService
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if api_key:
        # Initialize course creator
        course_creator = InteractiveCourseCreator()
        
        # Initialize assessment system
        llm_service = RealLLMService(api_key=api_key, model_name="gemini-2.5-flash")
        assessment_system = AssessmentSystem(llm_service)
        
        print("Course systems initialized successfully")
    else:
        print("Warning: GOOGLE_API_KEY not found. Course features will be disabled.")
        
except ImportError as e:
    print(f"Warning: Could not import course modules: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"Warning: Failed to initialize course systems: {e}")
    traceback.print_exc()

# Request/Response Models
class UserProfileRequest(BaseModel):
    user_id: Optional[str] = None
    name: str
    email: str
    learning_style: str = "balanced"
    preferred_difficulty: str = "intermediate"
    available_time: int = 60
    learning_goals: List[str] = []
    interests: List[str] = []

class UserProfileResponse(BaseModel):
    user_id: str
    name: str
    email: str
    learning_style: str
    preferred_difficulty: str
    available_time: int
    learning_goals: List[str]
    interests: List[str]
    created_at: str

class CourseRequirements(BaseModel):
    subject: str
    topic: str
    weeks: int = 4
    focus: str = "balanced"  # theoretical, practical, balanced, project-based
    assessments: bool = True

class CourseCreationRequest(BaseModel):
    user_id: str
    requirements: CourseRequirements

class CourseResponse(BaseModel):
    course_id: str
    user_id: str
    path_id: str
    subject: str
    topic: str
    title: str
    description: str
    difficulty: str
    learning_style: str
    focus: str
    weeks: int
    total_duration_minutes: int
    total_lessons: int
    assessments_enabled: bool
    lessons: List[Dict[str, Any]]
    progress: float
    completed: bool
    created_at: str

class LessonRequest(BaseModel):
    course_id: str
    lesson_id: str

class LessonResponse(BaseModel):
    lesson_id: str
    title: str
    duration: int
    difficulty: str
    learning_objectives: List[str]
    prerequisites: List[str]
    content: str
    assessment_questions: List[Dict[str, Any]]
    practice_exercises: List[str]
    status: str
    progress: float
    completed: bool

class LessonProgressRequest(BaseModel):
    course_id: str
    lesson_id: str
    progress: float
    completed: bool = False
    answers: Optional[Dict[str, str]] = None

class LessonProgressResponse(BaseModel):
    lesson_id: str
    course_id: str
    progress: float
    completed: bool
    course_progress: float
    updated_at: str

class AssessmentSubmission(BaseModel):
    course_id: str
    lesson_id: str
    user_id: str
    answers: Dict[str, str]

class AssessmentResult(BaseModel):
    lesson_id: str
    course_id: str
    score: float
    correct_count: int
    total_questions: int
    feedback: List[str]
    mastered_topics: List[str]
    knowledge_gaps: List[str]
    recommendations: List[str]
    submitted_at: str

class PracticeRequest(BaseModel):
    course_id: str
    lesson_id: str
    count: int = 5

class PracticeResponse(BaseModel):
    lesson_id: str
    course_id: str
    total_available: int
    questions: List[Dict[str, Any]]

class CourseProgressResponse(BaseModel):
    course_id: str
    title: str
    completion_percentage: float
    lessons_completed: int
    total_lessons: int
    current_lesson: Optional[str]
    time_spent: int
    estimated_time_remaining: int
    status: str
    created_at: str

class LearningCurveResponse(BaseModel):
    course_id: str
    data_points: List[Dict[str, Any]]
    trend: str
    average_score: float
    learning_velocity: float

class RecommendationsResponse(BaseModel):
    course_id: str
    user_id: str
    recommendations: List[Dict[str, Any]]
    next_best_action: str
    priority_topics: List[str]

class GapAnalysisResponse(BaseModel):
    course_id: str
    user_id: str
    identified_gaps: List[str]
    remedial_lessons: List[Dict[str, Any]]
    estimated_remedial_time: int
    priority: str

# ========================================================================
# USER PROFILE ENDPOINTS
# ========================================================================

@router.post("/user/profile", response_model=UserProfileResponse)
async def create_user_profile(request: UserProfileRequest):
    """Create or update user profile"""
    try:
        if not course_creator:
            raise HTTPException(status_code=503, detail="Course creator not available")

        user_data = {
            "user_id": request.user_id,
            "name": request.name,
            "email": request.email,
            "learning_style": request.learning_style,
            "preferred_difficulty": request.preferred_difficulty,
            "available_time": request.available_time,
            "learning_goals": request.learning_goals,
            "interests": request.interests
        }

        profile = await course_creator.create_user_profile(user_data)
        return UserProfileResponse(**profile)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile creation failed: {str(e)}")

# ========================================================================
# COURSE CREATION ENDPOINTS
# ========================================================================

@router.post("/create", response_model=CourseResponse)
async def create_course(request: CourseCreationRequest):
    """Create a new interactive course"""
    try:
        if not course_creator:
            raise HTTPException(status_code=503, detail="Course creator not available")

        # Ensure system is initialized
        await course_creator.initialize_system()

        # Create course using the interactive course creator
        course_requirements = {
            "subject": request.requirements.subject,
            "topic": request.requirements.topic,
            "weeks": request.requirements.weeks,
            "focus": request.requirements.focus,
            "assessments": request.requirements.assessments
        }

        course = await course_creator.create_course(request.user_id, course_requirements)
        return CourseResponse(**course)

    except Exception as e:
        print(f"Course creation error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Course creation failed: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_courses(user_id: str):
    """Get all courses for a user"""
    try:
        if not course_creator:
            raise HTTPException(status_code=503, detail="Course creator not available")

        courses = await course_creator.get_user_courses(user_id)
        return courses

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user courses: {str(e)}")

@router.get("/{course_id}/overview")
async def get_course_overview(course_id: str):
    """Get course overview and structure"""
    try:
        if not course_creator:
            raise HTTPException(status_code=503, detail="Course creator not available")

        overview = await course_creator.get_course_overview(course_id)
        return overview

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get course overview: {str(e)}")

# ========================================================================
# LESSON INTERACTION ENDPOINTS
# ========================================================================

@router.get("/{course_id}/lessons/{lesson_id}", response_model=LessonResponse)
async def get_lesson(course_id: str, lesson_id: str):
    """Get lesson details"""
    try:
        if not course_creator:
            raise HTTPException(status_code=503, detail="Course creator not available")

        lesson = await course_creator.get_lesson(course_id, lesson_id)
        return LessonResponse(**lesson)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get lesson: {str(e)}")

@router.post("/{course_id}/lessons/{lesson_id}/start")
async def start_lesson(course_id: str, lesson_id: str, user_id: str):
    """Start a learning session for a lesson"""
    try:
        if not course_creator:
            raise HTTPException(status_code=503, detail="Course creator not available")

        session = await course_creator.start_lesson(course_id, lesson_id, user_id)
        return session

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start lesson: {str(e)}")

@router.post("/{course_id}/lessons/{lesson_id}/progress", response_model=LessonProgressResponse)
async def update_lesson_progress(request: LessonProgressRequest):
    """Update lesson progress"""
    try:
        if not course_creator:
            raise HTTPException(status_code=503, detail="Course creator not available")

        result = await course_creator.update_lesson_progress(
            course_id=request.course_id,
            lesson_id=request.lesson_id,
            progress=request.progress,
            completed=request.completed,
            answers=request.answers
        )
        return LessonProgressResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update progress: {str(e)}")

# ========================================================================
# ASSESSMENT ENDPOINTS
# ========================================================================

@router.post("/{course_id}/lessons/{lesson_id}/assessments/submit", response_model=AssessmentResult)
async def submit_assessment(request: AssessmentSubmission):
    """Submit assessment answers and get evaluation"""
    try:
        if not course_creator:
            raise HTTPException(status_code=503, detail="Course creator not available")

        result = await course_creator.submit_assessment(
            course_id=request.course_id,
            lesson_id=request.lesson_id,
            user_id=request.user_id,
            answers=request.answers
        )
        return AssessmentResult(**result)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment submission failed: {str(e)}")

# ========================================================================
# PRACTICE ENDPOINTS
# ========================================================================

@router.post("/{course_id}/lessons/{lesson_id}/practice", response_model=PracticeResponse)
async def get_practice_questions(request: PracticeRequest):
    """Get practice questions for a lesson"""
    try:
        if not course_creator:
            raise HTTPException(status_code=503, detail="Course creator not available")

        questions = await course_creator.get_practice_questions(
            course_id=request.course_id,
            lesson_id=request.lesson_id,
            count=request.count
        )
        return PracticeResponse(**questions)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get practice questions: {str(e)}")

# ========================================================================
# PROGRESS & ANALYTICS ENDPOINTS
# ========================================================================

@router.get("/{course_id}/progress", response_model=CourseProgressResponse)
async def get_course_progress(course_id: str):
    """Get overall course progress"""
    try:
        if not course_creator:
            raise HTTPException(status_code=503, detail="Course creator not available")

        progress = await course_creator.get_course_progress(course_id)
        return CourseProgressResponse(**progress)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get course progress: {str(e)}")

@router.get("/{course_id}/learning-curve", response_model=LearningCurveResponse)
async def get_learning_curve(course_id: str):
    """Get learning curve analytics"""
    try:
        if not course_creator:
            raise HTTPException(status_code=503, detail="Course creator not available")

        curve_data = await course_creator.get_learning_curve(course_id)
        return LearningCurveResponse(**curve_data)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get learning curve: {str(e)}")

# ========================================================================
# RECOMMENDATIONS & GAP ANALYSIS ENDPOINTS
# ========================================================================

@router.get("/{course_id}/recommendations", response_model=RecommendationsResponse)
async def get_learning_recommendations(course_id: str, user_id: str):
    """Get AI-powered learning recommendations"""
    try:
        if not course_creator:
            raise HTTPException(status_code=503, detail="Course creator not available")

        recommendations = await course_creator.get_learning_recommendations(course_id, user_id)
        return RecommendationsResponse(**recommendations)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.get("/{course_id}/gap-analysis", response_model=GapAnalysisResponse)
async def analyze_knowledge_gaps(course_id: str, user_id: str):
    """Analyze knowledge gaps and provide remedial content"""
    try:
        if not course_creator:
            raise HTTPException(status_code=503, detail="Course creator not available")

        gap_analysis = await course_creator.analyze_knowledge_gaps(course_id, user_id)
        return GapAnalysisResponse(**gap_analysis)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze knowledge gaps: {str(e)}")

# ========================================================================
# AGENT-SPECIFIC ENDPOINTS
# ========================================================================

@router.post("/agents/knowledge/gap-analysis")
async def perform_agent_gap_analysis(user_id: str, course_id: str, assessment_results: Dict[str, Any]):
    """Perform knowledge gap analysis using KnowledgeAgent"""
    try:
        from new_agent.agents.knowledge_agent import KnowledgeAgent
        from new_agent.real_llm_service import RealLLMService
        
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=503, detail="API key not available")
            
        llm_service = RealLLMService(api_key=api_key, model_name="gemini-2.5-flash")
        knowledge_agent = KnowledgeAgent(llm_service)
        
        gap_analysis = await knowledge_agent.analyze_knowledge_gaps(
            user_id=user_id,
            course_id=course_id,
            assessment_data=assessment_results
        )
        
        return gap_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gap analysis failed: {str(e)}")

@router.post("/agents/planner/optimize-schedule")
async def optimize_learning_schedule(user_id: str, course_id: str, schedule_constraints: Dict[str, Any]):
    """Optimize learning schedule using PlannerAgent"""
    try:
        from new_agent.agents.planner_agent import PlannerAgent
        from new_agent.real_llm_service import RealLLMService
        
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=503, detail="API key not available")
            
        llm_service = RealLLMService(api_key=api_key, model_name="gemini-2.5-flash")
        planner_agent = PlannerAgent(llm_service)
        
        optimized_schedule = await planner_agent.create_optimized_schedule(
            user_id=user_id,
            course_id=course_id,
            constraints=schedule_constraints
        )
        
        return optimized_schedule
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schedule optimization failed: {str(e)}")

@router.post("/agents/motivation/personalized")
async def get_motivational_content(user_id: str, progress_data: Dict[str, Any]):
    """Get personalized motivational content using MotivationAgent"""
    try:
        from new_agent.agents.motivation_agent import MotivationAgent
        from new_agent.real_llm_service import RealLLMService
        
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=503, detail="API key not available")
            
        llm_service = RealLLMService(api_key=api_key, model_name="gemini-2.5-flash")
        motivation_agent = MotivationAgent(llm_service)
        
        motivational_content = await motivation_agent.generate_motivational_content(
            user_id=user_id,
            progress_data=progress_data
        )
        
        return motivational_content
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Motivational content generation failed: {str(e)}")

@router.post("/agents/practice/generate-exercises")
async def generate_practice_exercises(lesson_id: str, topic: str, difficulty: str, exercise_types: List[str] = None):
    """Generate practice exercises using PracticeAgent"""
    try:
        from new_agent.agents.practice_agent import PracticeAgent
        from new_agent.real_llm_service import RealLLMService
        
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=503, detail="API key not available")
            
        llm_service = RealLLMService(api_key=api_key, model_name="gemini-2.5-flash")
        practice_agent = PracticeAgent(llm_service)
        
        exercises = await practice_agent.generate_practice_exercises(
            topic=topic,
            difficulty=difficulty,
            exercise_types=exercise_types or ["multiple_choice", "coding", "problem_solving"]
        )
        
        return {
            "lesson_id": lesson_id,
            "topic": topic,
            "exercises": exercises
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Practice exercise generation failed: {str(e)}")

# ========================================================================
# UTILITY ENDPOINTS
# ========================================================================

@router.get("/subjects")
async def get_available_subjects():
    """Get available subjects"""
    return {
        "subjects": [
            "Python Programming", "JavaScript", "Machine Learning", "Web Development",
            "Data Science", "Computer Science", "Mathematics", "Physics", "Chemistry",
            "Biology", "Artificial Intelligence", "Deep Learning", "Natural Language Processing",
            "Computer Vision", "Software Engineering", "Database Systems", "Networking",
            "Cybersecurity", "Mobile Development", "Game Development", "Cloud Computing"
        ]
    }

@router.get("/learning-styles")
async def get_learning_styles():
    """Get available learning styles"""
    return {
        "styles": [
            {"value": "visual", "label": "Visual", "description": "Learn through diagrams and visual aids"},
            {"value": "auditory", "label": "Auditory", "description": "Learn through listening and explanations"},
            {"value": "kinesthetic", "label": "Kinesthetic", "description": "Learn through hands-on activities"},
            {"value": "reading_writing", "label": "Reading/Writing", "description": "Learn through text-based materials"},
            {"value": "social", "label": "Social", "description": "Learn through group interactions"},
            {"value": "solitary", "label": "Solitary", "description": "Learn through self-study"},
            {"value": "balanced", "label": "Balanced", "description": "Mix of different learning styles"}
        ]
    }

@router.get("/difficulty-levels")
async def get_difficulty_levels():
    """Get available difficulty levels"""
    return {
        "levels": [
            {"value": "beginner", "label": "Beginner", "description": "No prior knowledge required"},
            {"value": "intermediate", "label": "Intermediate", "description": "Basic knowledge expected"},
            {"value": "advanced", "label": "Advanced", "description": "Substantial prior knowledge required"},
            {"value": "expert", "label": "Expert", "description": "For professionals and specialists"}
        ]
    }

@router.get("/focus-types")
async def get_focus_types():
    """Get available focus types"""
    return {
        "focus_types": [
            {"value": "theoretical", "label": "Theoretical", "description": "Focus on concepts and theory"},
            {"value": "practical", "label": "Practical", "description": "Focus on hands-on applications"},
            {"value": "balanced", "label": "Balanced", "description": "Mix of theory and practice"},
            {"value": "project-based", "label": "Project-based", "description": "Learn through building projects"}
        ]
    }

@router.get("/system-status")
async def get_system_status():
    """Get status of course systems"""
    status = {
        "course_creator": bool(course_creator),
        "assessment_system": bool(assessment_system),
        "timestamp": datetime.now().isoformat()
    }
    return status