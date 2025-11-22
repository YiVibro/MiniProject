#!/usr/bin/env python3
"""
Interactive Course Creator - Web Backend Service
==============================================

Handles dynamic course creation and interaction for website.
Replaces terminal-based CLI with async service methods.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import os
import uuid
from .enhanced_tutoring_system import EnhancedTutoringSystem, SystemConfig
from .models import UserProfile, UserProgress
from .dynamic_lesson_generator import DynamicLessonGenerator


class InteractiveCourseCreator:
    """Backend service for interactive course creation and management"""
    
    def __init__(self):
        self.system = None
        self.user_courses: Dict[str, Any] = {}  # Store user courses
        self.learning_sessions: Dict[str, Any] = {}  # Store active sessions
        
    async def initialize_system(self):
        """Initialize the tutoring system"""
        if self.system is not None:
            return  # Already initialized
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set!")
        
        config = SystemConfig(
            llm_provider="google",
            llm_api_key=api_key,
            llm_model="gemini-2.5-flash",
            enable_analytics=True,
            enable_gap_analysis=True,
            enable_learning_curves=True,
            enable_mdp_recommendations=True
        )
        
        self.system = EnhancedTutoringSystem(config)
        return {"status": "initialized", "message": "System ready"}

    # ========================================================================
    # COURSE CREATION ENDPOINTS
    # ========================================================================
    
    async def create_user_profile(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user profile from website form data"""
        name = user_data.get("name", "Learner")
        email = user_data.get("email", f"{name.lower()}@example.com")
        learning_style = user_data.get("learning_style", "balanced")
        preferred_difficulty = user_data.get("preferred_difficulty", "intermediate")
        available_time = user_data.get("available_time", 60)
        learning_goals = user_data.get("learning_goals", ["Master the subject"])
        interests = user_data.get("interests", [])
        user_id = user_data.get("user_id", f"user_{uuid.uuid4()}")
        
        profile = UserProfile(
            user_id=user_id,
            name=name,
            email=email,
            learning_style=learning_style,
            preferred_difficulty=preferred_difficulty,
            available_time=available_time,
            learning_goals=learning_goals,
            interests=interests
        )
        
        return {
            "user_id": user_id,
            "name": name,
            "email": email,
            "learning_style": learning_style,
            "preferred_difficulty": preferred_difficulty,
            "available_time": available_time,
            "learning_goals": learning_goals,
            "interests": interests,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def create_course(self, user_id: str, course_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a dynamic course based on requirements
        
        Args:
            user_id: User ID
            course_requirements: {
                "subject": str,
                "topic": str,
                "weeks": int,
                "focus": str,  # theoretical, practical, balanced, project-based
                "assessments": bool
            }
        """
        await self.initialize_system()
        
        subject = course_requirements.get("subject", "General Programming")
        topic = course_requirements.get("topic", "Fundamentals")
        weeks = course_requirements.get("weeks", 4)
        focus = course_requirements.get("focus", "balanced")
        assessments = course_requirements.get("assessments", True)
        
        # Get user profile (should exist from create_user_profile call)
        if user_id not in self.system.user_profiles:
            raise ValueError(f"User profile not found for {user_id}")
        
        user_profile = self.system.user_profiles[user_id]
        
        # Generate curriculum
        curriculum = await self.system.create_dynamic_curriculum(
            subject=subject,
            level=user_profile.preferred_difficulty,
            duration_weeks=weeks,
            user_profile=user_profile
        )
        
        # Create learning path
        path_id = await self.system.create_personalized_learning_path(
            user_id=user_id,
            user_request=f"Learn {subject} focusing on {topic} with {focus} approach",
            user_profile=user_profile
        )
        
        # Create course object
        course_id = str(uuid.uuid4())
        course = {
            "course_id": course_id,
            "user_id": user_id,
            "path_id": path_id,
            "subject": subject,
            "topic": topic,
            "title": f"{subject} - {topic}",
            "description": f"A personalized {focus} course on {subject}",
            "difficulty": user_profile.preferred_difficulty,
            "learning_style": user_profile.learning_style,
            "focus": focus,
            "weeks": weeks,
            "total_duration_minutes": sum(lesson.duration for lesson in curriculum),
            "total_lessons": len(curriculum),
            "assessments_enabled": assessments,
            "lessons": [
                {
                    "lesson_id": lesson.lesson_id,
                    "title": lesson.title,
                    "duration": lesson.duration,
                    "difficulty": lesson.difficulty,
                    "learning_objectives": lesson.learning_objectives,
                    "prerequisites": lesson.prerequisites or [],
                    "content": lesson.content,
                    "assessment_questions": lesson.assessment_questions or [],
                    "practice_exercises": lesson.practice_exercises or [],
                    "status": "locked",
                    "progress": 0,
                    "completed": False
                }
                for lesson in curriculum
            ],
            "created_at": datetime.utcnow().isoformat(),
            "progress": 0,
            "completed": False
        }
        
        # Unlock first lesson
        if course["lessons"]:
            course["lessons"][0]["status"] = "available"
        
        # Store course
        self.user_courses[course_id] = course
        
        return course

    # ========================================================================
    # COURSE BROWSING ENDPOINTS
    # ========================================================================
    
    async def get_user_courses(self, user_id: str) -> Dict[str, Any]:
        """Get all courses for a user"""
        user_courses = [
            course for course in self.user_courses.values()
            if course.get("user_id") == user_id
        ]
        
        return {
            "user_id": user_id,
            "courses": user_courses,
            "total_count": len(user_courses)
        }
    
    async def get_course_overview(self, course_id: str) -> Dict[str, Any]:
        """Get course overview and structure"""
        if course_id not in self.user_courses:
            raise ValueError(f"Course {course_id} not found")
        
        course = self.user_courses[course_id]
        
        return {
            "course_id": course_id,
            "title": course["title"],
            "description": course["description"],
            "subject": course["subject"],
            "topic": course["topic"],
            "duration_minutes": course["total_duration_minutes"],
            "total_lessons": course["total_lessons"],
            "difficulty": course["difficulty"],
            "learning_style": course["learning_style"],
            "focus": course["focus"],
            "progress": course["progress"],
            "completed": course["completed"],
            "lessons": course["lessons"],
            "created_at": course["created_at"]
        }

    # ========================================================================
    # LESSON INTERACTION ENDPOINTS
    # ========================================================================
    
    async def get_lesson(self, course_id: str, lesson_id: str) -> Dict[str, Any]:
        """Get lesson details"""
        if course_id not in self.user_courses:
            raise ValueError(f"Course {course_id} not found")
        
        course = self.user_courses[course_id]
        lesson = next((l for l in course["lessons"] if l["lesson_id"] == lesson_id), None)
        
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found in course {course_id}")
        
        return lesson
    
    async def start_lesson(self, course_id: str, lesson_id: str, user_id: str) -> Dict[str, Any]:
        """Start a learning session for a lesson"""
        lesson = await self.get_lesson(course_id, lesson_id)
        
        if lesson["status"] == "locked":
            raise ValueError(f"Lesson {lesson_id} is locked. Complete prerequisites first.")
        
        session_id = str(uuid.uuid4())
        
        # Update lesson status
        lesson["status"] = "in-progress"
        
        # Create session
        session = {
            "session_id": session_id,
            "course_id": course_id,
            "lesson_id": lesson_id,
            "user_id": user_id,
            "started_at": datetime.utcnow().isoformat(),
            "status": "active",
            "progress": 0
        }
        
        self.learning_sessions[session_id] = session
        
        return session

    async def update_lesson_progress(
        self, 
        course_id: str, 
        lesson_id: str, 
        progress: float, 
        completed: bool = False,
        answers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Update lesson progress"""
        if course_id not in self.user_courses:
            raise ValueError(f"Course {course_id} not found")
        
        course = self.user_courses[course_id]
        lesson = next((l for l in course["lessons"] if l["lesson_id"] == lesson_id), None)
        
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found")
        
        # Update lesson progress
        lesson["progress"] = progress
        lesson["completed"] = completed
        
        if completed:
            lesson["status"] = "completed"
            
            # Unlock next lesson
            lesson_index = next(
                i for i, l in enumerate(course["lessons"]) 
                if l["lesson_id"] == lesson_id
            )
            if lesson_index + 1 < len(course["lessons"]):
                course["lessons"][lesson_index + 1]["status"] = "available"
        
        # Update course progress
        completed_lessons = sum(1 for l in course["lessons"] if l["completed"])
        course["progress"] = (completed_lessons / len(course["lessons"])) * 100
        
        return {
            "lesson_id": lesson_id,
            "course_id": course_id,
            "progress": progress,
            "completed": completed,
            "course_progress": course["progress"],
            "updated_at": datetime.utcnow().isoformat()
        }

    # ========================================================================
    # ASSESSMENT ENDPOINTS
    # ========================================================================
    
    async def submit_assessment(
        self,
        course_id: str,
        lesson_id: str,
        user_id: str,
        answers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Submit assessment answers and get evaluation
        Uses assessment_system to evaluate
        """
        lesson = await self.get_lesson(course_id, lesson_id)
        
        if not lesson["assessment_questions"]:
            return {
                "lesson_id": lesson_id,
                "score": 100,
                "message": "No assessment for this lesson"
            }
        
        # TODO: Integrate with assessment_system.py for actual evaluation
        # For now, return mock evaluation
        
        correct_count = len(answers)  # Mock: assume all correct
        total_questions = len(lesson["assessment_questions"])
        score = (correct_count / total_questions * 100) if total_questions > 0 else 100
        
        result = {
            "lesson_id": lesson_id,
            "course_id": course_id,
            "score": score,
            "correct_count": correct_count,
            "total_questions": total_questions,
            "feedback": [
                "Great effort! Review any incorrect answers.",
                "Focus on practice exercises for better retention."
            ],
            "mastered_topics": lesson["learning_objectives"][:2] if score >= 80 else [],
            "knowledge_gaps": lesson["learning_objectives"][2:] if score < 80 else [],
            "recommendations": [
                "Continue to next lesson" if score >= 70 else "Review this lesson before proceeding"
            ],
            "submitted_at": datetime.utcnow().isoformat()
        }
        
        return result

    # ========================================================================
    # PROGRESS & ANALYTICS ENDPOINTS
    # ========================================================================
    
    async def get_course_progress(self, course_id: str) -> Dict[str, Any]:
        """Get overall course progress"""
        if course_id not in self.user_courses:
            raise ValueError(f"Course {course_id} not found")
        
        course = self.user_courses[course_id]
        
        completed_lessons = sum(1 for l in course["lessons"] if l["completed"])
        current_lesson = next(
            (l for l in course["lessons"] if l["status"] == "in-progress"),
            None
        )
        
        return {
            "course_id": course_id,
            "title": course["title"],
            "completion_percentage": course["progress"],
            "lessons_completed": completed_lessons,
            "total_lessons": course["total_lessons"],
            "current_lesson": current_lesson["title"] if current_lesson else None,
            "time_spent": 0,  # TODO: Calculate from sessions
            "estimated_time_remaining": course["total_duration_minutes"],
            "status": "completed" if course["completed"] else "in-progress",
            "created_at": course["created_at"]
        }

    async def get_learning_curve(self, course_id: str) -> Dict[str, Any]:
        """Get learning curve analytics"""
        if course_id not in self.user_courses:
            raise ValueError(f"Course {course_id} not found")
        
        course = self.user_courses[course_id]
        
        # TODO: Integrate with learning_curve.py for actual analytics
        # For now return mock data
        
        return {
            "course_id": course_id,
            "data_points": [
                {
                    "lesson_index": i,
                    "lesson_title": lesson["title"],
                    "score": lesson["progress"]
                }
                for i, lesson in enumerate(course["lessons"])
            ],
            "trend": "improving",
            "average_score": course["progress"],
            "learning_velocity": 5.0
        }

    # ========================================================================
    # PRACTICE ENDPOINTS
    # ========================================================================
    
    async def get_practice_questions(
        self,
        course_id: str,
        lesson_id: str,
        count: int = 5
    ) -> Dict[str, Any]:
        """Get practice questions for a lesson"""
        lesson = await self.get_lesson(course_id, lesson_id)
        
        exercises = lesson.get("practice_exercises", [])
        selected_exercises = exercises[:count]
        
        return {
            "lesson_id": lesson_id,
            "course_id": course_id,
            "total_available": len(exercises),
            "questions": [
                {
                    "id": f"q{i}",
                    "question": exercise,
                    "type": "practice",
                    "difficulty": lesson["difficulty"]
                }
                for i, exercise in enumerate(selected_exercises)
            ]
        }

    # ========================================================================
    # RECOMMENDATIONS ENDPOINTS
    # ========================================================================
    
    async def get_learning_recommendations(self, course_id: str, user_id: str) -> Dict[str, Any]:
        """Get AI-powered learning recommendations"""
        if course_id not in self.user_courses:
            raise ValueError(f"Course {course_id} not found")
        
        course = self.user_courses[course_id]
        
        # TODO: Integrate with mdp_learning.py for actual recommendations
        
        # Find lowest progress lessons
        low_progress_lessons = sorted(
            course["lessons"],
            key=lambda l: l["progress"]
        )[:3]
        
        return {
            "course_id": course_id,
            "user_id": user_id,
            "recommendations": [
                {
                    "type": "review",
                    "lesson_id": lesson["lesson_id"],
                    "lesson_title": lesson["title"],
                    "reason": "Low mastery - needs review",
                    "priority": "high"
                }
                for lesson in low_progress_lessons
                if not lesson["completed"]
            ],
            "next_best_action": "Review concepts with low mastery",
            "priority_topics": [
                lesson["title"] for lesson in low_progress_lessons
            ]
        }

    # ========================================================================
    # GAP ANALYSIS ENDPOINTS
    # ========================================================================
    
    async def analyze_knowledge_gaps(self, course_id: str, user_id: str) -> Dict[str, Any]:
        """Analyze knowledge gaps and provide remedial content"""
        if course_id not in self.user_courses:
            raise ValueError(f"Course {course_id} not found")
        
        course = self.user_courses[course_id]
        
        # TODO: Integrate with gap_analysis.py for actual gap analysis
        
        gaps = []
        for lesson in course["lessons"]:
            if lesson["progress"] < 70:
                gaps.extend(lesson["learning_objectives"])
        
        return {
            "course_id": course_id,
            "user_id": user_id,
            "identified_gaps": list(set(gaps)),
            "remedial_lessons": [
                {
                    "lesson_id": lesson["lesson_id"],
                    "title": f"Remedial: {lesson['title']}",
                    "duration": lesson["duration"] + 15,
                    "focus": "Remedial"
                }
                for lesson in course["lessons"]
                if lesson["progress"] < 70
            ],
            "estimated_remedial_time": sum(
                lesson["duration"] + 15 for lesson in course["lessons"] 
                if lesson["progress"] < 70
            ),
            "priority": "high" if len(gaps) > 5 else "medium"
        }


# Global instance for easy access
_course_creator = None

async def get_course_creator() -> InteractiveCourseCreator:
    """Get or create the InteractiveCourseCreator instance"""
    global _course_creator
    if _course_creator is None:
        _course_creator = InteractiveCourseCreator()
        await _course_creator.initialize_system()
    return _course_creator

