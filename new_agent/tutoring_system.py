"""
Multi-Agent AI Tutoring System
==============================

This is the main integration file that brings together all components
of the adaptive learning system.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio
import uuid
from dataclasses import dataclass

# Import all system components
from models import (
    UserProfile, UserProgress, Lesson, Assessment, TestResult, 
    LearningPath, SessionData, ConceptMastery, PerformanceMetrics,
    GapAnalysisResult, LearningCurveData, MDPRecommendation
)
from llm_service import LLMServiceFactory, GoogleLLMService
from assessment_system import AssessmentSystem
from gap_analysis import GapAnalysisSystem
from knowledge_gap_filler import KnowledgeGapFiller
from learning_curve import LearningCurveTracker
from mdp_learning import MDPLearningPath

# Import all agents
from agents.knowledge_agent import KnowledgeAgent
from agents.practice_agent import PracticeAgent
from agents.motivation_agent import MotivationAgent
from agents.planner_agent import PlannerAgent

@dataclass
class SystemConfig:
    """System configuration"""
    llm_provider: str = "google"
    llm_api_key: str = "AIzaSyCKe9J2cwEzVnsp-MNU-xJxf255_hWAVzE"
    llm_model: str = "gemini-pro"
    max_concurrent_sessions: int = 100
    session_timeout: int = 3600  # seconds
    enable_analytics: bool = True
    enable_gap_analysis: bool = True
    enable_learning_curves: bool = True
    enable_mdp_recommendations: bool = True

class MultiAgentTutoringSystem:
    """Main tutoring system that coordinates all agents and components"""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        
        # Initialize LLM service
        self.llm_service = LLMServiceFactory.create_service(
            config.llm_provider, 
            config.llm_api_key, 
            config.llm_model
        )
        
        # Initialize core systems
        self.assessment_system = AssessmentSystem(self.llm_service)
        self.gap_analysis_system = GapAnalysisSystem(self.llm_service)
        self.knowledge_gap_filler = KnowledgeGapFiller(self.llm_service)
        self.learning_curve_tracker = LearningCurveTracker()
        self.mdp_system = MDPLearningPath()
        
        # Initialize agents
        self.knowledge_agent = KnowledgeAgent(self.llm_service)
        self.practice_agent = PracticeAgent(self.llm_service)
        self.motivation_agent = MotivationAgent(self.llm_service)
        self.planner_agent = PlannerAgent(self.llm_service)
        
        # System state
        self.active_sessions = {}  # session_id -> SessionData
        self.user_profiles = {}  # user_id -> UserProfile
        self.user_progress = {}  # user_id -> UserProgress
        self.lessons = {}  # lesson_id -> Lesson
        self.learning_paths = {}  # path_id -> LearningPath
        
        # Analytics
        self.system_metrics = {
            "total_sessions": 0,
            "active_sessions": 0,
            "lessons_completed": 0,
            "assessments_taken": 0,
            "average_engagement": 0.0,
            "system_uptime": 0.0
        }
    
    async def start_learning_session(self, user_id: str, lesson_id: str, 
                                   session_preferences: Dict[str, Any] = None) -> str:
        """Start a new learning session"""
        
        if session_preferences is None:
            session_preferences = {}
        
        # Create session
        session_id = str(uuid.uuid4())
        session_data = SessionData(
            session_id=session_id,
            user_id=user_id,
            start_time=datetime.now()
        )
        
        # Store session
        self.active_sessions[session_id] = session_data
        self.system_metrics["active_sessions"] = len(self.active_sessions)
        self.system_metrics["total_sessions"] += 1
        
        # Initialize user progress if needed
        if user_id not in self.user_progress:
            self.user_progress[user_id] = UserProgress(user_id=user_id)
        
        # Get lesson
        lesson = self.lessons.get(lesson_id)
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found")
        
        # Start learning process
        await self._initialize_learning_session(session_id, user_id, lesson, session_preferences)
        
        return session_id
    
    async def _initialize_learning_session(self, session_id: str, user_id: str, 
                                         lesson: Lesson, preferences: Dict[str, Any]):
        """Initialize learning session with adaptive content"""
        
        # Get user progress
        user_progress = self.user_progress.get(user_id)
        
        # Determine initial difficulty
        initial_difficulty = self._determine_initial_difficulty(user_progress, lesson)
        
        # Create adaptive content
        adaptive_content = await self._create_adaptive_content(lesson, initial_difficulty, preferences)
        
        # Initialize learning curve tracking
        self.learning_curve_tracker.add_learning_point(
            user_id, lesson.title, 0.5, 0, 0, 0.5  # Initial values
        )
        
        # Store session data
        session = self.active_sessions[session_id]
        session.lessons_completed = [lesson.lesson_id]
        session.engagement_score = 0.5  # Initial engagement
    
    def _determine_initial_difficulty(self, user_progress: UserProgress, lesson: Lesson) -> str:
        """Determine initial difficulty for lesson"""
        
        if not user_progress or not user_progress.test_scores:
            return "medium"
        
        # Calculate average performance
        avg_score = sum(user_progress.test_scores) / len(user_progress.test_scores)
        
        if avg_score >= 0.8:
            return "hard"
        elif avg_score >= 0.6:
            return "medium"
        else:
            return "easy"
    
    async def _create_adaptive_content(self, lesson: Lesson, difficulty: str, 
                                     preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Create adaptive content for lesson"""
        
        # Use knowledge agent to adapt content
        knowledge_state = self.knowledge_agent.create_state(
            user_id="system",
            session_id="adaptive_content",
            concept=lesson.title,
            difficulty=difficulty,
            learning_style=preferences.get("learning_style", "balanced"),
            user_progress=None
        )
        
        knowledge_response = await self.knowledge_agent.process(knowledge_state)
        
        return {
            "original_content": lesson.content,
            "adapted_content": knowledge_response.response,
            "difficulty": difficulty,
            "learning_style": preferences.get("learning_style", "balanced"),
            "adaptations": knowledge_response.metadata
        }
    
    async def process_user_interaction(self, session_id: str, interaction_type: str, 
                                     interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user interaction and provide response"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        user_id = session.user_id
        
        # Process based on interaction type
        if interaction_type == "question_answered":
            return await self._process_question_answer(session_id, interaction_data)
        elif interaction_type == "concept_explanation_requested":
            return await self._process_explanation_request(session_id, interaction_data)
        elif interaction_type == "practice_requested":
            return await self._process_practice_request(session_id, interaction_data)
        elif interaction_type == "assessment_requested":
            return await self._process_assessment_request(session_id, interaction_data)
        elif interaction_type == "progress_check":
            return await self._process_progress_check(session_id, interaction_data)
        else:
            return {"error": f"Unknown interaction type: {interaction_type}"}
    
    async def _process_question_answer(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user's answer to a question"""
        
        session = self.active_sessions[session_id]
        user_id = session.user_id
        
        # Get question and answer data
        question_id = data.get("question_id")
        user_answer = data.get("answer")
        time_taken = data.get("time_taken", 0)
        
        # Evaluate answer
        evaluation_result = await self.practice_agent._grade_answers(
            [user_answer], [data.get("correct_answer", "")], [data.get("question", {})]
        )
        
        # Update learning curve
        performance = evaluation_result["score"] / 100
        self.learning_curve_tracker.add_learning_point(
            user_id, data.get("concept", "general"), performance, time_taken, 1, 0.7
        )
        
        # Check for learning gaps
        if self.config.enable_gap_analysis:
            gap_analysis = await self.gap_analysis_system.analyze_responses(
                [user_answer], [data.get("correct_answer", "")], 
                data.get("concept", "general"), user_id, session_id
            )
            
            if gap_analysis.misconceptions or gap_analysis.learning_gaps:
                # Generate gap filling recommendations
                gap_recommendations = await self.knowledge_gap_filler.get_gap_filling_recommendations(
                    user_id, data.get("concept", "general")
                )
                evaluation_result["gap_recommendations"] = gap_recommendations
        
        # Update session
        session.engagement_score = min(1.0, session.engagement_score + 0.1)
        
        return {
            "evaluation": evaluation_result,
            "feedback": evaluation_result.get("detailed_feedback", []),
            "next_recommendations": await self._get_next_recommendations(session_id),
            "learning_curve": self.learning_curve_tracker.get_learning_curve_analysis(
                user_id, data.get("concept", "general")
            )
        }
    
    async def _process_explanation_request(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request for concept explanation"""
        
        session = self.active_sessions[session_id]
        user_id = session.user_id
        
        # Get user progress
        user_progress = self.user_progress.get(user_id)
        
        # Create knowledge agent state
        knowledge_state = self.knowledge_agent.create_state(
            user_id=user_id,
            session_id=session_id,
            concept=data.get("concept", ""),
            difficulty=data.get("difficulty", "medium"),
            learning_style=data.get("learning_style", "balanced"),
            user_progress=user_progress
        )
        
        # Get explanation
        explanation_response = await self.knowledge_agent.process(knowledge_state)
        
        return {
            "explanation": explanation_response.response,
            "resources": explanation_response.metadata.get("resources", []),
            "confidence": explanation_response.confidence,
            "adaptations": explanation_response.metadata
        }
    
    async def _process_practice_request(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request for practice exercises"""
        
        session = self.active_sessions[session_id]
        user_id = session.user_id
        
        # Create practice agent state
        practice_state = self.practice_agent.create_state(
            user_id=user_id,
            session_id=session_id,
            action="generate_quiz",
            lesson_content=data.get("lesson_content", ""),
            difficulty=data.get("difficulty", "medium"),
            num_questions=data.get("num_questions", 5),
            question_types=data.get("question_types", ["multiple_choice", "short_answer"])
        )
        
        # Generate practice content
        practice_response = await self.practice_agent.process(practice_state)
        
        return {
            "practice_content": practice_response.metadata.get("quiz_data", {}),
            "difficulty": practice_response.metadata.get("difficulty", "medium"),
            "question_count": practice_response.metadata.get("question_count", 0),
            "estimated_time": practice_response.metadata.get("quiz_data", {}).get("estimated_time", 0)
        }
    
    async def _process_assessment_request(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request for assessment"""
        
        session = self.active_sessions[session_id]
        user_id = session.user_id
        
        # Create assessment
        assessment = await self.assessment_system.create_assessment(
            lesson_id=data.get("lesson_id", ""),
            difficulty=data.get("difficulty", "medium"),
            num_questions=data.get("num_questions", 5),
            question_types=data.get("question_types", ["multiple_choice", "short_answer"])
        )
        
        return {
            "assessment_id": assessment.assessment_id,
            "questions": assessment.questions,
            "time_limit": assessment.time_limit,
            "difficulty": assessment.difficulty,
            "passing_score": assessment.passing_score
        }
    
    async def _process_progress_check(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process progress check request"""
        
        session = self.active_sessions[session_id]
        user_id = session.user_id
        
        # Get user progress
        user_progress = self.user_progress.get(user_id)
        
        # Create motivation agent state
        motivation_state = self.motivation_agent.create_state(
            user_id=user_id,
            session_id=session_id,
            action="track_progress",
            user_progress=user_progress,
            recent_activity=session.lessons_completed
        )
        
        # Get progress analysis
        progress_response = await self.motivation_agent.process(motivation_state)
        
        # Get learning curve analysis
        learning_curve_analysis = self.learning_curve_tracker.get_learning_curve_analysis(
            user_id, data.get("concept", "general")
        )
        
        # Get MDP recommendations if enabled
        mdp_recommendations = []
        if self.config.enable_mdp_recommendations:
            mdp_action = self.mdp_system.recommend_action(user_id, {
                "time_available": 30,
                "learning_style": "balanced"
            })
            mdp_recommendations = [{
                "action": mdp_action.action_type.value,
                "difficulty": mdp_action.difficulty,
                "duration": mdp_action.duration,
                "expected_outcome": mdp_action.expected_outcome
            }]
        
        return {
            "progress_analysis": progress_response.metadata.get("progress_analysis", {}),
            "achievements": progress_response.metadata.get("achievements", []),
            "recommendations": progress_response.metadata.get("recommendations", []),
            "learning_curve": learning_curve_analysis,
            "mdp_recommendations": mdp_recommendations,
            "session_stats": {
                "lessons_completed": len(session.lessons_completed),
                "assessments_taken": len(session.assessments_taken),
                "total_time": session.total_time,
                "engagement_score": session.engagement_score
            }
        }
    
    async def _get_next_recommendations(self, session_id: str) -> List[Dict[str, Any]]:
        """Get next learning recommendations"""
        
        session = self.active_sessions[session_id]
        user_id = session.user_id
        
        # Get learning curve analysis
        learning_curve = self.learning_curve_tracker.get_learning_curve_analysis(
            user_id, "general"
        )
        
        recommendations = []
        
        # Difficulty adjustment recommendation
        if learning_curve.get("recommended_difficulty") != learning_curve.get("current_difficulty"):
            recommendations.append({
                "type": "difficulty_adjustment",
                "current": learning_curve.get("current_difficulty"),
                "recommended": learning_curve.get("recommended_difficulty"),
                "reason": "Learning curve analysis suggests difficulty adjustment"
            })
        
        # Practice recommendations
        if learning_curve.get("recent_performance", 0) < 0.7:
            recommendations.append({
                "type": "additional_practice",
                "reason": "Recent performance suggests need for more practice",
                "suggested_actions": ["Review concepts", "Practice with examples", "Take assessment"]
            })
        
        # Engagement recommendations
        if session.engagement_score < 0.6:
            recommendations.append({
                "type": "engagement_boost",
                "reason": "Low engagement detected",
                "suggested_actions": ["Try interactive content", "Take a break", "Switch topics"]
            })
        
        return recommendations
    
    async def end_learning_session(self, session_id: str) -> Dict[str, Any]:
        """End learning session and provide summary"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Update session end time
        session.end_time = datetime.now()
        session.total_time = int((session.end_time - session.start_time).total_seconds() / 60)
        
        # Update user progress
        user_id = session.user_id
        if user_id in self.user_progress:
            user_progress = self.user_progress[user_id]
            user_progress.completed_lessons.extend(session.lessons_completed)
            user_progress.total_time_spent += session.total_time
            user_progress.last_activity = datetime.now()
        
        # Generate session summary
        summary = {
            "session_id": session_id,
            "user_id": user_id,
            "duration_minutes": session.total_time,
            "lessons_completed": len(session.lessons_completed),
            "assessments_taken": len(session.assessments_taken),
            "engagement_score": session.engagement_score,
            "difficulty_adjustments": session.difficulty_adjustments,
            "recommendations": await self._get_next_recommendations(session_id)
        }
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        self.system_metrics["active_sessions"] = len(self.active_sessions)
        
        return summary
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and metrics"""
        
        return {
            "system_metrics": self.system_metrics,
            "active_sessions": len(self.active_sessions),
            "total_users": len(self.user_profiles),
            "total_lessons": len(self.lessons),
            "total_learning_paths": len(self.learning_paths),
            "system_uptime": self.system_metrics["system_uptime"],
            "components_status": {
                "llm_service": "active",
                "assessment_system": "active",
                "gap_analysis": "active" if self.config.enable_gap_analysis else "disabled",
                "learning_curves": "active" if self.config.enable_learning_curves else "disabled",
                "mdp_system": "active" if self.config.enable_mdp_recommendations else "disabled"
            }
        }
    
    async def create_learning_path(self, user_id: str, goals: List[str], 
                                 timeline: str, preferences: Dict[str, Any]) -> str:
        """Create personalized learning path"""
        
        # Create planner agent state
        planner_state = self.planner_agent.create_state(
            user_id=user_id,
            session_id="learning_path_creation",
            action="create_study_plan",
            goals=goals,
            timeline=timeline,
            available_time=preferences.get("available_time", "1 hour per day"),
            learning_style=preferences.get("learning_style", "balanced"),
            current_level=preferences.get("current_level", "beginner")
        )
        
        # Generate learning path
        path_response = await self.planner_agent.process(planner_state)
        
        # Create learning path
        path_id = str(uuid.uuid4())
        
        # Extract difficulty progression as strings
        weekly_breakdown = path_response.metadata.get("study_plan", {}).get("weekly_breakdown", [])
        difficulty_progression = []
        for week in weekly_breakdown:
            if isinstance(week, dict):
                difficulty_progression.append(f"Week {week.get('week_number', 1)}: {week.get('focus_areas', ['Learning'])[0]}")
            else:
                difficulty_progression.append(str(week))
        
        learning_path = LearningPath(
            path_id=path_id,
            user_id=user_id,
            title=f"Personalized Learning Path for {', '.join(goals)}",
            description=path_response.response,
            lessons=[],  # Would be populated from path_response.metadata
            estimated_duration=path_response.metadata.get("study_plan", {}).get("total_estimated_hours", 0) * 60,
            difficulty_progression=difficulty_progression,
            milestones=path_response.metadata.get("study_plan", {}).get("milestones", [])
        )
        
        # Store learning path
        self.learning_paths[path_id] = learning_path
        
        return path_id

# Example usage and testing
async def main():
    """Example usage of the tutoring system"""
    
    # Create system configuration
    config = SystemConfig(
        llm_provider="google",
        llm_api_key="your-api-key-here",
        llm_model="gemini-pro",
        enable_analytics=True,
        enable_gap_analysis=True,
        enable_learning_curves=True,
        enable_mdp_recommendations=True
    )
    
    # Initialize system
    system = MultiAgentTutoringSystem(config)
    
    # Create a sample lesson
    lesson = Lesson(
        lesson_id="lesson_001",
        title="Introduction to Python",
        content="Python is a programming language...",
        difficulty="beginner",
        duration=30,
        learning_objectives=["Understand Python basics", "Write simple programs"],
        prerequisites=["Basic computer skills"]
    )
    
    system.lessons[lesson.lesson_id] = lesson
    
    # Start learning session
    session_id = await system.start_learning_session("user_001", lesson.lesson_id)
    print(f"Started learning session: {session_id}")
    
    # Process user interaction
    interaction_result = await system.process_user_interaction(
        session_id, "concept_explanation_requested", {
            "concept": "Python variables",
            "difficulty": "beginner",
            "learning_style": "visual"
        }
    )
    
    print("Explanation provided:", interaction_result["explanation"][:100] + "...")
    
    # End session
    session_summary = await system.end_learning_session(session_id)
    print("Session summary:", session_summary)
    
    # Get system status
    status = system.get_system_status()
    print("System status:", status)

if __name__ == "__main__":
    asyncio.run(main())
