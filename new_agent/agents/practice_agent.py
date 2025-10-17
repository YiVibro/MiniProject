"""
Practice Agent - Customized Quiz Generation and Evaluation
=========================================================

This agent generates and evaluates customized quizzes, adapting difficulty
and question types based on user performance and learning objectives.
"""

from typing import Dict, Any, List, Optional, Tuple
from .base_agent import BaseAgent, AgentState, AgentResponse
from models import Assessment, TestResult, Lesson
from assessment_system import AssessmentSystem

class PracticeAgent(BaseAgent):
    """Agent responsible for quiz generation and evaluation"""
    
    def __init__(self, llm_service):
        super().__init__("practice", llm_service)
        self.assessment_system = AssessmentSystem(llm_service)
        self.question_types = {
            "multiple_choice": "Multiple choice questions with 4 options",
            "true_false": "True/False statements",
            "fill_blank": "Fill in the blank questions",
            "short_answer": "Short answer questions",
            "problem_solving": "Step-by-step problem solving",
            "application": "Real-world application questions"
        }
    
    async def process(self, state: AgentState) -> AgentResponse:
        """Generate or evaluate practice content"""
        try:
            action = state.metadata.get("action", "generate_quiz")
            
            if action == "generate_quiz":
                return await self._generate_quiz(state)
            elif action == "evaluate_answers":
                return await self._evaluate_answers(state)
            elif action == "generate_practice_problems":
                return await self._generate_practice_problems(state)
            else:
                return self.create_response(
                    response="I can help with quiz generation, answer evaluation, or practice problems. What would you like me to do?",
                    confidence=0.8
                )
                
        except Exception as e:
            return self.create_response(
                response="I encountered an error while processing your practice request. Please try again.",
                confidence=0.1,
                metadata={"error": str(e)}
            )
    
    async def _generate_quiz(self, state: AgentState) -> AgentResponse:
        """Generate adaptive quiz"""
        try:
            lesson_content = state.metadata.get("lesson_content", "")
            difficulty = state.metadata.get("difficulty", "medium")
            num_questions = state.metadata.get("num_questions", 5)
            question_types = state.metadata.get("question_types", ["multiple_choice", "short_answer"])
            
            # Generate quiz questions
            quiz_data = await self._create_adaptive_quiz(
                lesson_content, difficulty, num_questions, question_types
            )
            
            return self.create_response(
                response=f"Generated {len(quiz_data['questions'])} practice questions",
                confidence=0.9,
                metadata={
                    "quiz_data": quiz_data,
                    "difficulty": difficulty,
                    "question_count": len(quiz_data['questions']),
                    "question_types": question_types
                }
            )
            
        except Exception as e:
            return self.create_response(
                response="Error generating quiz. Please try again.",
                confidence=0.1,
                metadata={"error": str(e)}
            )
    
    async def _create_adaptive_quiz(self, content: str, difficulty: str, 
                                  num_questions: int, question_types: List[str]) -> Dict[str, Any]:
        """Create adaptive quiz based on content and difficulty"""
        
        prompt = f"""
        Create a {difficulty} level quiz with {num_questions} questions based on this content:
        
        Content: {content}
        
        Question Types to Include: {', '.join(question_types)}
        
        For each question, provide:
        1. The question text
        2. Correct answer
        3. Explanation of the answer
        4. Difficulty level (1-5)
        5. Learning objective it tests
        
        Format as structured data that can be used for assessment.
        """
        
        quiz_text = await self.llm_service.generate_response(prompt)
        
        # Parse the generated quiz
        questions = self._parse_quiz_questions(quiz_text, num_questions)
        
        return {
            "questions": questions,
            "total_questions": len(questions),
            "difficulty": difficulty,
            "estimated_time": len(questions) * 2,  # 2 minutes per question
            "learning_objectives": self._extract_learning_objectives(questions)
        }
    
    def _parse_quiz_questions(self, quiz_text: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse generated quiz text into structured format"""
        questions = []
        lines = quiz_text.split('\n')
        current_question = None
        
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.')) or line.startswith('Question'):
                if current_question:
                    questions.append(current_question)
                current_question = {
                    "id": len(questions) + 1,
                    "question": line,
                    "options": [],
                    "correct_answer": "",
                    "explanation": "",
                    "difficulty": 3,
                    "type": "multiple_choice"
                }
            elif current_question and line:
                if line.startswith(('A)', 'B)', 'C)', 'D)')) or line.startswith(('A.', 'B.', 'C.', 'D.')):
                    current_question["options"].append(line)
                elif line.startswith("Answer:") or line.startswith("Correct:"):
                    current_question["correct_answer"] = line.replace("Answer:", "").replace("Correct:", "").strip()
                elif line.startswith("Explanation:"):
                    current_question["explanation"] = line.replace("Explanation:", "").strip()
        
        if current_question:
            questions.append(current_question)
        
        return questions[:expected_count]
    
    def _extract_learning_objectives(self, questions: List[Dict[str, Any]]) -> List[str]:
        """Extract learning objectives from questions"""
        objectives = set()
        for question in questions:
            if "learning_objective" in question:
                objectives.add(question["learning_objective"])
        return list(objectives)
    
    async def _evaluate_answers(self, state: AgentState) -> AgentResponse:
        """Evaluate user answers and provide feedback"""
        try:
            user_answers = state.metadata.get("user_answers", [])
            correct_answers = state.metadata.get("correct_answers", [])
            questions = state.metadata.get("questions", [])
            
            # Evaluate answers
            evaluation = await self._grade_answers(user_answers, correct_answers, questions)
            
            return self.create_response(
                response=f"Evaluation complete. Score: {evaluation['score']}%",
                confidence=0.9,
                metadata=evaluation
            )
            
        except Exception as e:
            return self.create_response(
                response="Error evaluating answers. Please try again.",
                confidence=0.1,
                metadata={"error": str(e)}
            )
    
    async def _grade_answers(self, user_answers: List[str], correct_answers: List[str], 
                           questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Grade user answers with detailed feedback"""
        
        if len(user_answers) != len(correct_answers):
            return {"error": "Mismatch in answer count"}
        
        correct_count = 0
        detailed_feedback = []
        
        for i, (user_answer, correct_answer) in enumerate(zip(user_answers, correct_answers)):
            is_correct = self._compare_answers(user_answer, correct_answer)
            if is_correct:
                correct_count += 1
            
            feedback = {
                "question_id": i + 1,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": questions[i].get("explanation", "") if i < len(questions) else ""
            }
            detailed_feedback.append(feedback)
        
        score = (correct_count / len(user_answers)) * 100 if user_answers else 0
        
        return {
            "score": round(score, 1),
            "correct_count": correct_count,
            "total_questions": len(user_answers),
            "passed": score >= 70,  # 70% passing threshold
            "detailed_feedback": detailed_feedback,
            "improvement_suggestions": await self._generate_improvement_suggestions(detailed_feedback)
        }
    
    def _compare_answers(self, user_answer: str, correct_answer: str) -> bool:
        """Compare user answer with correct answer (case-insensitive)"""
        return user_answer.lower().strip() == correct_answer.lower().strip()
    
    async def _generate_improvement_suggestions(self, feedback: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement suggestions based on incorrect answers"""
        
        incorrect_questions = [f for f in feedback if not f["is_correct"]]
        
        if not incorrect_questions:
            return ["Excellent work! All answers were correct."]
        
        prompt = f"""
        Based on these incorrect answers, provide 3-5 specific improvement suggestions:
        
        Incorrect Answers:
        {chr(10).join(f"Q{f['question_id']}: {f['user_answer']} (Correct: {f['correct_answer']})" for f in incorrect_questions)}
        
        Provide actionable suggestions for improvement.
        """
        
        suggestions_text = await self.llm_service.generate_response(prompt)
        return [s.strip() for s in suggestions_text.split('\n') if s.strip()][:5]
    
    async def _generate_practice_problems(self, state: AgentState) -> AgentResponse:
        """Generate additional practice problems"""
        try:
            topic = state.metadata.get("topic", "")
            difficulty = state.metadata.get("difficulty", "medium")
            num_problems = state.metadata.get("num_problems", 3)
            
            prompt = f"""
            Generate {num_problems} {difficulty} level practice problems for: {topic}
            
            For each problem:
            1. Clear problem statement
            2. Step-by-step solution
            3. Key concepts being tested
            4. Alternative approaches (if applicable)
            
            Make problems practical and engaging.
            """
            
            problems_text = await self.llm_service.generate_response(prompt)
            
            return self.create_response(
                response=f"Generated {num_problems} practice problems for {topic}",
                confidence=0.9,
                metadata={
                    "problems": problems_text,
                    "topic": topic,
                    "difficulty": difficulty,
                    "count": num_problems
                }
            )
            
        except Exception as e:
            return self.create_response(
                response="Error generating practice problems. Please try again.",
                confidence=0.1,
                metadata={"error": str(e)}
            )
    
    def get_capabilities(self) -> List[str]:
        """Return practice agent capabilities"""
        return [
            "Adaptive quiz generation",
            "Multi-format question creation",
            "Automated answer evaluation",
            "Detailed feedback and explanations",
            "Performance analysis",
            "Practice problem generation",
            "Difficulty adjustment",
            "Learning objective tracking"
        ]
