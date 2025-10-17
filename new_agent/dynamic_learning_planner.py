"""
Dynamic Learning Planner - Real-time Plan Creation and Progress Tracking
========================================================================

This system creates personalized learning plans dynamically based on user requests
and continuously tracks progress to adapt the learning path.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from tutoring_system import MultiAgentTutoringSystem, SystemConfig
from models import Lesson, UserProgress, LearningPath
from dynamic_lesson_generator import DynamicLessonGenerator

class DynamicLearningPlanner:
    """Dynamic learning planner that creates and adapts plans based on user requests"""
    
    def __init__(self):
        # Initialize system
        config = SystemConfig(
            llm_provider="google",
            llm_api_key="AIzaSyCKe9J2cwEzVnsp-MNU-xJxf255_hWAVzE",
            llm_model="gemini-pro",
            enable_analytics=True,
            enable_gap_analysis=True,
            enable_learning_curves=True,
            enable_mdp_recommendations=True
        )
        
        self.system = MultiAgentTutoringSystem(config)
        self.lesson_generator = DynamicLessonGenerator(self.system.llm_service)
        self.active_plans = {}  # user_id -> current_plan
        self.user_requests = {}  # user_id -> request_history
        self.progress_tracking = {}  # user_id -> progress_data
        
    async def create_learning_plan(self, user_id: str, user_request: str) -> Dict[str, Any]:
        """Create a dynamic learning plan based on user request"""
        
        print(f"🎯 Creating personalized learning plan for: {user_request}")
        print("=" * 60)
        
        # Parse user request to extract requirements
        requirements = await self._parse_user_request(user_request)
        
        # Create comprehensive curriculum based on requirements
        curriculum = await self._generate_curriculum(requirements)
        
        # Add lessons to system
        for lesson in curriculum:
            self.system.lessons[lesson.lesson_id] = lesson
        
        # Create learning path
        path_id = await self.system.create_learning_path(
            user_id,
            requirements["goals"],
            requirements["timeline"],
            {
                "available_time": requirements["time_per_day"],
                "learning_style": requirements["learning_style"],
                "current_level": requirements["current_level"],
                "weekly_tests": requirements["weekly_tests"],
                "adaptive_difficulty": True
            }
        )
        
        # Store active plan
        self.active_plans[user_id] = {
            "path_id": path_id,
            "requirements": requirements,
            "curriculum": curriculum,
            "created_at": datetime.now(),
            "current_week": 1,
            "weekly_scores": [],
            "completed_lessons": [],
            "next_topics": []
        }
        
        # Initialize user progress tracking
        self.progress_tracking[user_id] = {
            "total_time_spent": 0,
            "lessons_completed": 0,
            "assessments_taken": 0,
            "average_score": 0.0,
            "learning_velocity": 0.0,
            "strengths": [],
            "weaknesses": [],
            "recommendations": []
        }
        
        print(f"✅ Learning plan created successfully!")
        print(f"📋 Path ID: {path_id}")
        print(f"📚 Curriculum: {len(curriculum)} lessons")
        print(f"⏱️ Timeline: {requirements['timeline']}")
        print(f"🎯 Goals: {', '.join(requirements['goals'])}")
        
        return {
            "path_id": path_id,
            "requirements": requirements,
            "curriculum": [{"id": l.lesson_id, "title": l.title, "difficulty": l.difficulty} for l in curriculum],
            "timeline": requirements["timeline"],
            "goals": requirements["goals"]
        }
    
    async def _parse_user_request(self, user_request: str) -> Dict[str, Any]:
        """Parse user request to extract learning requirements"""
        
        # Use LLM to analyze the request
        prompt = f"""
        Analyze this learning request and extract key information:
        
        User Request: "{user_request}"
        
        Extract:
        1. Subject/Topic (e.g., Python, Machine Learning, Web Development)
        2. Current Level (beginner, intermediate, advanced)
        3. Timeline (e.g., 3 months, 6 weeks, 1 year)
        4. Goals (what they want to achieve)
        5. Time per day (e.g., 1 hour, 2 hours)
        6. Learning style (visual, practical, theoretical, balanced)
        7. Assessment preferences (weekly tests, projects, etc.)
        8. Specific requirements or constraints
        
        Format as structured requirements.
        """
        
        # For demo purposes, we'll use a mock analysis
        # In production, this would use the actual LLM service
        requirements = self._mock_parse_request(user_request)
        
        return requirements
    
    def _mock_parse_request(self, user_request: str) -> Dict[str, Any]:
        """Mock request parsing for demo purposes"""
        
        # Extract subject
        subject = "Python"
        if "python" in user_request.lower():
            subject = "Python"
        elif "javascript" in user_request.lower():
            subject = "JavaScript"
        elif "machine learning" in user_request.lower() or "ml" in user_request.lower():
            subject = "Machine Learning"
        elif "web development" in user_request.lower():
            subject = "Web Development"
        
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
        
        # Extract level
        level = "beginner"
        if "intermediate" in user_request.lower():
            level = "intermediate"
        elif "advanced" in user_request.lower():
            level = "advanced"
        elif "expert" in user_request.lower():
            level = "expert"
        
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
            "learning_style": "practical",
            "weekly_tests": True,
            "adaptive_difficulty": True,
            "project_based": "project" in user_request.lower()
        }
    
    async def _generate_curriculum(self, requirements: Dict[str, Any]) -> List[Lesson]:
        """Generate curriculum based on requirements using dynamic LLM generation"""
        
        subject = requirements["subject"]
        level = requirements["current_level"]
        timeline = requirements["timeline"]
        
        # Calculate number of weeks based on timeline
        weeks = self._extract_weeks_from_timeline(timeline)
        
        print(f"🤖 Generating dynamic curriculum for {subject} ({level}) - {weeks} weeks")
        
        # Use dynamic lesson generator to create curriculum
        curriculum = await self.lesson_generator.generate_curriculum(
            subject=subject,
            level=level,
            duration_weeks=weeks
        )
        
        print(f"✅ Generated {len(curriculum)} dynamic lessons")
        return curriculum
    
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
    
    # Note: Hardcoded curriculum methods removed - now using dynamic LLM generation
    
    async def track_progress(self, user_id: str, activity: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Track user progress and update learning plan"""
        
        if user_id not in self.active_plans:
            return {"error": "No active learning plan found for user"}
        
        plan = self.active_plans[user_id]
        progress = self.progress_tracking[user_id]
        
        # Update progress based on activity
        if activity == "lesson_completed":
            progress["lessons_completed"] += 1
            progress["total_time_spent"] += data.get("time_spent", 0)
            plan["completed_lessons"].append(data.get("lesson_id"))
            
        elif activity == "assessment_taken":
            score = data.get("score", 0)
            progress["assessments_taken"] += 1
            plan["weekly_scores"].append(score)
            
            # Update average score
            total_score = sum(plan["weekly_scores"])
            progress["average_score"] = total_score / len(plan["weekly_scores"])
            
        elif activity == "time_spent":
            progress["total_time_spent"] += data.get("time_spent", 0)
        
        # Analyze progress and generate recommendations
        recommendations = await self._analyze_progress(plan, progress)
        progress["recommendations"] = recommendations
        
        # Update learning plan if needed
        await self._adapt_learning_plan(user_id, plan, progress)
        
        return {
            "progress": progress,
            "plan_status": {
                "current_week": plan["current_week"],
                "completed_lessons": len(plan["completed_lessons"]),
                "weekly_scores": plan["weekly_scores"],
                "next_topics": plan["next_topics"]
            },
            "recommendations": recommendations
        }
    
    async def _analyze_progress(self, plan: Dict[str, Any], progress: Dict[str, Any]) -> List[str]:
        """Analyze user progress and generate recommendations"""
        
        recommendations = []
        
        # Analyze performance trends
        if progress["average_score"] >= 85:
            recommendations.append("Excellent performance! Consider advanced topics")
            recommendations.append("Start building portfolio projects")
        elif progress["average_score"] >= 70:
            recommendations.append("Good progress! Continue with current pace")
            recommendations.append("Focus on areas where you scored lower")
        else:
            recommendations.append("Review fundamental concepts")
            recommendations.append("Practice more with coding exercises")
        
        # Analyze learning velocity
        if progress["lessons_completed"] > 0:
            velocity = progress["total_time_spent"] / progress["lessons_completed"]
            if velocity < 30:  # Less than 30 minutes per lesson
                recommendations.append("Consider spending more time on each lesson")
            elif velocity > 120:  # More than 2 hours per lesson
                recommendations.append("Great dedication! Consider advanced challenges")
        
        # Analyze consistency
        if len(plan["weekly_scores"]) >= 3:
            recent_scores = plan["weekly_scores"][-3:]
            if all(score >= 80 for score in recent_scores):
                recommendations.append("Consistent high performance! Ready for next level")
            elif any(score < 60 for score in recent_scores):
                recommendations.append("Focus on weak areas identified in recent tests")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def _adapt_learning_plan(self, user_id: str, plan: Dict[str, Any], progress: Dict[str, Any]):
        """Adapt learning plan based on progress"""
        
        # Determine next topics based on performance
        if progress["average_score"] >= 85:
            # High performance - add advanced topics
            plan["next_topics"] = self._get_advanced_topics(plan["requirements"]["subject"])
        elif progress["average_score"] >= 70:
            # Good performance - continue with planned topics
            plan["next_topics"] = self._get_next_planned_topics(plan)
        else:
            # Low performance - add review topics
            plan["next_topics"] = self._get_review_topics(plan)
        
        # Update current week
        if len(plan["weekly_scores"]) > 0 and len(plan["weekly_scores"]) % 4 == 0:
            plan["current_week"] += 1
    
    def _get_advanced_topics(self, subject: str) -> List[str]:
        """Get advanced topics for high-performing students"""
        # Return actual advanced lesson IDs from curriculum
        if subject == "Python":
            return ["python_advanced_001", "python_advanced_002", "python_advanced_003"]
        else:
            return [f"{subject.lower().replace(' ', '_')}_advanced_{i+1:03d}" for i in range(3)]
    
    def _get_next_planned_topics(self, plan: Dict[str, Any]) -> List[str]:
        """Get next planned topics"""
        curriculum = plan["curriculum"]
        completed = len(plan["completed_lessons"])
        return [lesson.lesson_id for lesson in curriculum[completed:completed+3]]
    
    def _get_review_topics(self, plan: Dict[str, Any]) -> List[str]:
        """Get review topics for struggling students"""
        # Return actual lesson IDs for review, not "Review" prefixed strings
        completed = plan["completed_lessons"]
        if len(completed) >= 3:
            return completed[-3:]  # Last 3 completed lessons
        else:
            return completed  # All completed lessons
    
    async def get_learning_plan_status(self, user_id: str) -> Dict[str, Any]:
        """Get current status of user's learning plan"""
        
        if user_id not in self.active_plans:
            return {"error": "No active learning plan found"}
        
        plan = self.active_plans[user_id]
        progress = self.progress_tracking[user_id]
        
        return {
            "plan_id": plan["path_id"],
            "created_at": plan["created_at"],
            "current_week": plan["current_week"],
            "progress": progress,
            "next_topics": plan["next_topics"],
            "completed_lessons": len(plan["completed_lessons"]),
            "weekly_scores": plan["weekly_scores"],
            "recommendations": progress["recommendations"]
        }
    
    async def simulate_learning_session(self, user_id: str, week: int) -> Dict[str, Any]:
        """Simulate a learning session for demonstration"""
        
        if user_id not in self.active_plans:
            return {"error": "No active learning plan found"}
        
        plan = self.active_plans[user_id]
        
        print(f"\n📚 Week {week} - Learning Session")
        print("-" * 40)
        
        # Get topics for this week
        if plan["next_topics"]:
            topics = plan["next_topics"][:3]
        else:
            # Use actual lesson IDs from curriculum
            curriculum = plan["curriculum"]
            start_idx = len(plan["completed_lessons"])
            topics = [lesson.lesson_id for lesson in curriculum[start_idx:start_idx+3]]
        
        # Start learning session
        session_id = await self.system.start_learning_session(user_id, topics[0])
        
        # Simulate learning activities
        for i, topic in enumerate(topics):
            print(f"📖 Learning {topic}")
            
            # Get explanation
            explanation = await self.system.process_user_interaction(
                session_id,
                "concept_explanation_requested",
                {
                    "concept": topic,
                    "difficulty": plan["requirements"]["current_level"],
                    "learning_style": plan["requirements"]["learning_style"]
                }
            )
            
            # Track lesson completion
            await self.track_progress(user_id, "lesson_completed", {
                "lesson_id": topic,
                "time_spent": 45
            })
        
        # Take weekly test
        print(f"\n📝 Week {week} - Weekly Test")
        test_score = 60 + (week * 2) + (10 if week > 4 else 0)  # Simulated improvement
        
        # Track assessment
        await self.track_progress(user_id, "assessment_taken", {
            "score": test_score,
            "time_spent": 30
        })
        
        print(f"📊 Test Score: {test_score:.1f}%")
        
        # End session
        await self.system.end_learning_session(session_id)
        
        return {
            "week": week,
            "topics_covered": topics,
            "test_score": test_score,
            "time_spent": 45 * len(topics) + 30
        }

