# langgraph_course_creator.py - FIXED VERSION
import os
import json
from typing import Any, Dict, List

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

    def _prompt(self, inputs: Dict[str, Any]) -> str:
        subject = inputs.get("subject")
        topic = inputs.get("topic")
        weeks = inputs.get("weeks")
        focus = inputs.get("focus")
        user_profile = inputs.get("user_profile", {})
        goal = inputs.get("goal")
        
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
- User Profile: {json.dumps(user_profile)}
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
            print(f"First JSON parse failed: {e}")
            # ✅ IMPROVED: Second attempt with more specific instructions
            retry_prompt = prompt + "\n\nIMPORTANT: Your previous response was not valid JSON. Please return ONLY the JSON object without any additional text, markdown, or code blocks."
            response = model.generate_content(retry_prompt)
            text = response.text.strip()
            
            # Clean up again
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            try:
                data = json.loads(text)
            except json.JSONDecodeError as e2:
                print(f"Second JSON parse failed: {e2}")
                # ✅ FALLBACK: Return a basic valid structure
                data = self._get_fallback_course(state)
        
        # ✅ IMPROVED: Enhanced validation
        if not isinstance(data, dict):
            print("Model output is not a JSON object, using fallback")
            data = self._get_fallback_course(state)
        
        if "curriculum" not in data:
            print("Missing curriculum in output, using fallback")
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

        # Return merged state
        out = dict(state)
        out["curriculum"] = data["curriculum"]
        out["learning_path"] = data["learning_path"]
        return out

    def _get_fallback_course(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fallback course structure when JSON parsing fails"""
        subject = state.get("subject", "General")
        topic = state.get("topic", "Introduction")
        weeks = state.get("weeks", 4)
        
        return {
            "curriculum": [
                {
                    "id": "lesson_1",
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
                }
            ],
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
        # LangGraph supports sync; call in thread if needed. For simplicity, run sync path.
        inputs: Dict[str, Any] = {
            "subject": subject,
            "topic": topic,
            "weeks": weeks,
            "focus": focus,
            "user_profile": user_profile,
            "goal": goal,
        }
        try:
            result = self._app.invoke(inputs)
            return {
                "curriculum": result.get("curriculum", []),
                "learning_path": result.get("learning_path", {"title": f"{subject} Course"}),
            }
        except Exception as e:
            print(f"Error in create_course: {e}")
            # Return fallback course
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