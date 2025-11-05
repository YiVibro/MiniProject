"""
Enhanced Tutoring System with Dynamic Lesson Generation
======================================================

This enhanced version integrates dynamic lesson generation with the existing
multi-agent tutoring system, eliminating hardcoded lessons.
"""

import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from .tutoring_system import MultiAgentTutoringSystem, SystemConfig
from models import Lesson, UserProfile, UserProgress, LearningPath
from .dynamic_lesson_generator import DynamicLessonGenerator
from .real_llm_service import RealLLMService

class EnhancedTutoringSystem(MultiAgentTutoringSystem):
    """Enhanced tutoring system with dynamic lesson generation"""
    
    def __init__(self, config: SystemConfig):
        super().__init__(config)
        
        # Override to use the real LLM service for non-mock content
        self.llm_service = RealLLMService(config.llm_api_key, config.llm_model)

        # Reinitialize core systems and agents with the real LLM
        from assessment_system import AssessmentSystem
        from gap_analysis import GapAnalysisSystem
        from knowledge_gap_filler import KnowledgeGapFiller
        from agents.knowledge_agent import KnowledgeAgent
        from agents.practice_agent import PracticeAgent
        from agents.motivation_agent import MotivationAgent
        from agents.planner_agent import PlannerAgent

        self.assessment_system = AssessmentSystem(self.llm_service)
        self.gap_analysis_system = GapAnalysisSystem(self.llm_service)
        self.knowledge_gap_filler = KnowledgeGapFiller(self.llm_service)
        self.knowledge_agent = KnowledgeAgent(self.llm_service)
        self.practice_agent = PracticeAgent(self.llm_service)
        self.motivation_agent = MotivationAgent(self.llm_service)
        self.planner_agent = PlannerAgent(self.llm_service)

        # Initialize dynamic lesson generator with real LLM
        self.lesson_generator = DynamicLessonGenerator(self.llm_service)
        
        # Enhanced lesson management
        self.dynamic_lessons = {}  # lesson_id -> Lesson (dynamically generated)
        self.lesson_adaptations = {}  # user_id -> adapted_lessons
        
    async def create_dynamic_lesson(self, 
                                  subject: str, 
                                  topic: str, 
                                  difficulty: str = "medium",
                                  user_profile: Optional[UserProfile] = None) -> Lesson:
        """Create a dynamic lesson using LLM"""
        
        print(f"🤖 Creating dynamic lesson: {topic} ({subject})")
        
        # Generate lesson using LLM
        lesson = await self.lesson_generator.generate_lesson(
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            user_profile=user_profile,
            learning_style=user_profile.learning_style if user_profile else "balanced"
        )
        
        # Store in system
        self.lessons[lesson.lesson_id] = lesson
        self.dynamic_lessons[lesson.lesson_id] = lesson
        
        print(f"✅ Dynamic lesson created: {lesson.title}")
        return lesson
    
    async def create_dynamic_curriculum(self, 
                                     subject: str, 
                                     level: str, 
                                     duration_weeks: int,
                                     user_profile: Optional[UserProfile] = None) -> List[Lesson]:
        """Create a complete dynamic curriculum"""
        
        print(f"📚 Creating dynamic curriculum: {subject} ({level}) - {duration_weeks} weeks")
        
        # Generate curriculum using LLM
        curriculum = await self.lesson_generator.generate_curriculum(
            subject=subject,
            level=level,
            duration_weeks=duration_weeks,
            user_profile=user_profile
        )
        
        # Store all lessons in system
        for lesson in curriculum:
            self.lessons[lesson.lesson_id] = lesson
            self.dynamic_lessons[lesson.lesson_id] = lesson
        
        print(f"✅ Dynamic curriculum created: {len(curriculum)} lessons")
        return curriculum
    
    async def adapt_lesson_for_user(self, 
                                  lesson_id: str, 
                                  user_id: str) -> Lesson:
        """Adapt an existing lesson for a specific user"""
        
        # Get original lesson
        original_lesson = self.lessons.get(lesson_id)
        if not original_lesson:
            raise ValueError(f"Lesson {lesson_id} not found")
        
        # Get user profile
        user_profile = self.user_profiles.get(user_id)
        if not user_profile:
            raise ValueError(f"User profile for {user_id} not found")
        
        # Get user progress
        user_progress = self.user_progress.get(user_id)
        
        print(f"🎯 Adapting lesson {lesson_id} for user {user_id}")
        
        # Adapt lesson using LLM
        adapted_lesson = await self.lesson_generator.adapt_lesson_for_user(
            lesson=original_lesson,
            user_profile=user_profile,
            user_progress=user_progress
        )
        
        # Store adapted lesson
        adapted_lesson_id = f"{lesson_id}_adapted_{user_id}"
        adapted_lesson.lesson_id = adapted_lesson_id
        self.lessons[adapted_lesson_id] = adapted_lesson
        
        # Track adaptation
        if user_id not in self.lesson_adaptations:
            self.lesson_adaptations[user_id] = []
        self.lesson_adaptations[user_id].append(adapted_lesson_id)
        
        print(f"✅ Lesson adapted for user {user_id}")
        return adapted_lesson
    
    async def create_personalized_learning_path(self, 
                                              user_id: str, 
                                              user_request: str,
                                              user_profile: Optional[UserProfile] = None) -> str:
        """Create a personalized learning path with dynamic lessons"""
        
        print(f"🎯 Creating personalized learning path for: {user_request}")
        
        # Parse user request to extract requirements
        requirements = await self._parse_user_request(user_request)
        
        # Create user profile if not provided
        if not user_profile:
            user_profile = UserProfile(
                user_id=user_id,
                name=f"User {user_id}",
                email=f"{user_id}@example.com",
                learning_style=requirements.get("learning_style", "balanced"),
                preferred_difficulty=requirements.get("current_level", "medium"),
                available_time=requirements.get("time_per_day", "2 hours").split()[0],
                learning_goals=requirements.get("goals", []),
                interests=[]
            )
            self.user_profiles[user_id] = user_profile
        
        # Generate dynamic curriculum
        curriculum = await self.create_dynamic_curriculum(
            subject=requirements["subject"],
            level=requirements["current_level"],
            duration_weeks=self._extract_weeks_from_timeline(requirements["timeline"]),
            user_profile=user_profile
        )
        
        # Create learning path
        path_id = await self.create_learning_path(
            user_id=user_id,
            goals=requirements["goals"],
            timeline=requirements["timeline"],
            preferences={
                "available_time": requirements["time_per_day"],
                "learning_style": requirements["learning_style"],
                "current_level": requirements["current_level"],
                "weekly_tests": requirements.get("weekly_tests", True),
                "adaptive_difficulty": True
            }
        )
        
        # Update learning path with dynamic lessons
        learning_path = self.learning_paths[path_id]
        learning_path.lessons = [lesson.lesson_id for lesson in curriculum]
        learning_path.description = f"Dynamic learning path for {requirements['subject']} with {len(curriculum)} personalized lessons"
        
        print(f"✅ Personalized learning path created: {path_id}")
        return path_id
    
    async def _parse_user_request(self, user_request: str) -> Dict[str, Any]:
        """Parse user request using LLM for better understanding"""
        
        prompt = f"""
        Analyze this learning request and extract structured information:
        
        User Request: "{user_request}"
        
        Extract and return in JSON format:
        {{
            "subject": "Primary subject/topic",
            "current_level": "beginner/intermediate/advanced",
            "timeline": "Duration (e.g., 3 months, 6 weeks)",
            "goals": ["Goal 1", "Goal 2", "Goal 3"],
            "time_per_day": "Available time per day",
            "learning_style": "visual/auditory/kinesthetic/analytical/practical/balanced",
            "weekly_tests": true/false,
            "project_based": true/false,
            "specific_requirements": ["Any specific requirements"]
        }}
        
        Be specific and practical in your analysis.
        """
        
        try:
            # Use LLM to parse request
            response = await self.llm_service.generate_response(prompt)
            
            # Try to extract JSON from response
            import json
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"Error parsing request with LLM: {e}")
        
        # Fallback to simple parsing
        return self._simple_parse_request(user_request)
    
    def _simple_parse_request(self, user_request: str) -> Dict[str, Any]:
        """Simple fallback parsing"""
        
        # Extract subject
        subject = "General"
        if "python" in user_request.lower():
            subject = "Python"
        elif "javascript" in user_request.lower():
            subject = "JavaScript"
        elif "machine learning" in user_request.lower() or "ml" in user_request.lower():
            subject = "Machine Learning"
        elif "web development" in user_request.lower():
            subject = "Web Development"
        elif "data science" in user_request.lower():
            subject = "Data Science"
        
        # Extract level
        level = "beginner"
        if "intermediate" in user_request.lower():
            level = "intermediate"
        elif "advanced" in user_request.lower():
            level = "advanced"
        elif "expert" in user_request.lower():
            level = "advanced"
        
        # Extract timeline
        timeline = "3 months"
        if "3 months" in user_request.lower():
            timeline = "3 months"
        elif "6 months" in user_request.lower():
            timeline = "6 months"
        elif "1 year" in user_request.lower():
            timeline = "1 year"
        elif "6 weeks" in user_request.lower():
            timeline = "6 weeks"
        
        # Extract goals
        goals = ["Master the subject", "Build practical skills"]
        if "job" in user_request.lower() or "career" in user_request.lower():
            goals.append("Prepare for job interviews")
        if "project" in user_request.lower():
            goals.append("Build real-world projects")
        if "certification" in user_request.lower():
            goals.append("Prepare for certification")
        
        return {
            "subject": subject,
            "current_level": level,
            "timeline": timeline,
            "goals": goals,
            "time_per_day": "2 hours",
            "learning_style": "balanced",
            "weekly_tests": True,
            "project_based": "project" in user_request.lower(),
            "specific_requirements": []
        }
    
    def _extract_weeks_from_timeline(self, timeline: str) -> int:
        """Extract number of weeks from timeline string"""
        if "3 months" in timeline:
            return 12
        elif "6 months" in timeline:
            return 24
        elif "1 year" in timeline:
            return 52
        elif "6 weeks" in timeline:
            return 6
        else:
            return 12  # Default
    
    async def get_adaptive_lesson(self, 
                                 user_id: str, 
                                 subject: str, 
                                 topic: str) -> Lesson:
        """Get an adaptive lesson for a user"""
        
        # Check if we have a user profile
        user_profile = self.user_profiles.get(user_id)
        user_progress = self.user_progress.get(user_id)
        
        # Determine difficulty based on user progress
        difficulty = "medium"
        if user_progress and user_progress.test_scores:
            avg_score = sum(user_progress.test_scores) / len(user_progress.test_scores)
            if avg_score >= 0.8:
                difficulty = "advanced"
            elif avg_score >= 0.6:
                difficulty = "intermediate"
            else:
                difficulty = "beginner"
        
        # Create or get existing lesson
        lesson_id = f"{subject.lower().replace(' ', '_')}_{topic.lower().replace(' ', '_')}"
        existing_lesson = self.lessons.get(lesson_id)
        
        if existing_lesson and user_profile:
            # Adapt existing lesson for user
            return await self.adapt_lesson_for_user(lesson_id, user_id)
        else:
            # Create new dynamic lesson
            return await self.create_dynamic_lesson(
                subject=subject,
                topic=topic,
                difficulty=difficulty,
                user_profile=user_profile
            )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get enhanced system status"""
        
        base_status = super().get_system_status()
        
        # Add dynamic lesson statistics
        base_status.update({
            "dynamic_lessons": len(self.dynamic_lessons),
            "lesson_adaptations": len(self.lesson_adaptations),
            "dynamic_generation_enabled": True,
            "llm_service_status": "active"
        })
        
        return base_status

# Example usage and testing
async def demo_enhanced_system():
    """Demonstrate the enhanced tutoring system"""
    
    print("🚀 Enhanced Tutoring System Demo")
    print("=" * 50)
    
    # Initialize enhanced system
    config = SystemConfig(
        llm_provider="google",
        llm_api_key="demo-key",
        llm_model="gemini-pro",
        enable_analytics=True,
        enable_gap_analysis=True,
        enable_learning_curves=True,
        enable_mdp_recommendations=True
    )
    
    system = EnhancedTutoringSystem(config)
    
    # Create a user profile
    user_profile = UserProfile(
        user_id="demo_user",
        name="Demo User",
        email="demo@example.com",
        learning_style="visual",
        preferred_difficulty="intermediate",
        available_time=60,
        learning_goals=["Learn Python programming", "Build web applications"],
        interests=["Web development", "Data science"]
    )
    
    system.user_profiles["demo_user"] = user_profile
    
    # Create dynamic lesson
    print("\n📖 Creating dynamic lesson...")
    lesson = await system.create_dynamic_lesson(
        subject="Python Programming",
        topic="Object-Oriented Programming",
        difficulty="intermediate",
        user_profile=user_profile
    )
    
    print(f"✅ Created lesson: {lesson.title}")
    print(f"📝 Content preview: {lesson.content[:200]}...")
    print(f"🎯 Learning objectives: {lesson.learning_objectives}")
    
    # Create dynamic curriculum
    print("\n📚 Creating dynamic curriculum...")
    curriculum = await system.create_dynamic_curriculum(
        subject="Machine Learning",
        level="beginner",
        duration_weeks=4,
        user_profile=user_profile
    )
    
    print(f"✅ Created curriculum: {len(curriculum)} lessons")
    for i, lesson in enumerate(curriculum[:3], 1):
        print(f"   {i}. {lesson.title}")
    
    # Create personalized learning path
    print("\n🛤️ Creating personalized learning path...")
    path_id = await system.create_personalized_learning_path(
        user_id="demo_user",
        user_request="I want to learn Python for web development in 3 months with weekly tests",
        user_profile=user_profile
    )
    
    print(f"✅ Created learning path: {path_id}")
    
    # Get system status
    print("\n📊 System Status:")
    status = system.get_system_status()
    print(f"   - Total lessons: {status['total_lessons']}")
    print(f"   - Dynamic lessons: {status['dynamic_lessons']}")
    print(f"   - Learning paths: {status['total_learning_paths']}")
    print(f"   - Dynamic generation: {status['dynamic_generation_enabled']}")
    
    print("\n🎉 Enhanced system demo completed!")

if __name__ == "__main__":
    asyncio.run(demo_enhanced_system())