async def demo_dynamic_learning():
    """Demonstrate dynamic learning plan creation and progress tracking"""
    
    print("🚀 Dynamic Learning Planner Demo")
    print("=" * 50)
    
    # Initialize planner
    planner = DynamicLearningPlanner()
    
    # Example user requests
    user_requests = [
        "I want to learn Python for 3 months with weekly tests",
        "I need to master JavaScript in 6 weeks for a job interview",
        "I want to learn Machine Learning for 6 months with projects",
        "I need to become a web developer in 1 year"
    ]
    
    for i, request in enumerate(user_requests, 1):
        print(f"\n🎯 Example {i}: {request}")
        print("-" * 50)
        
        user_id = f"user_{i:03d}"
        
        # Create learning plan
        plan = await planner.create_learning_plan(user_id, request)
        
        # Simulate 4 weeks of learning
        for week in range(1, 5):
            session_result = await planner.simulate_learning_session(user_id, week)
            
            # Get progress status
            status = await planner.get_learning_plan_status(user_id)
            
            print(f"   Week {week}: Score {session_result['test_score']:.1f}%, "
                  f"Lessons: {status['completed_lessons']}, "
                  f"Avg: {status['progress']['average_score']:.1f}%")
        
        print(f"✅ Plan completed for {user_id}")
        print(f"📊 Final stats: {status['completed_lessons']} lessons, "
              f"Avg score: {status['progress']['average_score']:.1f}%")
        print(f"💡 Recommendations: {len(status['progress']['recommendations'])} suggestions")

