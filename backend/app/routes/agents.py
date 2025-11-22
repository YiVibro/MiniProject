from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import asyncio
import sys
from pathlib import Path
import os
from datetime import datetime
from uuid import uuid4
from new_agent.tutoring_system import MultiAgentTutoringSystem, SystemConfig
from new_agent.dynamic_learning_planner import DynamicLearningPlanner
from new_agent.interactive_course_creator import InteractiveCourseCreator

# Import from your new_agent modules
try:
    from new_agent.tutoring_system import MultiAgentTutoringSystem, SystemConfig
    from new_agent.dynamic_learning_planner import DynamicLearningPlanner
    from new_agent.interactive_course_creator import InteractiveCourseCreator
    from new_agent.models import UserProfile, UserProgress, Lesson
    from new_agent.real_llm_service import RealLLMService
    
    # Try to import LangGraphCourseCreator
    try:
        from new_agent.langgraph_course_creator import LangGraphCourseCreator
        LANGGRAPH_AVAILABLE = True
    except ImportError:
        LangGraphCourseCreator = None
        LANGGRAPH_AVAILABLE = False
        
except ImportError as e:
    print(f"Warning: Could not import new_agent modules: {e}")
    # Set fallbacks
    MultiAgentTutoringSystem = None
    SystemConfig = None
    DynamicLearningPlanner = None
    InteractiveCourseCreator = None
    UserProfile = None
    UserProgress = None
    Lesson = None
    LangGraphCourseCreator = None
    LANGGRAPH_AVAILABLE = False

from app.database.db import supabase

router = APIRouter(prefix="/api/agents", tags=["agents"])
# Initialize systems with proper error handling
tutoring_system = None
learning_planner = None
course_creator = None
lg_course_creator = None

try:
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if api_key and MultiAgentTutoringSystem and SystemConfig:
        # Initialize LLM service
        llm_service = RealLLMService(
            api_key=api_key,
            model_name="gemini-2.5-flash"
        )
        
        # Initialize tutoring system
        config = SystemConfig(
            llm_provider="google",
            llm_api_key=api_key,
            llm_model="gemini-2.5-flash",
            enable_analytics=True,
            enable_gap_analysis=True,
            enable_learning_curves=True,
            enable_mdp_recommendations=True
        )
        tutoring_system = MultiAgentTutoringSystem(config)
        
        # Initialize other systems
        if DynamicLearningPlanner:
            learning_planner = DynamicLearningPlanner()
        if InteractiveCourseCreator:
            course_creator = InteractiveCourseCreator()
        
        # Initialize LangGraph if available
        if LANGGRAPH_AVAILABLE and LangGraphCourseCreator:
            try:
                lg_course_creator = LangGraphCourseCreator(
                    api_key=api_key,
                    model_name="gemini-2.5-flash",
                )
            except Exception as e:
                print(f"Warning: Failed to initialize LangGraphCourseCreator: {e}")
                lg_course_creator = None
        
        print("AI agents initialized successfully")
    else:
        print("Warning: API key missing or modules not available. AI features disabled.")
        
except Exception as e:
    print(f"Warning: Failed to initialize AI systems: {e}")

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

class ContinueLearningRequest(BaseModel):
    user_id: str
    course_id: Optional[str] = None  # From user_progress.id
    course_name: Optional[str] = None  # From user_progress.course_name

class ContinueLearningResponse(BaseModel):
    course_id: str
    learning_goal_id: str
    curriculum: List[Dict[str, Any]]  # Full lesson data
    progress: Dict[str, Any]  # Current progress
    requirements: Dict[str, Any]  # Original preferences
    learning_path: Dict[str, Any]
    is_cached: bool = False

@router.post("/create-assessment", response_model=AssessmentResponse)
async def create_assessment(request: CreateAssessmentRequest):
    """Create an assessment for a lesson"""
    try:
        if not tutoring_system:
            raise HTTPException(status_code=503,detail="AI system not available")
        
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
        if not tutoring_system:
            raise HTTPException(status_code=503,detail="AI system not available")
        
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
        if not learning_planner:
            raise HTTPException(status_code=503, detail="Learning planner not available")

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
        if not course_creator and not lg_course_creator:
            raise HTTPException(status_code=503, detail="Course Creator not available")
        
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
        
        # Try LangGraph-based generation first 
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
        if not track_progress:
            return {"Track progress issue"}
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
        if not start_learning_session:
            return {"Start learning session issue"}
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
        if not learning_planner:
            return {"Learning planner issue"}
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
    
