"""
Knowledge Agent - Dynamic Concept Explanations
==============================================

This agent specializes in explaining concepts at tailored difficulty levels,
adapting explanations based on user proficiency and learning style.
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentState, AgentResponse
from models import Lesson, UserProgress

class KnowledgeAgent(BaseAgent):
    """Agent responsible for dynamic concept explanations"""
    
    def __init__(self, llm_service):
        super().__init__("knowledge", llm_service)
        self.explanation_styles = {
            "visual": "Use diagrams, charts, and visual metaphors",
            "analytical": "Focus on step-by-step logical breakdowns", 
            "practical": "Emphasize real-world applications and examples",
            "conceptual": "Build understanding through fundamental principles"
        }
    
    async def process(self, state: AgentState) -> AgentResponse:
        """Generate adaptive concept explanation"""
        try:
            concept = state.metadata.get("concept", "")
            difficulty = state.metadata.get("difficulty", "medium")
            learning_style = state.metadata.get("learning_style", "practical")
            user_progress = state.metadata.get("user_progress")
            
            # Generate adaptive explanation
            explanation = await self._generate_adaptive_explanation(
                concept, difficulty, learning_style, user_progress
            )
            
            # Add learning resources
            resources = await self._generate_learning_resources(concept, difficulty)
            
            return self.create_response(
                response=explanation,
                confidence=0.9,
                metadata={
                    "concept": concept,
                    "difficulty": difficulty,
                    "learning_style": learning_style,
                    "resources": resources,
                    "explanation_type": "adaptive"
                }
            )
            
        except Exception as e:
            return self.create_response(
                response=f"I apologize, but I encountered an error while explaining {state.metadata.get('concept', 'this concept')}. Please try again.",
                confidence=0.1,
                metadata={"error": str(e)}
            )
    
    async def _generate_adaptive_explanation(self, concept: str, difficulty: str, 
                                          learning_style: str, user_progress: Optional[UserProgress]) -> str:
        """Generate explanation adapted to user's needs"""
        
        style_guidance = self.explanation_styles.get(learning_style, self.explanation_styles["practical"])
        
        prompt = f"""
        Explain the concept "{concept}" with the following adaptations:
        
        Difficulty Level: {difficulty}
        - Easy: Use simple language, basic examples, step-by-step approach
        - Medium: Include some complexity, practical applications, moderate depth
        - Hard: Advanced concepts, edge cases, theoretical foundations
        
        Learning Style: {learning_style}
        {style_guidance}
        
        Additional Context:
        - Make it engaging and interactive
        - Include analogies or metaphors where helpful
        - Provide concrete examples
        - Ask thought-provoking questions to check understanding
        
        Format the explanation clearly with headers and bullet points where appropriate.
        """
        
        return await self.llm_service.generate_response(prompt)
    
    async def _generate_learning_resources(self, concept: str, difficulty: str) -> List[Dict[str, str]]:
        """Generate additional learning resources"""
        
        prompt = f"""
        For the concept "{concept}" at {difficulty} level, suggest 3-5 learning resources:
        
        Include:
        1. A practical exercise or problem to solve
        2. A real-world application example
        3. A visual diagram or chart description
        4. A related concept to explore next
        5. A common misconception to avoid
        
        Format as a structured list with clear titles and brief descriptions.
        """
        
        resources_text = await self.llm_service.generate_response(prompt)
        
        # Parse resources into structured format
        resources = []
        lines = resources_text.split('\n')
        current_resource = None
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith(('1.', '2.', '3.', '4.', '5.')) or 
                       line.startswith(('•', '-', '*'))):
                if current_resource:
                    resources.append(current_resource)
                current_resource = {
                    "title": line,
                    "description": "",
                    "type": "learning_resource"
                }
            elif current_resource and line:
                current_resource["description"] += line + " "
        
        if current_resource:
            resources.append(current_resource)
        
        return resources[:5]  # Limit to 5 resources
    
    def get_capabilities(self) -> List[str]:
        """Return knowledge agent capabilities"""
        return [
            "Adaptive concept explanations",
            "Multi-difficulty content generation", 
            "Learning style adaptation",
            "Interactive explanations with questions",
            "Learning resource recommendations",
            "Misconception identification and correction",
            "Progressive complexity adjustment"
        ]
    
    async def explain_with_context(self, concept: str, context: str, 
                                 user_level: str = "intermediate") -> str:
        """Explain concept with specific context"""
        
        prompt = f"""
        Explain "{concept}" in the context of "{context}" for a {user_level} learner.
        
        Requirements:
        - Connect the concept to the given context
        - Use appropriate complexity for the user level
        - Include practical examples from the context
        - Suggest how this concept applies in similar situations
        
        Make it clear, engaging, and immediately applicable.
        """
        
        return await self.llm_service.generate_response(prompt)
    
    async def identify_learning_gaps(self, user_responses: List[str], 
                                    target_concept: str) -> List[str]:
        """Identify knowledge gaps from user responses"""
        
        prompt = f"""
        Analyze these user responses about "{target_concept}":
        
        User Responses:
        {chr(10).join(f"- {response}" for response in user_responses)}
        
        Identify specific knowledge gaps or misconceptions. For each gap:
        1. Describe the specific misunderstanding
        2. Explain why it's incorrect
        3. Provide the correct understanding
        4. Suggest how to address this gap
        
        Format as a clear, actionable list.
        """
        
        return await self.llm_service.generate_response(prompt)