async def interactive_demo():
    """Interactive demo where user can make requests"""
    
    print("🎮 Interactive Learning Planner Demo")
    print("=" * 50)
    print("Enter your learning request (or 'quit' to exit):")
    
    planner = DynamicLearningPlanner()
    user_id = "interactive_user"
    
    while True:
        try:
            user_request = input("\n🎯 Your learning request: ").strip()
            
            if user_request.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_request:
                continue
            
            # Create learning plan
            print(f"\n🔄 Processing: {user_request}")
            plan = await planner.create_learning_plan(user_id, user_request)
            
            # Simulate a few weeks
            print(f"\n📚 Simulating learning progress...")
            for week in range(1, 4):
                session_result = await planner.simulate_learning_session(user_id, week)
                status = await planner.get_learning_plan_status(user_id)
                
                print(f"   Week {week}: Score {session_result['test_score']:.1f}%, "
                      f"Lessons completed: {status['completed_lessons']}")
            
            # Show final status
            final_status = await planner.get_learning_plan_status(user_id)
            print(f"\n📊 Final Results:")
            print(f"   - Lessons completed: {final_status['completed_lessons']}")
            print(f"   - Average score: {final_status['progress']['average_score']:.1f}%")
            print(f"   - Time spent: {final_status['progress']['total_time_spent']} minutes")
            print(f"   - Recommendations: {len(final_status['progress']['recommendations'])}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Main demo function"""
    
    print("🎓 Dynamic Learning Planner - Real-time Plan Creation & Progress Tracking")
    print("=" * 80)
    print("This system creates personalized learning plans based on user requests")
    print("and continuously tracks progress to adapt the learning path.")
    print()
    
    # Run demo
    await demo_dynamic_learning()
    
    print(f"\n🎉 Demo completed successfully!")
    print("The system can dynamically create learning plans and track progress!")

if __name__ == "__main__":
    asyncio.run(main())
