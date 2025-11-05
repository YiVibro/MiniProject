"""
Dynamic Lesson Generator - LLM-Powered Lesson Creation
=====================================================

This module provides dynamic lesson generation using LLM services,
eliminating the need for hardcoded lessons and enabling truly
adaptive content creation.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from new_agent.models import Lesson, UserProfile, UserProgress
from new_agent.llm_service import BaseLLMService, LLMServiceFactory

class DynamicLessonGenerator:
    """Dynamic lesson generator using LLM services"""
    
    def __init__(self, llm_service: BaseLLMService):
        self.llm_service = llm_service
        self.generated_lessons = {}  # Cache for generated lessons
        self.lesson_templates = {}  # Templates for different subjects
        
    async def generate_lesson(self, 
                            subject: str, 
                            topic: str, 
                            difficulty: str = "medium",
                            user_profile: Optional[UserProfile] = None,
                            learning_style: str = "balanced",
                            duration: int = 45) -> Lesson:
        """Generate a complete lesson using LLM"""
        
        print(f"🎯 Generating dynamic lesson: {topic} ({subject})")
        
        # Create lesson ID
        lesson_id = f"{subject.lower().replace(' ', '_')}_{topic.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        
        # Generate lesson content using LLM
        lesson_data = await self._generate_lesson_content(
            subject, topic, difficulty, user_profile, learning_style, duration
        )
        
        # Create lesson object
        lesson = Lesson(
            lesson_id=lesson_id,
            title=lesson_data["title"],
            content=lesson_data["content"],
            difficulty=difficulty,
            duration=duration,
            learning_objectives=lesson_data["learning_objectives"],
            prerequisites=lesson_data["prerequisites"],
            assessment_questions=lesson_data["assessment_questions"],
            practice_exercises=lesson_data["practice_exercises"]
        )
        
        # Cache the lesson
        self.generated_lessons[lesson_id] = lesson
        
        print(f"✅ Generated lesson: {lesson.title}")
        return lesson
    
    async def _generate_lesson_content(self, 
                                     subject: str, 
                                     topic: str, 
                                     difficulty: str,
                                     user_profile: Optional[UserProfile],
                                     learning_style: str,
                                     duration: int) -> Dict[str, Any]:
        """Generate comprehensive lesson content using LLM (structured first, fallback to parsing)."""
        
        prompt = self._create_lesson_generation_prompt(
            subject, topic, difficulty, user_profile, learning_style, duration
        )
        
        # Directly ask for free-form content then parse, to avoid placeholder structured data
        response = await self.llm_service.generate_response(prompt)
        return await self._parse_lesson_response(response, topic, difficulty)
    
    def _create_lesson_generation_prompt(self, 
                                       subject: str, 
                                       topic: str, 
                                       difficulty: str,
                                       user_profile: Optional[UserProfile],
                                       learning_style: str,
                                       duration: int) -> str:
        """Create a comprehensive prompt for lesson generation"""
        
        # Base prompt structure
        prompt = f"""
        Create a comprehensive {duration}-minute lesson on "{topic}" in the subject of {subject}.
        
        DIFFICULTY LEVEL: {difficulty.upper()}
        LEARNING STYLE: {learning_style.upper()}
        DURATION: {duration} minutes
        
        """
        
        # Add user profile information if available
        if user_profile:
            prompt += f"""
        USER PROFILE:
        - Learning Style: {user_profile.learning_style}
        - Preferred Difficulty: {user_profile.preferred_difficulty}
        - Available Time: {user_profile.available_time} minutes per day
        - Learning Goals: {', '.join(user_profile.learning_goals)}
        - Interests: {', '.join(user_profile.interests)}
        
        """
        
        # Detailed lesson requirements
        prompt += f"""
        LESSON REQUIREMENTS:
        
        1. TITLE: Create an engaging, descriptive title for the lesson
        
        2. CONTENT: Provide comprehensive educational content that includes:
           - Clear introduction and overview
           - Key concepts and principles
           - Detailed explanations with examples
           - Step-by-step instructions where applicable
           - Real-world applications and use cases
           - Common pitfalls and how to avoid them
           - Visual aids suggestions (diagrams, charts, etc.)
        
        3. LEARNING OBJECTIVES: List 3-5 specific, measurable learning objectives
        
        4. PREREQUISITES: List any required prior knowledge or skills
        
        5. ASSESSMENT QUESTIONS: Create 5-7 questions including:
           - Multiple choice questions
           - Short answer questions
           - Practical application questions
           - Problem-solving scenarios
        
        6. PRACTICE EXERCISES: Provide 3-5 hands-on exercises with:
           - Clear instructions
           - Expected outcomes
           - Difficulty progression
           - Self-assessment criteria
        
        ADAPTATION GUIDELINES:
        - For VISUAL learners: Include diagrams, charts, and visual examples
        - For AUDITORY learners: Focus on explanations and verbal descriptions
        - For KINESTHETIC learners: Emphasize hands-on activities and movement
        - For ANALYTICAL learners: Provide detailed breakdowns and logical structures
        - For PRACTICAL learners: Focus on real-world applications and examples
        
        DIFFICULTY ADAPTATIONS:
        - BEGINNER: Use simple language, basic concepts, lots of examples
        - INTERMEDIATE: Balance theory and practice, moderate complexity
        - ADVANCED: Complex concepts, advanced applications, critical thinking
        
        Please structure your response as a comprehensive lesson plan that can be directly used for teaching.
        """
        
        return prompt
    
    async def _parse_lesson_response(self, response: str, topic: str, difficulty: str) -> Dict[str, Any]:
        """Parse LLM response into structured lesson data"""
        
        # Extract title
        title = self._extract_title(response, topic)
        
        # Extract content
        content = self._extract_content(response)
        
        # Extract learning objectives
        objectives = self._extract_learning_objectives(response)
        
        # Extract prerequisites
        prerequisites = self._extract_prerequisites(response)
        
        # Extract assessment questions
        assessment_questions = self._extract_assessment_questions(response)
        
        # Extract practice exercises
        practice_exercises = self._extract_practice_exercises(response)
        
        return {
            "title": title,
            "content": content,
            "learning_objectives": objectives,
            "prerequisites": prerequisites,
            "assessment_questions": assessment_questions,
            "practice_exercises": practice_exercises
        }
    
    def _extract_title(self, response: str, topic: str) -> str:
        """Extract lesson title from response"""
        lines = response.split('\n')
        for line in lines:
            if 'TITLE:' in line.upper() or 'LESSON TITLE:' in line.upper():
                return line.split(':', 1)[1].strip()
            elif line.strip() and not line.startswith('#') and not line.startswith('*') and not line.startswith('A)') and not line.startswith('B)'):
                # Use first meaningful line as title
                return line.strip()
        return f"Introduction to {topic}"
    
    def _extract_content(self, response: str) -> str:
        """Extract main content from response"""
        # Look for content sections
        content_sections = []
        lines = response.split('\n')
        in_content = False
        
        for line in lines:
            if 'CONTENT:' in line.upper() or 'LESSON CONTENT:' in line.upper():
                in_content = True
                continue
            elif in_content and (line.startswith('LEARNING OBJECTIVES:') or 
                               line.startswith('ASSESSMENT:') or 
                               line.startswith('PRACTICE:')):
                break
            elif in_content and line.strip():
                content_sections.append(line)
        
        if content_sections:
            return '\n'.join(content_sections)
        else:
            # Fallback: use the entire response as content
            return response
    
    def _extract_learning_objectives(self, response: str) -> List[str]:
        """Extract learning objectives from response"""
        objectives = []
        lines = response.split('\n')
        in_objectives = False
        
        for line in lines:
            if 'LEARNING OBJECTIVES:' in line.upper() or 'OBJECTIVES:' in line.upper():
                in_objectives = True
                continue
            elif in_objectives and (line.startswith('PREREQUISITES:') or 
                                  line.startswith('ASSESSMENT:') or 
                                  line.startswith('PRACTICE:')):
                break
            elif in_objectives and line.strip():
                # Clean up objective text
                objective = line.strip()
                if objective.startswith('-') or objective.startswith('*') or objective.startswith('•'):
                    objective = objective[1:].strip()
                if objective.startswith(('1.', '2.', '3.', '4.', '5.')):
                    objective = objective[2:].strip()
                if objective:
                    objectives.append(objective)
        
        # Fallback objectives if none found
        if not objectives:
            objectives = [
                f"Understand the basic concepts of the topic",
                f"Apply the concepts in practical scenarios",
                f"Demonstrate mastery through assessment"
            ]
        
        return objectives[:5]  # Limit to 5 objectives
    
    def _extract_prerequisites(self, response: str) -> List[str]:
        """Extract prerequisites from response"""
        prerequisites = []
        lines = response.split('\n')
        in_prerequisites = False
        
        for line in lines:
            if 'PREREQUISITES:' in line.upper() or 'REQUIRED KNOWLEDGE:' in line.upper():
                in_prerequisites = True
                continue
            elif in_prerequisites and (line.startswith('ASSESSMENT:') or 
                                     line.startswith('PRACTICE:') or
                                     line.startswith('LEARNING OBJECTIVES:')):
                break
            elif in_prerequisites and line.strip():
                prereq = line.strip()
                if prereq.startswith('-') or prereq.startswith('*') or prereq.startswith('•'):
                    prereq = prereq[1:].strip()
                if prereq:
                    prerequisites.append(prereq)
        
        return prerequisites[:3]  # Limit to 3 prerequisites
    
    def _extract_assessment_questions(self, response: str) -> List[Dict[str, Any]]:
        """Extract assessment questions from response"""
        questions = []
        lines = response.split('\n')
        in_questions = False
        current_question = None
        
        for line in lines:
            if 'ASSESSMENT' in line.upper() or 'QUESTIONS:' in line.upper():
                in_questions = True
                continue
            elif in_questions and (line.startswith('PRACTICE:') or 
                                 line.startswith('EXERCISES:')):
                break
            elif in_questions and line.strip():
                # Check if this is a new question
                if (line.startswith(('Q', 'Question')) or 
                    line.startswith(('1.', '2.', '3.', '4.', '5.')) or
                    '?' in line):
                    
                    # Save previous question
                    if current_question:
                        questions.append(current_question)
                    
                    # Start new question
                    current_question = {
                        "question": line.strip(),
                        "type": "multiple_choice",
                        "options": [],
                        "correct_answer": "",
                        "explanation": ""
                    }
                elif current_question:
                    # Add to current question
                    if line.startswith(('A)', 'B)', 'C)', 'D)')):
                        current_question["options"].append(line.strip())
                    elif line.startswith("Answer:"):
                        current_question["correct_answer"] = line.replace("Answer:", "").strip()
                    elif line.startswith("Explanation:"):
                        current_question["explanation"] = line.replace("Explanation:", "").strip()
        
        # Add final question
        if current_question:
            questions.append(current_question)
        
        # Generate fallback questions if none found
        if not questions:
            questions = [
                {
                    "question": f"What is the main concept of this topic?",
                    "type": "short_answer",
                    "correct_answer": "The main concept is...",
                    "explanation": "This question tests basic understanding."
                },
                {
                    "question": f"How would you apply this concept in practice?",
                    "type": "short_answer", 
                    "correct_answer": "In practice, this concept can be applied by...",
                    "explanation": "This question tests practical application."
                }
            ]
        
        return questions[:7]  # Limit to 7 questions
    
    def _extract_practice_exercises(self, response: str) -> List[str]:
        """Extract practice exercises from response"""
        exercises = []
        lines = response.split('\n')
        in_exercises = False
        
        for line in lines:
            if 'PRACTICE:' in line.upper() or 'EXERCISES:' in line.upper():
                in_exercises = True
                continue
            elif in_exercises and line.strip():
                exercise = line.strip()
                if exercise.startswith('-') or exercise.startswith('*') or exercise.startswith('•'):
                    exercise = exercise[1:].strip()
                if exercise.startswith(('1.', '2.', '3.', '4.', '5.')):
                    exercise = exercise[2:].strip()
                if exercise:
                    exercises.append(exercise)
        
        # Fallback exercises if none found
        if not exercises:
            exercises = [
                "Practice the basic concepts with simple examples",
                "Apply the concepts to solve practical problems",
                "Create your own examples to demonstrate understanding"
            ]
        
        return exercises[:5]  # Limit to 5 exercises
    
    async def generate_curriculum(self, 
                                subject: str, 
                                level: str, 
                                duration_weeks: int,
                                user_profile: Optional[UserProfile] = None) -> List[Lesson]:
        """Generate a complete curriculum using LLM"""
        
        print(f"📚 Generating {duration_weeks}-week curriculum for {subject} ({level})")
        
        # Generate curriculum outline
        curriculum_outline = await self._generate_curriculum_outline(
            subject, level, duration_weeks, user_profile
        )
        
        # Generate lessons for each topic
        lessons = []
        for i, topic in enumerate(curriculum_outline):
            lesson = await self.generate_lesson(
                subject=subject,
                topic=topic,
                difficulty=level,
                user_profile=user_profile,
                learning_style=user_profile.learning_style if user_profile else "balanced",
                duration=45 + (i * 5)  # Increasing duration
            )
            lessons.append(lesson)
        
        print(f"✅ Generated {len(lessons)} lessons for {subject} curriculum")
        return lessons
    
    async def _generate_curriculum_outline(self, 
                                         subject: str, 
                                         level: str, 
                                         duration_weeks: int,
                                         user_profile: Optional[UserProfile]) -> List[str]:
        """Generate curriculum outline using LLM"""
        
        prompt = f"""
        Create a {duration_weeks}-week curriculum outline for {subject} at {level} level.
        
        """
        
        if user_profile:
            prompt += f"""
        USER PROFILE:
        - Learning Goals: {', '.join(user_profile.learning_goals)}
        - Interests: {', '.join(user_profile.interests)}
        - Available Time: {user_profile.available_time} minutes per day
        
        """
        
        prompt += f"""
        REQUIREMENTS:
        - Create {duration_weeks * 3} topics (3 topics per week)
        - Progress from basic to advanced concepts
        - Include practical applications
        - Ensure logical progression
        - Consider {level} level complexity
        
        FORMAT: Provide a simple list of topics, one per line.
        Example:
        Week 1: Introduction to Basics
        Week 1: Core Concepts
        Week 1: First Applications
        Week 2: Intermediate Topics
        ...
        
        Focus on creating a logical learning progression that builds upon previous knowledge.
        """
        
        response = await self.llm_service.generate_response(prompt)
        
        # Parse topics from response
        topics = []
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('*'):
                # Extract topic from line
                if ':' in line:
                    topic = line.split(':', 1)[1].strip()
                else:
                    topic = line
                if topic:
                    topics.append(topic)
        
        # Fallback topics if none found
        if not topics:
            topics = [
                f"Introduction to {subject}",
                f"Basic Concepts of {subject}",
                f"Intermediate {subject} Topics",
                f"Advanced {subject} Applications",
                f"Practical {subject} Projects"
            ]
        
        return topics[:duration_weeks * 3]  # Limit to requested number
    
    async def adapt_lesson_for_user(self, 
                                 lesson: Lesson, 
                                 user_profile: UserProfile,
                                 user_progress: Optional[UserProgress] = None) -> Lesson:
        """Adapt an existing lesson for a specific user"""
        
        print(f"🎯 Adapting lesson for user: {user_profile.user_id}")
        
        # Create adaptation prompt
        prompt = f"""
        Adapt this lesson for a specific user profile:
        
        LESSON: {lesson.title}
        CONTENT: {lesson.content[:500]}...
        
        USER PROFILE:
        - Learning Style: {user_profile.learning_style}
        - Preferred Difficulty: {user_profile.preferred_difficulty}
        - Available Time: {user_profile.available_time} minutes
        - Learning Goals: {', '.join(user_profile.learning_goals)}
        - Interests: {', '.join(user_profile.interests)}
        
        """
        
        if user_progress:
            prompt += f"""
        USER PROGRESS:
        - Current Difficulty: {user_progress.current_difficulty}
        - Completed Lessons: {len(user_progress.completed_lessons)}
        - Average Score: {sum(user_progress.test_scores) / len(user_progress.test_scores) if user_progress.test_scores else 0:.1%}
        - Learning Goals: {', '.join(user_progress.learning_goals)}
        
        """
        
        prompt += f"""
        ADAPTATION REQUIREMENTS:
        1. Adjust content complexity to match user's level
        2. Incorporate user's learning style preferences
        3. Include examples relevant to user's interests
        4. Modify duration to fit available time
        5. Align with user's learning goals
        6. Provide personalized examples and applications
        
        Return the adapted lesson content with the same structure as the original.
        """
        
        # Generate adapted content
        adapted_content = await self.llm_service.generate_response(prompt)
        
        # Create adapted lesson
        adapted_lesson = Lesson(
            lesson_id=f"{lesson.lesson_id}_adapted_{user_profile.user_id}",
            title=f"{lesson.title} (Adapted)",
            content=adapted_content,
            difficulty=user_profile.preferred_difficulty,
            duration=min(lesson.duration, user_profile.available_time),
            learning_objectives=lesson.learning_objectives,
            prerequisites=lesson.prerequisites,
            assessment_questions=lesson.assessment_questions,
            practice_exercises=lesson.practice_exercises
        )
        
        print(f"✅ Lesson adapted for user: {user_profile.user_id}")
        return adapted_lesson

# Utility functions for easy integration
async def create_dynamic_lesson(subject: str, 
                               topic: str, 
                               difficulty: str = "medium",
                               llm_service: Optional[BaseLLMService] = None) -> Lesson:
    """Create a single dynamic lesson"""
    
    if not llm_service:
        llm_service = LLMServiceFactory.create_service("google", "demo-key", "gemini-pro")
    
    generator = DynamicLessonGenerator(llm_service)
    return await generator.generate_lesson(subject, topic, difficulty)

async def create_dynamic_curriculum(subject: str, 
                                  level: str, 
                                  duration_weeks: int,
                                  llm_service: Optional[BaseLLMService] = None) -> List[Lesson]:
    """Create a complete dynamic curriculum"""
    
    if not llm_service:
        llm_service = LLMServiceFactory.create_service("google", "demo-key", "gemini-pro")
    
    generator = DynamicLessonGenerator(llm_service)
    return await generator.generate_curriculum(subject, level, duration_weeks)

# Example usage and testing
async def demo_dynamic_lesson_generation():
    """Demonstrate dynamic lesson generation"""
    
    print("🚀 Dynamic Lesson Generation Demo")
    print("=" * 50)
    
    # Initialize LLM service
    llm_service = LLMServiceFactory.create_service("google", "demo-key", "gemini-pro")
    generator = DynamicLessonGenerator(llm_service)
    
    # Generate a single lesson
    print("\n📖 Generating single lesson...")
    lesson = await generator.generate_lesson(
        subject="Python Programming",
        topic="Object-Oriented Programming",
        difficulty="intermediate"
    )
    
    print(f"✅ Generated lesson: {lesson.title}")
    print(f"📝 Content length: {len(lesson.content)} characters")
    print(f"🎯 Learning objectives: {len(lesson.learning_objectives)}")
    print(f"❓ Assessment questions: {len(lesson.assessment_questions)}")
    print(f"💪 Practice exercises: {len(lesson.practice_exercises)}")
    
    # Generate a curriculum
    print("\n📚 Generating curriculum...")
    curriculum = await generator.generate_curriculum(
        subject="Machine Learning",
        level="beginner",
        duration_weeks=4
    )
    
    print(f"✅ Generated curriculum: {len(curriculum)} lessons")
    for i, lesson in enumerate(curriculum[:3], 1):
        print(f"   {i}. {lesson.title}")
    
    print("\n🎉 Dynamic lesson generation completed!")

if __name__ == "__main__":
    asyncio.run(demo_dynamic_lesson_generation())
