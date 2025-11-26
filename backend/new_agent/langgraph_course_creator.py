# langgraph_course_creator.py - FIXED VERSION
import os
import json
from typing import Any, Dict, List
from datetime import datetime
import logging

# Set up proper logging
logger = logging.getLogger(__name__)

# Minimal LangGraph + Gemini integration to generate a curriculum from a user goal
try:
    from langgraph.graph import StateGraph, START, END
    import google.generativeai as genai
except Exception as e:  # pragma: no cover
    StateGraph = None  # type: ignore
    genai = None  # type: ignore


class LangGraphCourseCreator:
    """Create a dynamic course using a small LangGraph flow that calls Gemini.

    This is intentionally minimal and self-contained. It produces a JSON curriculum
    and a learning_path summary from a user goal without hardcoding topics.
    """

    def __init__(self, api_key: str | None = None, model: str = "gemini-1.5-flash") -> None:
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model
        if genai is None or StateGraph is None:
            raise RuntimeError("LangGraph or google-generativeai is not installed.")
        if not self.api_key:
            raise RuntimeError("GOOGLE_API_KEY is required for Gemini.")
        genai.configure(api_key=self.api_key)

        # Build a trivial graph with one node that calls Gemini and validates JSON
        self._graph = StateGraph(dict)
        self._graph.add_node("generate", self._generate_node)
        self._graph.add_edge(START, "generate")
        self._graph.add_edge("generate", END)
        self._app = self._graph.compile()

    def _clean_state_for_serialization(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Clean state recursively to ensure all values are JSON serializable"""
        def clean_value(value: Any) -> Any:
            """Recursively clean a value to be JSON serializable"""
            if isinstance(value, datetime):
                # Convert datetime to ISO format string
                return value.isoformat()
            elif isinstance(value, dict):
                # Recursively clean dictionary
                return {k: clean_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                # Recursively clean list
                return [clean_value(item) for item in value]
            elif isinstance(value, tuple):
                # Convert tuple to list and clean
                return [clean_value(item) for item in value]
            else:
                # Try to serialize, convert to string if it fails
                try:
                    json.dumps(value)
                    return value
                except (TypeError, ValueError):
                    return str(value)
        
        # Clean the entire state dictionary recursively
        cleaned = {}
        for key, value in state.items():
            cleaned[key] = clean_value(value)
        return cleaned

    def _prompt(self, inputs: Dict[str, Any]) -> str:
        subject = inputs.get("subject")
        topic = inputs.get("topic")
        weeks = inputs.get("weeks")
        focus = inputs.get("focus")
        user_profile = inputs.get("user_profile", {})
        goal = inputs.get("goal")
        
        # Ensure user_profile is serializable for the prompt
        try:
            user_profile_str = json.dumps(user_profile, default=str)
        except (TypeError, ValueError):
            user_profile_str = str(user_profile)
        
        # ✅ IMPROVED PROMPT: More structured and explicit JSON format
        return f"""Create a course curriculum in STRICT JSON format.

REQUIRED JSON STRUCTURE (copy exactly):
{{
  "curriculum": [
    {{
      "id": "lesson_1",
      "title": "Lesson Title",
      "difficulty": "beginner",
      "duration": 45,
      "content": "Lesson content here...",
      "learning_objectives": ["objective 1", "objective 2"],
      "prerequisites": [],
      "subtopics": [
        {{"title": "Subtopic 1", "deadline_minutes": 20}}
      ],
      "questions": [
        {{
          "question": "What is X?",
          "type": "multiple_choice",
          "options": ["A", "B", "C", "D"],
          "answer": "A"
        }}
      ]
    }}
  ],
  "learning_path": {{
    "title": "Course Title",
    "description": "Course description",
    "estimated_duration": 300,
    "difficulty_progression": ["beginner", "intermediate"],
    "milestones": ["milestone 1", "milestone 2"]
  }}
}}

COURSE REQUIREMENTS:
- Subject: {subject}
- Topic: {topic}
- Weeks: {weeks}
- Focus: {focus}
- User Profile: {user_profile_str}
- Goal: {goal}

CRITICAL RULES:
1. Return ONLY the JSON object above - NO markdown, NO code blocks, NO explanatory text
2. Create exactly {weeks * 3} lessons (3 lessons per week)
3. Each lesson MUST have 3-5 assessment questions
4. Each lesson MUST have 2-4 subtopics
5. Content must be substantive (minimum 200 words per lesson)
6. Ensure valid JSON syntax (proper quotes, commas, brackets)
7. Difficulty should progress from "beginner" to "intermediate" to "advanced"
8. Questions should test actual understanding, not just recall
9. Learning objectives should be specific and measurable
10. Duration should be realistic (30-90 minutes per lesson)

LESSON STRUCTURE RULES:
- First lesson should be introductory and motivational
- Middle lessons should build core concepts
- Final lessons should focus on application and synthesis
- Include practical examples and real-world applications
- Balance theory with practice

OUTPUT ONLY THE JSON OBJECT. DO NOT WRITE ANY OTHER TEXT.
"""

    def _generate_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._prompt(state)
        model = genai.GenerativeModel(self.model)
        
        try:
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            # ✅ IMPROVED: Clean up common JSON issues
            # Remove markdown code blocks if present
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            # Try to parse JSON
            data = json.loads(text)
            
        except json.JSONDecodeError as e:
            logger.error(f"First JSON parse failed: {e}")
            logger.error(f"Response text: {text[:500]}")
            # ✅ IMPROVED: Second attempt with more specific instructions
            retry_prompt = prompt + "\n\nIMPORTANT: Your previous response was not valid JSON. Please return ONLY the JSON object without any additional text, markdown, or code blocks."
            try:
                response = model.generate_content(retry_prompt)
                text = response.text.strip()
                
                # Clean up again
                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
                
                data = json.loads(text)
            except (json.JSONDecodeError, Exception) as e2:
                logger.error(f"Second JSON parse failed: {e2}")
                logger.error(f"Retry response text: {text[:500]}")
                # ✅ FIXED FALLBACK: Return proper number of lessons
                data = self._get_fallback_course(state)
        
        # ✅ IMPROVED: Enhanced validation
        if not isinstance(data, dict):
            logger.error("Model output is not a JSON object, using fallback")
            data = self._get_fallback_course(state)
        
        if "curriculum" not in data:
            logger.error("Missing curriculum in output, using fallback")
            data = self._get_fallback_course(state)
        
        if "learning_path" not in data:
            data["learning_path"] = {
                "title": f"{state.get('subject', 'General')} Course",
                "description": f"Learn {state.get('topic', 'the subject')}",
                "estimated_duration": state.get('weeks', 4) * 7 * 60,  # minutes
                "difficulty_progression": ["beginner", "intermediate", "advanced"],
                "milestones": ["Foundation", "Core Concepts", "Advanced Applications"]
            }

        # Validate curriculum structure
        if isinstance(data["curriculum"], list):
            for i, lesson in enumerate(data["curriculum"]):
                # Ensure required fields exist
                lesson.setdefault("id", f"lesson_{i+1}")
                lesson.setdefault("title", f"Lesson {i+1}")
                lesson.setdefault("difficulty", "beginner")
                lesson.setdefault("duration", 45)
                lesson.setdefault("content", "Lesson content")
                lesson.setdefault("learning_objectives", [f"Learn key concepts for {state.get('topic', 'the subject')}"])
                lesson.setdefault("prerequisites", [])
                lesson.setdefault("subtopics", [{"title": "Introduction", "deadline_minutes": 15}])
                lesson.setdefault("questions", [
                    {
                        "question": f"What is the main topic of {state.get('subject', 'this lesson')}?",
                        "type": "multiple_choice",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "answer": "Option A"
                    }
                ])

        # Return merged state - ensure it's serializable
        out = dict(state)
        out["curriculum"] = data["curriculum"]
        out["learning_path"] = data["learning_path"]
        return self._clean_state_for_serialization(out)

    def _get_fallback_course(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fallback course structure when JSON parsing fails"""
        subject = state.get("subject", "General")
        topic = state.get("topic", "Introduction")
        weeks = state.get("weeks", 4)
        total_lessons = weeks * 3  # ✅ FIXED: Generate proper number of lessons
        
        curriculum = []
        for i in range(total_lessons):
            lesson_num = i + 1
            if lesson_num == 1:
                # First lesson - introductory
                curriculum.append({
                    "id": f"lesson_{lesson_num}",
                    "title": f"Introduction to {topic}",
                    "difficulty": "beginner",
                    "duration": 45,
                    "content": f"This lesson introduces the fundamental concepts of {topic}. You will learn the basic principles and how they apply in real-world scenarios.",
                    "learning_objectives": [
                        f"Understand basic {topic} concepts",
                        "Identify key principles and applications",
                        "Apply foundational knowledge to simple problems"
                    ],
                    "prerequisites": [],
                    "subtopics": [
                        {"title": "What is this subject about?", "deadline_minutes": 20},
                        {"title": "Key concepts and terminology", "deadline_minutes": 25}
                    ],
                    "questions": [
                        {
                            "question": f"What is the primary focus of {topic}?",
                            "type": "multiple_choice",
                            "options": [
                                "Theory only",
                                "Practical application", 
                                "Memorization",
                                "All of the above"
                            ],
                            "answer": "Practical application"
                        },
                        {
                            "question": "Why is this subject important?",
                            "type": "short_answer", 
                            "options": [],
                            "answer": "It provides foundational knowledge for advanced topics"
                        }
                    ]
                })
            elif lesson_num <= total_lessons - 1:
                # Middle lessons
                curriculum.append({
                    "id": f"lesson_{lesson_num}",
                    "title": f"{topic} Core Concepts - Part {lesson_num-1}",
                    "difficulty": "intermediate",
                    "duration": 60,
                    "content": f"This lesson builds on foundational knowledge to explore deeper concepts in {topic}. You'll learn practical applications and problem-solving techniques.",
                    "learning_objectives": [
                        f"Apply {topic} concepts to real-world scenarios",
                        "Develop problem-solving strategies",
                        "Analyze complex situations using core principles"
                    ],
                    "prerequisites": [f"lesson_{lesson_num-1}"],
                    "subtopics": [
                        {"title": "Advanced concepts", "deadline_minutes": 25},
                        {"title": "Practical applications", "deadline_minutes": 20},
                        {"title": "Problem-solving techniques", "deadline_minutes": 15}
                    ],
                    "questions": [
                        {
                            "question": f"How would you apply {topic} concepts to solve a real-world problem?",
                            "type": "short_answer",
                            "options": [],
                            "answer": "By identifying the core principles and adapting them to the specific context"
                        }
                    ]
                })
            else:
                # Final lesson
                curriculum.append({
                    "id": f"lesson_{lesson_num}",
                    "title": f"Advanced Applications of {topic}",
                    "difficulty": "advanced",
                    "duration": 75,
                    "content": f"This final lesson focuses on advanced applications and synthesis of all {topic} concepts learned throughout the course.",
                    "learning_objectives": [
                        f"Synthesize all {topic} concepts",
                        "Create advanced applications",
                        "Evaluate complex scenarios critically"
                    ],
                    "prerequisites": [f"lesson_{lesson_num-1}"],
                    "subtopics": [
                        {"title": "Advanced synthesis", "deadline_minutes": 30},
                        {"title": "Real-world case studies", "deadline_minutes": 25},
                        {"title": "Future applications", "deadline_minutes": 20}
                    ],
                    "questions": [
                        {
                            "question": f"What are the most important advanced applications of {topic}?",
                            "type": "short_answer",
                            "options": [],
                            "answer": "The applications that solve complex real-world problems and drive innovation"
                        }
                    ]
                })
        
        return {
            "curriculum": curriculum,
            "learning_path": {
                "title": f"{subject} Course",
                "description": f"Learn {topic} through practical examples and applications",
                "estimated_duration": weeks * 7 * 60,
                "difficulty_progression": ["beginner", "intermediate", "advanced"],
                "milestones": ["Foundation", "Core Concepts", "Mastery"]
            }
        }

    async def create_course(self, *, subject: str, topic: str, weeks: int, focus: str, user_profile: Dict[str, Any], goal: str) -> Dict[str, Any]:
        """Run the graph to generate a course JSON."""
        # Clean inputs to ensure serializability
        cleaned_user_profile = self._clean_state_for_serialization(user_profile)
        
        inputs: Dict[str, Any] = {
            "subject": subject,
            "topic": topic,
            "weeks": weeks,
            "focus": focus,
            "user_profile": cleaned_user_profile,
            "goal": goal,
        }
        
        try:
            # Clean the entire inputs dict before passing to LangGraph
            cleaned_inputs = self._clean_state_for_serialization(inputs)
            result = self._app.invoke(cleaned_inputs)
            
            # Ensure the result is clean before returning
            clean_result = self._clean_state_for_serialization(result)
            return {
                "curriculum": clean_result.get("curriculum", []),
                "learning_path": clean_result.get("learning_path", {"title": f"{subject} Course"}),
            }
        except Exception as e:
            logger.error(f"Error in create_course: {e}")
            # Return fallback course with proper lesson count
            return self._get_fallback_course(inputs)

    # Convenience wrapper for a single-call API
    async def generate_course(self, user_goal: str, subject: str, topic: str, weeks: int = 4, focus: str = "balanced", user_profile: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return await self.create_course(
            subject=subject,
            topic=topic,
            weeks=weeks,
            focus=focus,
            user_profile=user_profile or {},
            goal=user_goal,
        )