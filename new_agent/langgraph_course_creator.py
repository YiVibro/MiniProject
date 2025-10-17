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
        self.api_key = api_key or os.getenv("AIzaSyCID-mm0AsMkDBJ5NJsDGTKx0LFTfQc594")
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
        return (
            "You are an expert curriculum designer. Create a compact JSON course based on the user's goal.\n"
            "Return ONLY valid JSON, no extra text. Keys must be: curriculum (array of lessons), learning_path (object).\n"
            "Each lesson object must have: id (string), title (string), difficulty (string), duration (number minutes), content (string), "
            "learning_objectives (string array), prerequisites (string array), subtopics (array), questions (array).\n"
            "For subtopics: produce 2-4 concise subtopics per lesson as an array of objects with fields: title (string), deadline_minutes (number).\n"
            "For questions: produce 3-5 varied questions per lesson as an array of objects with fields: "
            "question (string), type (one of 'multiple_choice','short_answer'), options (string array, required for multiple_choice, else empty), "
            "answer (string). Keep questions concise but specific.\n"
            f"User Goal: {goal}\n"
            f"Subject: {subject} | Topic: {topic} | Weeks: {weeks} | Focus: {focus}\n"
            f"User Profile: {json.dumps(user_profile)}\n"
            "Constraints:\n"
            "- No placeholders.\n"
            "- Ensure 8-16 lessons depending on weeks and focus.\n"
            "- Difficulty progression should be coherent.\n"
            "- Keep content concise but specific.\n"
            "- Output must be strict JSON with the exact schema."
        )

    def _generate_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._prompt(state)
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        text = response.text if hasattr(response, "text") else str(response)
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Attempt a second pass asking for JSON only
            response = model.generate_content(
                prompt + "\nReturn only JSON conforming exactly to the schema."
            )
            text = response.text if hasattr(response, "text") else str(response)
            data = json.loads(text)

        # Basic validation
        if not isinstance(data, dict):
            raise ValueError("Model output is not a JSON object")
        if "curriculum" not in data or "learning_path" not in data:
            raise ValueError("Missing required keys in output")

        # Return merged state
        out = dict(state)
        out["curriculum"] = data["curriculum"]
        out["learning_path"] = data["learning_path"]
        return out

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
        result = self._app.invoke(inputs)
        return {
            "curriculum": result.get("curriculum", []),
            "learning_path": result.get("learning_path", {"title": f"{subject} Course"}),
        }

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


