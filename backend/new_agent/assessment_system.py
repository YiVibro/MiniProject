"""
Assessment System for Multi-Agent AI Tutoring System
====================================================

This module provides comprehensive assessment capabilities including
quiz generation, evaluation, and performance analysis.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import uuid
from pydantic import BaseModel, Field
from models import Assessment, TestResult, UserProgress, Lesson

class Question(BaseModel):
    """Question model"""
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str
    question_type: str  # multiple_choice, true_false, short_answer, essay
    options: List[str] = Field(default_factory=list)  # For multiple choice
    correct_answer: str
    explanation: str = ""
    difficulty: str = "medium"
    points: int = 1
    time_limit: int = 60  # seconds
    tags: List[str] = Field(default_factory=list)

class AssessmentResult(BaseModel):
    """Assessment result model"""
    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    assessment_id: str
    score: float
    total_points: int
    percentage: float
    time_taken: int  # seconds
    answers: List[Dict[str, Any]] = Field(default_factory=list)
    feedback: List[str] = Field(default_factory=list)
    completed_at: datetime = Field(default_factory=datetime.now)
    passed: bool = False

class PerformanceAnalysis(BaseModel):
    """Performance analysis model"""
    user_id: str
    concept: str
    accuracy: float
    speed: float  # questions per minute
    consistency: float
    improvement_areas: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)

class AssessmentSystem:
    """Comprehensive assessment system"""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.assessments = {}  # assessment_id -> Assessment
        self.results = {}  # result_id -> AssessmentResult
        self.questions = {}  # question_id -> Question
        self.performance_data = {}  # user_id -> List[PerformanceAnalysis]
    
    async def create_assessment(self, lesson_id: str, difficulty: str = "medium", 
                               num_questions: int = 5, question_types: List[str] = None) -> Assessment:
        """Create a new assessment"""
        
        if question_types is None:
            question_types = ["multiple_choice", "short_answer"]
        
        # Generate questions using LLM
        questions = await self._generate_questions(lesson_id, difficulty, num_questions, question_types)
        
        # Create assessment
        assessment = Assessment(
            assessment_id=str(uuid.uuid4()),
            lesson_id=lesson_id,
            questions=questions,
            time_limit=num_questions * 2,  # 2 minutes per question
            passing_score=0.7,
            difficulty=difficulty
        )
        
        # Store assessment
        self.assessments[assessment.assessment_id] = assessment
        
        return assessment
    
    async def _generate_questions(self, lesson_id: str, difficulty: str, 
                                 num_questions: int, question_types: List[str]) -> List[Dict[str, Any]]:
        """Generate questions using LLM"""
        
        prompt = f"""
        Create {num_questions} {difficulty} level assessment questions for lesson {lesson_id}.
        
        Question types to include: {', '.join(question_types)}
        
        For each question, provide:
        1. Question text
        2. Question type
        3. Options (for multiple choice)
        4. Correct answer
        5. Explanation
        6. Difficulty level (1-5)
        7. Points (1-5)
        8. Tags (topics covered)
        
        Format as structured questions that can be used for assessment.
        """
        
        response = await self.llm_service.generate_response(prompt)
        
        # Parse questions from response
        questions = self._parse_questions_from_response(response, num_questions)
        
        return questions
    
    def _parse_questions_from_response(self, response: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse questions from LLM response"""
        questions = []
        lines = response.split('\n')
        current_question = None
        
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.')) or line.startswith('Question'):
                if current_question:
                    questions.append(current_question)
                
                current_question = {
                    "question_id": str(uuid.uuid4()),
                    "question_text": line,
                    "question_type": "multiple_choice",
                    "options": [],
                    "correct_answer": "",
                    "explanation": "",
                    "difficulty": 3,
                    "points": 1,
                    "tags": []
                }
            elif current_question and line:
                if line.startswith(('A)', 'B)', 'C)', 'D)')):
                    current_question["options"].append(line)
                elif line.startswith("Answer:"):
                    current_question["correct_answer"] = line.replace("Answer:", "").strip()
                elif line.startswith("Explanation:"):
                    current_question["explanation"] = line.replace("Explanation:", "").strip()
                elif line.startswith("Type:"):
                    current_question["question_type"] = line.replace("Type:", "").strip()
                elif line.startswith("Difficulty:"):
                    try:
                        current_question["difficulty"] = int(line.replace("Difficulty:", "").strip())
                    except ValueError:
                        current_question["difficulty"] = 3
                elif line.startswith("Points:"):
                    try:
                        current_question["points"] = int(line.replace("Points:", "").strip())
                    except ValueError:
                        current_question["points"] = 1
        
        if current_question:
            questions.append(current_question)
        
        return questions[:expected_count]
    
    async def evaluate_assessment(self, assessment_id: str, user_answers: List[Dict[str, Any]], 
                                 user_id: str) -> AssessmentResult:
        """Evaluate user's assessment answers"""
        
        assessment = self.assessments.get(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")
        
        # Calculate score
        total_points = 0
        earned_points = 0
        detailed_answers = []
        
        for i, (question, user_answer) in enumerate(zip(assessment.questions, user_answers)):
            question_points = question.get("points", 1)
            total_points += question_points
            
            # Check if answer is correct
            is_correct = self._check_answer(question, user_answer)
            if is_correct:
                earned_points += question_points
            
            # Store detailed answer
            detailed_answers.append({
                "question_id": question.get("question_id", f"q_{i}"),
                "user_answer": user_answer.get("answer", ""),
                "correct_answer": question.get("correct_answer", ""),
                "is_correct": is_correct,
                "points_earned": question_points if is_correct else 0,
                "explanation": question.get("explanation", "")
            })
        
        # Calculate percentage
        percentage = (earned_points / total_points) * 100 if total_points > 0 else 0
        
        # Generate feedback
        feedback = await self._generate_feedback(detailed_answers, percentage)
        
        # Create result
        result = AssessmentResult(
            user_id=user_id,
            assessment_id=assessment_id,
            score=earned_points,
            total_points=total_points,
            percentage=percentage,
            time_taken=user_answers[0].get("time_taken", 0) if user_answers else 0,
            answers=detailed_answers,
            feedback=feedback,
            passed=percentage >= (assessment.passing_score * 100)
        )
        
        # Store result
        self.results[result.result_id] = result
        
        # Update performance data
        await self._update_performance_data(user_id, result)
        
        return result
    
    def _check_answer(self, question: Dict[str, Any], user_answer: Dict[str, Any]) -> bool:
        """Check if user answer is correct"""
        
        correct_answer = question.get("correct_answer", "").lower().strip()
        user_response = user_answer.get("answer", "").lower().strip()
        
        if question.get("question_type") == "multiple_choice":
            # For multiple choice, check if user selected correct option
            return user_response == correct_answer
        elif question.get("question_type") == "true_false":
            # For true/false, check exact match
            return user_response == correct_answer
        elif question.get("question_type") == "short_answer":
            # For short answer, check if answer contains key terms
            return self._check_short_answer(user_response, correct_answer)
        else:
            # Default: exact match
            return user_response == correct_answer
    
    def _check_short_answer(self, user_answer: str, correct_answer: str) -> bool:
        """Check short answer with fuzzy matching"""
        
        # Simple keyword matching
        user_words = set(user_answer.split())
        correct_words = set(correct_answer.split())
        
        # Check if user answer contains key terms from correct answer
        overlap = len(user_words.intersection(correct_words))
        total_correct_words = len(correct_words)
        
        # Consider correct if at least 70% of key terms are present
        return overlap / total_correct_words >= 0.7 if total_correct_words > 0 else False
    
    async def _generate_feedback(self, detailed_answers: List[Dict[str, Any]], 
                                percentage: float) -> List[str]:
        """Generate feedback for assessment"""
        
        correct_count = sum(1 for answer in detailed_answers if answer["is_correct"])
        total_count = len(detailed_answers)
        
        feedback = []
        
        if percentage >= 90:
            feedback.append("Excellent work! You've mastered this material.")
        elif percentage >= 80:
            feedback.append("Good job! You have a solid understanding of the concepts.")
        elif percentage >= 70:
            feedback.append("Not bad! You're on the right track, but there's room for improvement.")
        elif percentage >= 60:
            feedback.append("You're making progress, but consider reviewing the material.")
        else:
            feedback.append("Don't worry! This is a learning opportunity. Review the material and try again.")
        
        # Add specific feedback for incorrect answers
        incorrect_answers = [answer for answer in detailed_answers if not answer["is_correct"]]
        if incorrect_answers:
            feedback.append(f"You missed {len(incorrect_answers)} questions. Focus on reviewing those concepts.")
        
        # Add improvement suggestions
        if percentage < 80:
            feedback.append("Consider spending more time on the foundational concepts.")
            feedback.append("Practice with additional examples to reinforce your understanding.")
        
        return feedback
    
    async def _update_performance_data(self, user_id: str, result: AssessmentResult):
        """Update performance data for user"""
        
        if user_id not in self.performance_data:
            self.performance_data[user_id] = []
        
        # Calculate performance metrics
        accuracy = result.percentage / 100
        speed = result.total_points / (result.time_taken / 60) if result.time_taken > 0 else 0
        
        # Analyze performance patterns
        analysis = PerformanceAnalysis(
            user_id=user_id,
            concept="general",  # Would be determined from assessment content
            accuracy=accuracy,
            speed=speed,
            consistency=0.8,  # Would be calculated from historical data
            improvement_areas=await self._identify_improvement_areas(result),
            strengths=await self._identify_strengths(result),
            recommendations=await self._generate_recommendations(result)
        )
        
        self.performance_data[user_id].append(analysis)
        
        # Keep only last 20 analyses
        if len(self.performance_data[user_id]) > 20:
            self.performance_data[user_id] = self.performance_data[user_id][-20:]
    
    async def _identify_improvement_areas(self, result: AssessmentResult) -> List[str]:
        """Identify areas for improvement"""
        
        improvement_areas = []
        
        # Analyze incorrect answers
        incorrect_answers = [answer for answer in result.answers if not answer["is_correct"]]
        
        if len(incorrect_answers) > len(result.answers) * 0.5:
            improvement_areas.append("Fundamental understanding")
        
        if result.percentage < 70:
            improvement_areas.append("Concept application")
        
        if result.time_taken > 300:  # More than 5 minutes
            improvement_areas.append("Speed and efficiency")
        
        return improvement_areas
    
    async def _identify_strengths(self, result: AssessmentResult) -> List[str]:
        """Identify user strengths"""
        
        strengths = []
        
        if result.percentage >= 90:
            strengths.append("Excellent comprehension")
        
        if result.time_taken < 120:  # Less than 2 minutes
            strengths.append("Quick problem-solving")
        
        correct_answers = [answer for answer in result.answers if answer["is_correct"]]
        if len(correct_answers) > 0:
            strengths.append("Good understanding of core concepts")
        
        return strengths
    
    async def _generate_recommendations(self, result: AssessmentResult) -> List[str]:
        """Generate recommendations based on performance"""
        
        recommendations = []
        
        if result.percentage < 70:
            recommendations.append("Review the lesson material thoroughly")
            recommendations.append("Practice with additional examples")
            recommendations.append("Consider seeking help from a tutor")
        elif result.percentage < 85:
            recommendations.append("Focus on areas where you made mistakes")
            recommendations.append("Practice similar problems")
        else:
            recommendations.append("Great job! Consider moving to more advanced topics")
            recommendations.append("Help others who might be struggling")
        
        return recommendations
    
    def get_user_performance(self, user_id: str) -> List[PerformanceAnalysis]:
        """Get performance data for user"""
        return self.performance_data.get(user_id, [])
    
    def get_assessment_result(self, result_id: str) -> Optional[AssessmentResult]:
        """Get assessment result by ID"""
        return self.results.get(result_id)
    
    def get_assessment(self, assessment_id: str) -> Optional[Assessment]:
        """Get assessment by ID"""
        return self.assessments.get(assessment_id)
    
    async def generate_adaptive_questions(self, user_id: str, concept: str, 
                                        difficulty: str = "medium") -> List[Question]:
        """Generate adaptive questions based on user performance"""
        
        # Get user's performance history
        performance_history = self.get_user_performance(user_id)
        
        # Analyze performance patterns
        if performance_history:
            recent_accuracy = sum(p.accuracy for p in performance_history[-5:]) / len(performance_history[-5:])
            if recent_accuracy > 0.8:
                difficulty = "hard"
            elif recent_accuracy < 0.6:
                difficulty = "easy"
        
        # Generate questions
        prompt = f"""
        Generate 5 adaptive questions for concept "{concept}" at {difficulty} level.
        
        Consider the user's performance history and create questions that:
        1. Match their current ability level
        2. Address any knowledge gaps
        3. Build on their strengths
        4. Provide appropriate challenge
        
        Format as structured questions.
        """
        
        response = await self.llm_service.generate_response(prompt)
        questions = self._parse_questions_from_response(response, 5)
        
        return [Question(**q) for q in questions]
    
    async def analyze_learning_gaps(self, user_id: str, assessment_id: str) -> Dict[str, Any]:
        """Analyze learning gaps from assessment"""
        
        result = self.results.get(assessment_id)
        if not result:
            return {"error": "Assessment result not found"}
        
        # Analyze incorrect answers
        incorrect_answers = [answer for answer in result.answers if not answer["is_correct"]]
        
        gap_analysis = {
            "total_questions": len(result.answers),
            "incorrect_count": len(incorrect_answers),
            "accuracy": result.percentage,
            "gaps_identified": [],
            "recommendations": []
        }
        
        # Identify specific gaps
        for answer in incorrect_answers:
            gap_analysis["gaps_identified"].append({
                "question_id": answer["question_id"],
                "concept": "Unknown",  # Would be determined from question content
                "gap_type": "knowledge",
                "severity": "medium"
            })
        
        # Generate recommendations
        if result.percentage < 70:
            gap_analysis["recommendations"].append("Review fundamental concepts")
            gap_analysis["recommendations"].append("Practice with easier examples")
        elif result.percentage < 85:
            gap_analysis["recommendations"].append("Focus on specific problem areas")
            gap_analysis["recommendations"].append("Practice similar problems")
        
        return gap_analysis
