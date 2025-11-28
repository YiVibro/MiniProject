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
import re
from pydantic import BaseModel, Field
from .models import Assessment, TestResult, UserProgress, Lesson

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
        """Create a new assessment - with enhanced error handling"""
        
        if question_types is None:
            question_types = ["multiple_choice", "short_answer"]
        
        try:
            # Generate questions using LLM
            questions = await self._generate_questions(lesson_id, difficulty, num_questions, question_types)
            
            # ✅ ENHANCED: Ensure we have the expected number of questions
            if len(questions) < num_questions:
                print(f"Warning: Generated only {len(questions)} questions, expected {num_questions}")
                # Add fallback questions if needed
                questions.extend(self._generate_fallback_questions(num_questions - len(questions)))
            
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
            
        except Exception as e:
            print(f"Error in create_assessment: {e}")
            # Return a fallback assessment
            return self._create_fallback_assessment(lesson_id, num_questions)
    
    def _create_fallback_assessment(self, lesson_id: str, num_questions: int) -> Assessment:
        """Create a fallback assessment when LLM generation fails"""
        questions = self._generate_fallback_questions(num_questions)
        
        return Assessment(
            assessment_id=str(uuid.uuid4()),
            lesson_id=lesson_id,
            questions=questions,
            time_limit=num_questions * 2,
            passing_score=0.7,
            difficulty="medium"
        )
    
    def _generate_fallback_questions(self, num_questions: int) -> List[Dict[str, Any]]:
        """Generate fallback questions when LLM fails - with varied content"""
        fallback_templates = [
            {
                "question_text": "What is the key learning objective from this lesson?",
                "options": [
                    "Understanding core concepts",
                    "Memorizing facts", 
                    "Practical application",
                    "Theoretical knowledge"
                ],
                "correct_answer": "Understanding core concepts",
                "explanation": "The primary goal is to understand fundamental concepts that can be applied.",
            },
            {
                "question_text": "Which of the following best describes the main topic covered?",
                "options": [
                    "A foundational concept essential for advanced topics",
                    "A superficial overview of the subject",
                    "An outdated approach",
                    "A theoretical exercise"
                ],
                "correct_answer": "A foundational concept essential for advanced topics",
                "explanation": "This lesson provides foundational knowledge that builds toward more advanced topics.",
            },
            {
                "question_text": "How can you apply what you learned in a practical scenario?",
                "options": [
                    "By implementing the core principles in real-world situations",
                    "By memorizing all the definitions",
                    "By ignoring edge cases",
                    "By following only traditional approaches"
                ],
                "correct_answer": "By implementing the core principles in real-world situations",
                "explanation": "Practical application involves taking learned principles and implementing them effectively.",
            },
            {
                "question_text": "What is a critical takeaway from this lesson?",
                "options": [
                    "Mastering the fundamental concepts enables better problem-solving",
                    "The details don't matter much",
                    "One approach works for all scenarios",
                    "Practice is unnecessary"
                ],
                "correct_answer": "Mastering the fundamental concepts enables better problem-solving",
                "explanation": "Strong foundational understanding is critical for tackling complex problems.",
            },
            {
                "question_text": "Which skill would you develop through this lesson?",
                "options": [
                    "The ability to understand and apply core concepts",
                    "Memorization without understanding",
                    "Random problem-solving",
                    "Avoiding the subject matter"
                ],
                "correct_answer": "The ability to understand and apply core concepts",
                "explanation": "This lesson develops conceptual understanding and practical application skills.",
            },
        ]
        
        questions = []
        for i in range(num_questions):
            template = fallback_templates[i % len(fallback_templates)]
            questions.append({
                "question_id": str(uuid.uuid4()),
                "question_text": template["question_text"],
                "question_type": "multiple_choice",
                "options": template["options"],
                "correct_answer": template["correct_answer"],
                "explanation": template["explanation"],
                "difficulty": 2 + (i % 3),  # Vary difficulty from 2-4
                "points": 1,
                "tags": ["core_concepts", "practical_application"]
            })
        return questions

    async def _generate_questions(self, lesson_id: str, difficulty: str, 
                                 num_questions: int, question_types: List[str]) -> List[Dict[str, Any]]:
        """Generate questions using LLM"""
        
        prompt = f"""
        You are generating assessment questions for a lesson. Return ONLY a valid JSON array with exactly {num_questions} items. No extra text.
        
        Each item must be an object with these fields:
        - question_text: string
        - question_type: one of "multiple_choice", "short_answer", "true_false"
        - options: array of strings (required only for multiple_choice; omit or empty for others)
        - correct_answer: string
        - explanation: string
        - difficulty: integer from 1 to 5
        - points: integer from 1 to 5
        - tags: array of strings
        
        Lesson ID: {lesson_id}
        Difficulty: {difficulty}
        Question types to include: {', '.join(question_types)}
        """
        
        try:
            print(f"[Assessment] Attempting to generate {num_questions} {difficulty} questions for lesson {lesson_id}")
            response = await self.llm_service.generate_response(
                prompt,
                response_mime_type="application/json"
            )
            print(f"[Assessment] LLM response received: {len(response)} characters")
            questions = self._parse_questions_from_response(response, num_questions)
            print(f"[Assessment] Parsed {len(questions)} questions from LLM response")
        except Exception as e:
            print(f"[Assessment] ERROR: LLM question generation failed: {e}")
            import traceback
            traceback.print_exc()
            questions = []
        
        # Use fallback if LLM generation fails or returns too few questions
        if len(questions) < num_questions:
            fallback_count = num_questions - len(questions)
            print(f"[Assessment] Generating {fallback_count} fallback questions")
            questions.extend(self._generate_fallback_questions(fallback_count))
        
        return questions
    
    def _parse_questions_from_response(self, response: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse questions from LLM response with robust JSON-first strategy and heuristic fallback"""
        
        def normalize_question(item: Dict[str, Any]) -> Dict[str, Any]:
            qt = (
                item.get("question_text")
                or item.get("question")
                or item.get("text")
                or item.get("prompt")
                or ""
            )
            options_raw = item.get("options") or item.get("choices") or []
            options: List[str] = []
            for opt in options_raw:
                if isinstance(opt, dict):
                    val = opt.get("text") or opt.get("label") or opt.get("value") or str(opt)
                else:
                    val = str(opt)
                options.append(val)
            qtype = (
                item.get("question_type")
                or item.get("type")
                or ("multiple_choice" if options else "short_answer")
            )
            correct = (
                item.get("correct_answer")
                or item.get("answer")
                or item.get("correct")
                or ""
            )
            explanation = item.get("explanation") or item.get("rationale") or ""
            difficulty = item.get("difficulty", 3)
            if isinstance(difficulty, str):
                mapping = {"easy": 1, "medium": 3, "hard": 5}
                difficulty = mapping.get(difficulty.lower().strip(), 3)
            try:
                difficulty = int(difficulty)
            except Exception:
                difficulty = 3
            points = item.get("points", 1)
            try:
                points = int(points)
            except Exception:
                points = 1
            tags = item.get("tags") or item.get("topics") or []
            if not isinstance(tags, list):
                tags = [str(tags)]
            return {
                "question_id": str(uuid.uuid4()),
                "question_text": str(qt).strip(),
                "question_type": str(qtype).strip(),
                "options": options,
                "correct_answer": str(correct).strip(),
                "explanation": str(explanation).strip(),
                "difficulty": max(1, min(5, difficulty)),
                "points": max(1, min(5, points)),
                "tags": [str(t) for t in tags],
            }

        # 1) Try direct JSON parsing
        parsed: List[Dict[str, Any]] = []
        try:
            data = json.loads(response)
            if isinstance(data, dict):
                # Common keys where the array may live
                for key in ("questions", "items", "data", "quiz", "assessment"):
                    if key in data and isinstance(data[key], list):
                        data = data[key]
                        break
                # If still a dict, try interpreting as dict-of-questions
                if isinstance(data, dict):
                    values = list(data.values())
                    if values and all(isinstance(v, (dict, list)) for v in values):
                        # Flatten lists if needed and take first expected_count
                        flattened: List[Dict[str, Any]] = []
                        for v in values:
                            if isinstance(v, list):
                                flattened.extend(v)
                            else:
                                flattened.append(v)
                        data = flattened
            if isinstance(data, list):
                parsed = [normalize_question(item) for item in data[:expected_count]]
        except Exception:
            data = None

        # 2) Try extracting fenced JSON code block
        if not parsed:
            try:
                # Try language-tagged json/jsonc first
                match = re.search(r"```(?:json|jsonc)\s*(\[.*?\])\s*```", response, re.IGNORECASE | re.DOTALL)
                blocks = []
                if match:
                    blocks.append(match.group(1))
                else:
                    # Fallback: any fenced block, then try to parse an array from it
                    for m in re.finditer(r"```[a-zA-Z0-9_-]*\s*([\s\S]*?)\s*```", response, re.DOTALL):
                        blocks.append(m.group(1))
                for blk in blocks:
                    # If the whole block is a JSON array
                    try:
                        cand = blk.strip()
                        if cand:
                            # Try direct
                            cand_data = json.loads(cand)
                            if isinstance(cand_data, list):
                                parsed = [normalize_question(item) for item in cand_data[:expected_count]]
                                break
                    except Exception:
                        pass
                    # Try extracting the first array from the block
                    try:
                        s = blk.find("["); e = blk.rfind("]")
                        if s != -1 and e != -1 and e > s:
                            cand = blk[s:e+1]
                            cand_data = json.loads(cand)
                            if isinstance(cand_data, list):
                                parsed = [normalize_question(item) for item in cand_data[:expected_count]]
                                break
                    except Exception:
                        pass
            except Exception:
                pass

        # 3) Try naive bracket slicing if a JSON array is embedded
        if not parsed:
            try:
                start = response.find("[")
                end = response.rfind("]")
                if start != -1 and end != -1 and end > start:
                    data = json.loads(response[start : end + 1])
                    if isinstance(data, list):
                        parsed = [normalize_question(item) for item in data[:expected_count]]
            except Exception:
                pass

        if parsed:
            return parsed[:expected_count]

        # 4) Heuristic fallback: parse line-based formats
        def _preprocess_text(text: str) -> str:
            # Remove fenced code blocks markers
            text = re.sub(r"```[a-zA-Z0-9_-]*\s*", "", text)
            text = re.sub(r"\s*```\s*", "\n", text)
            # Remove bold/italic/code markers while preserving content
            text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
            text = re.sub(r"__(.*?)__", r"\1", text)
            text = re.sub(r"`(.*?)`", r"\1", text)
            # Normalize headings: drop leading #'s
            text = re.sub(r"^\s*#{1,6}\s*", "", text, flags=re.MULTILINE)
            # Insert newlines before anchors when they appear inline
            anchors = [
                r"(Question\s*\d+)",
                r"(Q\d+)",
                r"(Answer:)",
                r"(Correct\s*Answer:)",
                r"(Explanation:)",
                r"(Type:)",
                r"(Difficulty:)",
                r"(Points:)",
            ]
            for pat in anchors:
                text = re.sub(rf"\s+{pat}", r"\n\1", text, flags=re.IGNORECASE)
            # Put options on separate lines if inline
            text = re.sub(r"\s+([A-Da-d][\).]\s+)", r"\n\1", text)
            # Normalize line endings
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            return text

        raw_text = _preprocess_text(response)
        questions: List[Dict[str, Any]] = []
        lines = raw_text.split("\n")
        current_question: Optional[Dict[str, Any]] = None

        question_start_pattern = re.compile(r"^(?:#{1,6}\s*)?(?:Question\s*\d+\b|Q\d+\b|\d+[\.)])", re.IGNORECASE)
        option_pattern = re.compile(r"^(?:[A-Da-d][\).]|[-*])\s+(.*)")
        inline_options_pattern = re.compile(r"([A-Da-d][\).])\s+([^A-Da-d]+?)(?=(?:\s+[A-Da-d][\).]\s+|$))")

        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            if question_start_pattern.match(line):
                if current_question:
                    questions.append(current_question)
                # Derive type if mentioned on the same line
                qtype = "multiple_choice"
                low = line.lower()
                if "short answer" in low:
                    qtype = "short_answer"
                elif "true/false" in low or "true or false" in low:
                    qtype = "true_false"
                current_question = {
                    "question_id": str(uuid.uuid4()),
                    "question_text": line,
                    "question_type": qtype,
                    "options": [],
                    "correct_answer": "",
                    "explanation": "",
                    "difficulty": 3,
                    "points": 1,
                    "tags": [],
                }
                continue

            if current_question:
                m = option_pattern.match(line)
                if m:
                    current_question["options"].append(m.group(1).strip())
                    continue
                # Extract inline options if present on the same line
                for om in inline_options_pattern.finditer(line):
                    opt_text = om.group(2).strip()
                    if opt_text:
                        current_question["options"].append(opt_text)
                # Detect type lines like "Multiple Choice:" / "Short Answer:" / "True/False:"
                low_line = line.lower()
                if low_line.startswith("multiple choice:") or low_line.startswith("multiple-choice:"):
                    current_question["question_type"] = "multiple_choice"
                    # If line also contains the prompt after the label, capture it
                    parts = line.split(":", 1)
                    if len(parts) == 2 and parts[1].strip():
                        current_question["question_text"] = parts[1].strip()
                    continue
                if low_line.startswith("short answer:"):
                    current_question["question_type"] = "short_answer"
                    parts = line.split(":", 1)
                    if len(parts) == 2 and parts[1].strip():
                        current_question["question_text"] = parts[1].strip()
                    continue
                if low_line.startswith("true/false:") or low_line.startswith("true or false:"):
                    current_question["question_type"] = "true_false"
                    parts = line.split(":", 1)
                    if len(parts) == 2 and parts[1].strip():
                        current_question["question_text"] = parts[1].strip()
                    continue
                if line.lower().startswith("answer:") or line.lower().startswith("correct answer:") or line.lower().startswith("correct:"):
                    current_question["correct_answer"] = line.split(":", 1)[1].strip() if ":" in line else line
                    continue
                if line.lower().startswith("explanation:"):
                    current_question["explanation"] = line.split(":", 1)[1].strip() if ":" in line else line
                    continue
                if line.lower().startswith("type:"):
                    current_question["question_type"] = line.split(":", 1)[1].strip()
                    continue
                if line.lower().startswith("difficulty:"):
                    try:
                        current_question["difficulty"] = int(line.split(":", 1)[1].strip())
                    except Exception:
                        current_question["difficulty"] = 3
                    continue
                if line.lower().startswith("points:"):
                    try:
                        current_question["points"] = int(line.split(":", 1)[1].strip())
                    except Exception:
                        current_question["points"] = 1
                    continue
                # If it's a plain line and current question text is just a heading, use this as the prompt
                try:
                    head = current_question["question_text"].strip().lower()
                    if re.match(r"^(question\s*\d+\b|q\d+\b)$", head) and line:
                        current_question["question_text"] = line
                except Exception:
                    pass

        if current_question:
            questions.append(current_question)

        result = questions[:expected_count]
        if not result:
            try:
                preview = response[:500].replace("\n", " ")
                print(f"[Assessment] WARNING: Parser produced 0 questions. Response preview: {preview}")
            except Exception:
                pass
        return result
    
    async def evaluate_assessment(self, assessment_id: str, user_answers: List[Dict[str, Any]], 
                                 user_id: str = None) -> AssessmentResult:
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
        """Check short answer with better fuzzy matching"""
        import re
        
        # Clean the text
        user_clean = re.sub(r'[^\w\s]', '', user_answer.lower())
        correct_clean = re.sub(r'[^\w\s]', '', correct_answer.lower())
        user_words = set(user_clean.split())
        correct_words = set(correct_clean.split())
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'but'}
        user_words = user_words - stop_words
        correct_words = correct_words - stop_words
        
        if not correct_words:  # Avoid division by zero
            return False
        
        # Calculate overlap
        overlap = len(user_words.intersection(correct_words))
        similarity = overlap / len(correct_words)
        
        # Consider correct if at least 60% of key terms are present
        return similarity >= 0.6
        
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