@router.post("/continue-learning", response_model=ContinueLearningResponse)
async def continue_learning(request: ContinueLearningRequest):
    """Continue learning - generate course on first click, fetch existing on subsequent clicks"""
    try:
        # Validate request
        if not request.user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        if not request.course_id and not request.course_name:
            raise HTTPException(status_code=400, detail="Either course_id or course_name must be provided")
        
        # Check Supabase connection
        if not supabase:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Step 1: ✅ CHECK IF COURSE ALREADY EXISTS IN generated_courses TABLE
        existing_course = None
        course_name = None
        
        try:
            # If we have course_id, look up by course_id
            if request.course_id:
                existing_response = supabase.table("generated_courses")\
                    .select("*")\
                    .eq("id", request.course_id)\
                    .eq("user_id", request.user_id)\
                    .execute()
                
                if existing_response.data and len(existing_response.data) > 0:
                    existing_course = existing_response.data[0]
                    course_name = existing_course.get("course_name")
            
            # If no course found by ID, try by course_name
            if not existing_course and request.course_name:
                course_name = request.course_name
                existing_response = supabase.table("generated_courses")\
                    .select("*")\
                    .eq("user_id", request.user_id)\
                    .eq("course_name", course_name)\
                    .execute()
                
                if existing_response.data and len(existing_response.data) > 0:
                    existing_course = existing_response.data[0]
            
            # If still no course found, check user_progress for course_name
            if not existing_course:
                if request.course_id:
                    progress_response = supabase.table("user_progress").select("*").eq("id", request.course_id).eq("user_id", request.user_id).execute()
                    if progress_response.data and len(progress_response.data) > 0:
                        user_progress_record = progress_response.data[0]
                        course_name = user_progress_record.get("course_name")
                elif request.course_name:
                    course_name = request.course_name
                    
        except Exception as e:
            print(f"Error querying database: {e}")
            # Continue with course generation if query fails
        
        # Step 2: ✅ RETURN EXISTING COURSE IF FOUND
        if existing_course:
            curriculum = existing_course.get("curriculum", [])
            course_metadata = existing_course.get("course_metadata", {})
            
            # Get progress from user_progress
            progress_percent = 0
            try:
                progress_response = supabase.table("user_progress")\
                    .select("*")\
                    .eq("user_id", request.user_id)\
                    .eq("course_name", course_name)\
                    .execute()
                
                if progress_response.data and len(progress_response.data) > 0:
                    progress_percent = progress_response.data[0].get("progress_percent", 0)
            except Exception as e:
                print(f"Error fetching progress: {e}")
            
            # Calculate completed lessons
            total_lessons = len(curriculum) if isinstance(curriculum, list) else 0
            completed_lessons = int((progress_percent / 100) * total_lessons) if total_lessons > 0 else 0
            
            return ContinueLearningResponse(
                course_id=str(existing_course.get("id")),
                learning_goal_id=str(existing_course.get("learning_goal_id", "")),
                curriculum=curriculum if isinstance(curriculum, list) else [],
                progress={
                    "progress_percent": progress_percent,
                    "completed_lessons": completed_lessons,
                    "total_lessons": total_lessons,
                    "current_lesson": completed_lessons + 1 if completed_lessons < total_lessons else total_lessons
                },
                requirements=course_metadata.get("requirements", {}),
                learning_path=course_metadata.get("learning_path", {}),
                is_cached=True  # ✅ ADD THIS FIELD TO INDICATE IT'S FROM CACHE
            )
        
        # Step 3: ✅ GENERATE NEW COURSE (existing logic with improvements)
        
        # Get learning_goal record
        learning_goal = None
        if not course_name:
            raise HTTPException(status_code=400, detail="Course name is required")
        
        try:
            goals_response = supabase.table("learning_goals").select("*").eq("user_id", request.user_id).eq("title", course_name).execute()
            if goals_response.data and len(goals_response.data) > 0:
                learning_goal = goals_response.data[0]
            else:
                # Try to find by course_name in user_progress
                progress_response = supabase.table("user_progress").select("*").eq("user_id", request.user_id).eq("course_name", course_name).execute()
                if progress_response.data and len(progress_response.data) > 0:
                    user_progress_record = progress_response.data[0]
                    # Try to find learning_goal by matching description or title
                    all_goals = supabase.table("learning_goals").select("*").eq("user_id", request.user_id).execute()
                    if all_goals.data:
                        for goal in all_goals.data:
                            if goal.get("title") == course_name or (goal.get("description") and course_name.lower() in goal.get("description", "").lower()):
                                learning_goal = goal
                                break
        except Exception as e:
            print(f"Error querying learning_goals: {e}")
        
        if not learning_goal:
            # If no learning goal found, create a basic one from the course name
            learning_goal = {
                "id": str(uuid4()),
                "user_id": request.user_id,
                "title": course_name,
                "description": f"Course for {course_name}",
                "difficulty": "intermediate",
                "learning_style": "balanced",
                "focus_type": "balanced",
                "target_weeks": 4,
                "study_duration_hours": 5
            }
        
        learning_goal_id = learning_goal.get("id")
        
        # Extract preferences from learning_goal
        subject = learning_goal.get("category_id", "General")
        # Get category name if category_id exists
        category_id = learning_goal.get("category_id")
        if category_id:
            try:
                cat_response = supabase.table("categories").select("name").eq("id", category_id).execute()
                if cat_response.data:
                    subject = cat_response.data[0].get("name", "General")
            except Exception as e:
                print(f"Error fetching category: {e}")
        
        difficulty = learning_goal.get("difficulty", "intermediate")
        learning_style = learning_goal.get("learning_style", "balanced")
        focus_type = learning_goal.get("focus_type", "balanced")
        weeks = learning_goal.get("target_weeks", 4)
        description = learning_goal.get("description", "")
        topic = learning_goal.get("title", course_name)
        
        # Create user profile from learning_goal
        user_profile = UserProfile(
            user_id=request.user_id,
            name="Learner",
            email=f"{request.user_id}@example.com",
            learning_style=learning_style,
            preferred_difficulty=difficulty,
            available_time=learning_goal.get("study_duration_hours", 5) * 60,
            learning_goals=[description] if description else ["Master the subject"],
            interests=[]
        )
        
        # Generate course using available course creators
        course_id = str(uuid4())
        curriculum = []
        learning_path_data = {}
        
        # Try LangGraphCourseCreator first
        if lg_course_creator is not None:
            goal = f"Learn {subject} focusing on {topic} with a {focus_type} approach."
            try:
                lg = await lg_course_creator.create_course(
                    subject=subject,
                    topic=topic,
                    weeks=weeks,
                    focus=focus_type,
                    user_profile=user_profile.dict(),
                    goal=goal,
                )
                curriculum = lg.get("curriculum", [])
                learning_path_data = lg.get("learning_path", {})
            except Exception as e:
                print(f"LangGraph course creation failed: {e}, falling back to InteractiveCourseCreator")
        
        # Fallback to InteractiveCourseCreator
        if not curriculum:
            if not course_creator:
                raise HTTPException(
                    status_code=503, 
                    detail="Course creator not available. Please ensure GOOGLE_API_KEY is set in environment variables."
                )
            if not course_creator.system:
                await course_creator.initialize_system()
            
            curriculum_lessons = await course_creator.system.create_dynamic_curriculum(
                subject=subject,
                level=difficulty,
                duration_weeks=weeks,
                user_profile=user_profile
            )
            
            # Convert lessons to dict format
            curriculum = [{
                "id": lesson.lesson_id,
                "title": lesson.title,
                "difficulty": lesson.difficulty,
                "duration": lesson.duration,
                "content": lesson.content,
                "learning_objectives": lesson.learning_objectives,
                "prerequisites": lesson.prerequisites,
                "assessment_questions": lesson.assessment_questions if hasattr(lesson, 'assessment_questions') else [],
                "practice_exercises": lesson.practice_exercises if hasattr(lesson, 'practice_exercises') else []
            } for lesson in curriculum_lessons]
            
            # Create learning path
            path_id = await course_creator.system.create_personalized_learning_path(
                user_id=request.user_id,
                user_request=f"Learn {subject} focusing on {topic} with {focus_type} approach",
                user_profile=user_profile
            )
            
            # Get learning path data
            learning_path_obj = course_creator.system.learning_paths.get(path_id)
            if learning_path_obj:
                if hasattr(learning_path_obj, 'model_dump'):
                    learning_path_data = learning_path_obj.model_dump()
                elif hasattr(learning_path_obj, 'dict'):
                    learning_path_data = learning_path_obj.dict()
                else:
                    learning_path_data = {
                        "title": getattr(learning_path_obj, 'title', f"{subject} Course"),
                        "description": getattr(learning_path_obj, 'description', ""),
                        "estimated_duration": getattr(learning_path_obj, 'estimated_duration', weeks * 7 * 60),
                        "difficulty_progression": getattr(learning_path_obj, 'difficulty_progression', []),
                        "milestones": getattr(learning_path_obj, 'milestones', [])
                    }
            course_id = path_id
        
        # Prepare course metadata
        course_metadata = {
            "requirements": {
                "subject": subject,
                "topic": topic,
                "difficulty": difficulty,
                "learning_style": learning_style,
                "focus": focus_type,
                "weeks": weeks,
                "description": description
            },
            "learning_path": {
                "path_id": course_id,
                "title": learning_path_data.get("title", f"{subject} Course"),
                "description": learning_path_data.get("description", ""),
                "estimated_duration": learning_path_data.get("estimated_duration", weeks * 7 * 60),
                "difficulty_progression": learning_path_data.get("difficulty_progression", []),
                "milestones": learning_path_data.get("milestones", [])
            }
        }
        
        # Step 4: ✅ STORE GENERATED COURSE IN DATABASE
        try:
            stored_course = supabase.table("generated_courses").insert({
                "id": course_id,
                "user_id": request.user_id,
                "learning_goal_id": learning_goal_id,
                "course_name": course_name,
                "curriculum": curriculum,
                "course_metadata": course_metadata,
                "progress": {
                    "completed_lessons": 0,
                    "total_lessons": len(curriculum),
                    "progress_percent": 0
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }).execute()
            
            print(f"✅ Course stored in database with ID: {course_id}")
            
        except Exception as e:
            print(f"❌ Could not insert into generated_courses: {e}")
            # Fallback: try to store in learning_goals
            try:
                supabase.table("learning_goals").update({
                    "generated_curriculum": curriculum,
                    "course_metadata": course_metadata
                }).eq("id", learning_goal_id).execute()
                print(f"✅ Course stored in learning_goals as fallback")
            except Exception as e2:
                print(f"❌ Could not update learning_goals: {e2}")
        
        # Step 5: ✅ RETURN GENERATED COURSE
        return ContinueLearningResponse(
            course_id=course_id,
            learning_goal_id=str(learning_goal_id),
            curriculum=curriculum,
            progress={
                "progress_percent": 0,
                "completed_lessons": 0,
                "total_lessons": len(curriculum),
                "current_lesson": 1
            },
            requirements=course_metadata["requirements"],
            learning_path=course_metadata["learning_path"],
            is_cached=False  # ✅ ADD THIS FIELD TO INDICATE IT'S NEWLY GENERATED
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in continue_learning: {e}")
        print(f"Full traceback:\n{error_trace}")
        
        error_detail = str(e)
        if hasattr(e, '__cause__') and e.__cause__:
            error_detail += f" | Cause: {str(e.__cause__)}"
        
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to continue learning: {error_detail}"
        )
    
    
@router.get("/system-status")
async def get_system_status():
    """Get system status and metrics"""
    try:
        if not tutoring_system:
            return {"status": "disabled", "reason": "AI system not initialized"}
            
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

@router.post("/api/agents/check-course-exists")
async def check_course_exists(request: dict):
    """
    Check if a course already exists for the user
    Returns: { "exists": true/false, "course_id": "..." }
    """
    try:
        user_id = request.get("user_id")
        course_name = request.get("course_name")
        
        if not user_id or not course_name:
            raise HTTPException(status_code=400, detail="user_id and course_name are required")
        
        # Check if course exists in database
        result = supabase.table("generated_courses")\
            .select("course_id, created_at, progress")\
            .eq("user_id", user_id)\
            .eq("course_name", course_name)\
            .execute()
        
        if result.data and len(result.data) > 0:
            course = result.data[0]
            return {
                "exists": True,
                "course_id": course["course_id"],
                "created_at": course.get("created_at"),
                "progress": course.get("progress", {})
            }
        else:
            return {
                "exists": False,
                "course_id": None
            }
            
    except Exception as e:
        print(f"❌ Error checking course existence: {str(e)}")
        # Return false on error to allow course generation
        return {
            "exists": False,
            "course_id": None,
            "error": str(e)
        }
    
@router.post("/api/agents/update-course-progress")
async def update_course_progress(request: dict):
    """
    Update course progress in database
    """
    try:
        user_id = request.get("user_id")
        course_id = request.get("course_id")
        progress = request.get("progress", {})
        
        if not user_id or not course_id:
            raise HTTPException(status_code=400, detail="user_id and course_id are required")
        
        # Update progress in database
        result = supabase.table("generated_courses")\
            .update({"progress": progress, "updated_at": datetime.now().isoformat()})\
            .eq("user_id", user_id)\
            .eq("course_id", course_id)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return {
            "success": True,
            "message": "Progress updated successfully",
            "progress": progress
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error updating progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
