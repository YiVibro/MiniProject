#!/usr/bin/env python3
"""
Interactive Course Creator
=========================

A terminal-based application that creates dynamic courses based on user requirements
using LLM-powered lesson generation.
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from enhanced_tutoring_system import EnhancedTutoringSystem, SystemConfig
from models import UserProfile, UserProgress
from dynamic_lesson_generator import DynamicLessonGenerator

class InteractiveCourseCreator:
    """Interactive terminal application for creating dynamic courses"""
    
    def __init__(self):
        self.system = None
        self.current_user = None
        self.current_course = None
        
    async def initialize_system(self):
        """Initialize the tutoring system"""
        print("🚀 Initializing Dynamic Learning System...")
        
        config = SystemConfig(
            llm_provider="google",
            llm_api_key="demo-key",
            llm_model="gemini-pro",
            enable_analytics=True,
            enable_gap_analysis=True,
            enable_learning_curves=True,
            enable_mdp_recommendations=True
        )
        
        self.system = EnhancedTutoringSystem(config)
        print("✅ System initialized successfully!")
    
    def display_welcome(self):
        """Display welcome message"""
        print("\n" + "="*60)
        print("🎓 DYNAMIC COURSE CREATOR")
        print("="*60)
        print("Create personalized courses using AI-powered lesson generation!")
        print("No hardcoded content - everything is generated dynamically.")
        print("="*60)
    
    def get_user_profile(self) -> UserProfile:
        """Get user profile information"""
        print("\n👤 Let's create your learning profile...")
        
        name = input("📝 Your name: ").strip() or "Learner"
        email = input("📧 Your email: ").strip() or f"{name.lower()}@example.com"
        
        print("\n🎯 Learning Style (choose one):")
        print("1. Visual - Learn through diagrams, charts, and visual aids")
        print("2. Auditory - Learn through listening and verbal explanations")
        print("3. Kinesthetic - Learn through hands-on activities and movement")
        print("4. Analytical - Learn through detailed analysis and logical structure")
        print("5. Practical - Learn through real-world applications")
        print("6. Balanced - Mix of all styles")
        
        style_choice = input("Choose (1-6): ").strip()
        style_map = {
            "1": "visual", "2": "auditory", "3": "kinesthetic",
            "4": "analytical", "5": "practical", "6": "balanced"
        }
        learning_style = style_map.get(style_choice, "balanced")
        
        print("\n📊 Difficulty Level:")
        print("1. Beginner - New to the subject")
        print("2. Intermediate - Some experience")
        print("3. Advanced - Experienced learner")
        
        level_choice = input("Choose (1-3): ").strip()
        level_map = {"1": "beginner", "2": "intermediate", "3": "advanced"}
        difficulty = level_map.get(level_choice, "intermediate")
        
        time_input = input("⏰ Available time per day (minutes): ").strip()
        try:
            available_time = int(time_input) if time_input else 60
        except ValueError:
            available_time = 60
        
        goals_input = input("🎯 Learning goals (comma-separated): ").strip()
        goals = [goal.strip() for goal in goals_input.split(",")] if goals_input else ["Master the subject"]
        
        interests_input = input("💡 Areas of interest (comma-separated): ").strip()
        interests = [interest.strip() for interest in interests_input.split(",")] if interests_input else []
        
        user_id = f"user_{hash(name + email) % 10000}"
        
        profile = UserProfile(
            user_id=user_id,
            name=name,
            email=email,
            learning_style=learning_style,
            preferred_difficulty=difficulty,
            available_time=available_time,
            learning_goals=goals,
            interests=interests
        )
        
        print(f"\n✅ Profile created for {name}")
        return profile
    
    def get_course_requirements(self) -> Dict[str, Any]:
        """Get course requirements from user"""
        print("\n📚 Let's design your course...")
        
        subject = input("📖 Subject/Topic (e.g., Python, Machine Learning, Web Development): ").strip()
        if not subject:
            subject = "General Programming"
        
        print(f"\n🎯 What do you want to learn about {subject}?")
        topic = input("Specific topic or area: ").strip()
        if not topic:
            topic = "Fundamentals"
        
        print("\n⏱️ Course Duration:")
        print("1. 2 weeks (6 lessons)")
        print("2. 1 month (12 lessons)")
        print("3. 2 months (24 lessons)")
        print("4. 3 months (36 lessons)")
        print("5. 6 months (48 lessons)")
        print("6. Custom")
        
        duration_choice = input("Choose (1-6): ").strip()
        duration_map = {
            "1": 2, "2": 4, "3": 8, "4": 12, "5": 24, "6": None
        }
        weeks = duration_map.get(duration_choice)
        
        if weeks is None:  # Custom duration
            try:
                weeks = int(input("Enter number of weeks: ").strip())
            except ValueError:
                weeks = 4
        
        print("\n🎓 Course Focus:")
        print("1. Theory-focused - Deep understanding of concepts")
        print("2. Practice-focused - Hands-on exercises and projects")
        print("3. Balanced - Mix of theory and practice")
        print("4. Project-based - Build real-world projects")
        
        focus_choice = input("Choose (1-4): ").strip()
        focus_map = {
            "1": "theoretical", "2": "practical", "3": "balanced", "4": "project-based"
        }
        focus = focus_map.get(focus_choice, "balanced")
        
        assessment_pref = input("\n📝 Include assessments? (y/n): ").strip().lower() == 'y'
        
        return {
            "subject": subject,
            "topic": topic,
            "weeks": weeks,
            "focus": focus,
            "assessments": assessment_pref
        }
    
    async def create_course(self, user_profile: UserProfile, requirements: Dict[str, Any]):
        """Create a dynamic course based on requirements"""
        print(f"\n🤖 Creating your {requirements['subject']} course...")
        print("This may take a moment as we generate personalized content...")
        
        # Create user in system
        self.system.user_profiles[user_profile.user_id] = user_profile
        self.current_user = user_profile
        
        # Generate curriculum
        curriculum = await self.system.create_dynamic_curriculum(
            subject=requirements["subject"],
            level=user_profile.preferred_difficulty,
            duration_weeks=requirements["weeks"],
            user_profile=user_profile
        )
        
        # Create learning path
        path_id = await self.system.create_personalized_learning_path(
            user_id=user_profile.user_id,
            user_request=f"Learn {requirements['subject']} focusing on {requirements['topic']} with {requirements['focus']} approach",
            user_profile=user_profile
        )
        
        self.current_course = {
            "path_id": path_id,
            "curriculum": curriculum,
            "requirements": requirements
        }
        
        print(f"✅ Course created successfully!")
        return curriculum
    
    def display_course_overview(self, curriculum: List):
        """Display course overview"""
        print(f"\n📋 YOUR COURSE OVERVIEW")
        print("="*50)
        
        learning_path = self.system.learning_paths[self.current_course["path_id"]]
        
        print(f"📚 Course: {learning_path.title}")
        print(f"📝 Description: {learning_path.description}")
        print(f"⏱️ Duration: {learning_path.estimated_duration} minutes")
        print(f"📖 Lessons: {len(curriculum)}")
        print(f"🎯 Difficulty: {self.current_user.preferred_difficulty}")
        print(f"🎨 Learning Style: {self.current_user.learning_style}")
        
        print(f"\n📚 LESSON BREAKDOWN:")
        print("-"*30)
        for i, lesson in enumerate(curriculum, 1):
            print(f"{i:2d}. {lesson.title}")
            print(f"    Duration: {lesson.duration} min | Difficulty: {lesson.difficulty}")
            if lesson.learning_objectives:
                print(f"    Objectives: {lesson.learning_objectives[0]}")
            print()
    
    def display_lesson_details(self, lesson, lesson_number: int):
        """Display detailed lesson information"""
        print(f"\n📖 LESSON {lesson_number}: {lesson.title}")
        print("="*60)
        
        print(f"⏱️ Duration: {lesson.duration} minutes")
        print(f"🎯 Difficulty: {lesson.difficulty}")
        
        print(f"\n🎯 LEARNING OBJECTIVES:")
        for i, objective in enumerate(lesson.learning_objectives, 1):
            print(f"   {i}. {objective}")
        
        if lesson.prerequisites:
            print(f"\n📋 PREREQUISITES:")
            for prereq in lesson.prerequisites:
                print(f"   • {prereq}")
        
        print(f"\n📝 CONTENT PREVIEW:")
        content_preview = lesson.content[:300] + "..." if len(lesson.content) > 300 else lesson.content
        print(content_preview)
        
        if lesson.assessment_questions:
            print(f"\n❓ ASSESSMENT QUESTIONS: {len(lesson.assessment_questions)}")
            for i, question in enumerate(lesson.assessment_questions[:2], 1):
                print(f"   {i}. {question.get('question', 'Question')}")
        
        if lesson.practice_exercises:
            print(f"\n💪 PRACTICE EXERCISES: {len(lesson.practice_exercises)}")
            for i, exercise in enumerate(lesson.practice_exercises[:2], 1):
                print(f"   {i}. {exercise}")
    
    def show_course_menu(self):
        """Show course interaction menu"""
        while True:
            print(f"\n🎓 COURSE MENU")
            print("="*30)
            print("1. View course overview")
            print("2. Browse lessons")
            print("3. View specific lesson")
            print("4. Start learning session")
            print("5. Create new course")
            print("6. Exit")
            
            choice = input("\nChoose an option (1-6): ").strip()
            
            if choice == "1":
                self.display_course_overview(self.current_course["curriculum"])
            elif choice == "2":
                self.browse_lessons()
            elif choice == "3":
                self.view_specific_lesson()
            elif choice == "4":
                self.start_learning_session()
            elif choice == "5":
                return "new_course"
            elif choice == "6":
                return "exit"
            else:
                print("❌ Invalid choice. Please try again.")
    
    def browse_lessons(self):
        """Browse through lessons"""
        curriculum = self.current_course["curriculum"]
        
        print(f"\n📚 LESSON BROWSER")
        print("="*30)
        
        for i, lesson in enumerate(curriculum, 1):
            print(f"{i:2d}. {lesson.title}")
            print(f"    Duration: {lesson.duration} min | Difficulty: {lesson.difficulty}")
            print()
        
        print("Enter lesson number to view details, or 'back' to return to menu.")
        choice = input("Choice: ").strip()
        
        if choice.lower() == 'back':
            return
        
        try:
            lesson_num = int(choice)
            if 1 <= lesson_num <= len(curriculum):
                self.display_lesson_details(curriculum[lesson_num - 1], lesson_num)
            else:
                print("❌ Invalid lesson number.")
        except ValueError:
            print("❌ Please enter a valid number.")
    
    def view_specific_lesson(self):
        """View a specific lesson"""
        curriculum = self.current_course["curriculum"]
        
        try:
            lesson_num = int(input(f"Enter lesson number (1-{len(curriculum)}): ").strip())
            if 1 <= lesson_num <= len(curriculum):
                self.display_lesson_details(curriculum[lesson_num - 1], lesson_num)
            else:
                print("❌ Invalid lesson number.")
        except ValueError:
            print("❌ Please enter a valid number.")
    
    async def start_learning_session(self):
        """Start a learning session"""
        curriculum = self.current_course["curriculum"]
        
        print(f"\n🎯 START LEARNING SESSION")
        print("="*40)
        
        try:
            lesson_num = int(input(f"Which lesson to start with (1-{len(curriculum)}): ").strip())
            if 1 <= lesson_num <= len(curriculum):
                lesson = curriculum[lesson_num - 1]
                
                print(f"\n🚀 Starting session for: {lesson.title}")
                print("Session features:")
                print("• Interactive explanations")
                print("• Adaptive content")
                print("• Real-time feedback")
                print("• Progress tracking")
                
                # Start actual learning session
                session_id = await self.system.start_learning_session(
                    self.current_user.user_id, 
                    lesson.lesson_id
                )
                
                print(f"✅ Session started: {session_id}")
                print("🎓 Happy learning!")
                
            else:
                print("❌ Invalid lesson number.")
        except ValueError:
            print("❌ Please enter a valid number.")
    
    async def run(self):
        """Main application loop"""
        self.display_welcome()
        
        # Initialize system
        await self.initialize_system()
        
        while True:
            try:
                # Get user profile
                user_profile = self.get_user_profile()
                
                # Get course requirements
                requirements = self.get_course_requirements()
                
                # Create course
                curriculum = await self.create_course(user_profile, requirements)
                
                # Display course overview
                self.display_course_overview(curriculum)
                
                # Show course menu
                menu_result = self.show_course_menu()
                
                if menu_result == "exit":
                    print("\n👋 Thank you for using the Dynamic Course Creator!")
                    print("🎓 Happy learning!")
                    break
                elif menu_result == "new_course":
                    print("\n🔄 Creating a new course...")
                    continue
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                print("Please try again.")

async def main():
    """Main function"""
    app = InteractiveCourseCreator()
    await app.run()

if __name__ == "__main__":
    print("🎓 Starting Dynamic Course Creator...")
    asyncio.run(main())
