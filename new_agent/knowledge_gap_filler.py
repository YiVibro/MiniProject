"""
Automatic Knowledge Gap Filling System
======================================

This module implements automatic knowledge gap filling that identifies missing
foundational concepts and provides immediate review lessons during learning sessions.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
from dataclasses import dataclass
from enum import Enum

class GapType(Enum):
    """Types of knowledge gaps"""
    FOUNDATIONAL = "foundational"
    PREREQUISITE = "prerequisite"
    CONCEPTUAL = "conceptual"
    PROCEDURAL = "procedural"
    APPLICATION = "application"

class GapSeverity(Enum):
    """Severity levels for knowledge gaps"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class KnowledgeGap:
    """Identified knowledge gap"""
    gap_id: str
    concept: str
    gap_type: GapType
    severity: GapSeverity
    description: str
    missing_prerequisites: List[str]
    impact_on_learning: str
    suggested_remediation: List[str]
    estimated_time_to_fill: int  # minutes
    priority_score: float  # 0.0 to 1.0

@dataclass
class GapFillingLesson:
    """Lesson designed to fill a knowledge gap"""
    lesson_id: str
    gap_id: str
    title: str
    content: str
    difficulty: str
    duration: int  # minutes
    learning_objectives: List[str]
    prerequisites: List[str]
    assessment_questions: List[str]
    practice_exercises: List[str]

class KnowledgeGapFiller:
    """Automatic knowledge gap filling system"""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.gap_database = {}  # concept -> List[KnowledgeGap]
        self.filling_lessons = {}  # gap_id -> GapFillingLesson
        self.concept_dependencies = {}  # concept -> List[prerequisites]
        
        # Initialize concept dependencies
        self._initialize_concept_dependencies()
    
    def _initialize_concept_dependencies(self):
        """Initialize concept dependency graph"""
        
        # Example dependencies - in practice, this would be loaded from a knowledge base
        self.concept_dependencies = {
            "calculus": ["algebra", "trigonometry", "functions"],
            "algebra": ["arithmetic", "basic_math"],
            "trigonometry": ["geometry", "algebra"],
            "functions": ["algebra", "graphing"],
            "derivatives": ["limits", "functions"],
            "integrals": ["derivatives", "antiderivatives"],
            "linear_algebra": ["algebra", "vectors"],
            "probability": ["statistics", "combinatorics"],
            "statistics": ["probability", "data_analysis"],
            "machine_learning": ["statistics", "linear_algebra", "programming"]
        }
    
    async def identify_knowledge_gaps(self, user_responses: List[str], 
                                    current_concept: str, 
                                    user_id: str) -> List[KnowledgeGap]:
        """Identify knowledge gaps from user responses"""
        
        try:
            # Analyze responses for gap indicators
            gap_indicators = await self._analyze_gap_indicators(user_responses, current_concept)
            
            # Identify specific gaps
            gaps = []
            for indicator in gap_indicators:
                gap = await self._create_knowledge_gap(indicator, current_concept, user_id)
                if gap:
                    gaps.append(gap)
            
            # Prioritize gaps by severity and impact
            prioritized_gaps = self._prioritize_gaps(gaps)
            
            return prioritized_gaps
            
        except Exception as e:
            print(f"Error identifying knowledge gaps: {e}")
            return []
    
    async def _analyze_gap_indicators(self, user_responses: List[str], 
                                     current_concept: str) -> List[Dict[str, Any]]:
        """Analyze user responses for gap indicators"""
        
        prompt = f"""
        Analyze these user responses for knowledge gaps in the concept "{current_concept}":
        
        User Responses: {user_responses}
        
        Identify specific knowledge gaps by looking for:
        1. Missing foundational concepts
        2. Incorrect understanding of prerequisites
        3. Conceptual misunderstandings
        4. Procedural knowledge gaps
        5. Application difficulties
        
        For each gap found, provide:
        - Gap type (foundational, prerequisite, conceptual, procedural, application)
        - Severity (low, medium, high, critical)
        - Description of the gap
        - Missing prerequisites
        - Impact on learning
        - Suggested remediation steps
        
        Format as structured analysis.
        """
        
        try:
            analysis_text = await self.llm_service.generate_response(prompt)
            return self._parse_gap_indicators(analysis_text)
        except Exception as e:
            print(f"Error analyzing gap indicators: {e}")
            return []
    
    def _parse_gap_indicators(self, analysis_text: str) -> List[Dict[str, Any]]:
        """Parse gap indicators from analysis text"""
        
        indicators = []
        lines = analysis_text.split('\n')
        
        current_indicator = None
        for line in lines:
            line = line.strip()
            if line and (line.startswith(('1.', '2.', '3.', '4.', '5.')) or 
                        line.startswith(('Gap', 'Issue', 'Problem'))):
                if current_indicator:
                    indicators.append(current_indicator)
                
                current_indicator = {
                    "gap_type": "foundational",
                    "severity": "medium",
                    "description": line,
                    "missing_prerequisites": [],
                    "impact": "moderate",
                    "remediation": []
                }
            elif current_indicator and line:
                if "type:" in line.lower():
                    gap_type = line.split(':')[1].strip().lower()
                    current_indicator["gap_type"] = gap_type
                elif "severity:" in line.lower():
                    severity = line.split(':')[1].strip().lower()
                    current_indicator["severity"] = severity
                elif "prerequisites:" in line.lower():
                    prereqs = line.split(':')[1].strip().split(',')
                    current_indicator["missing_prerequisites"] = [p.strip() for p in prereqs]
                elif "impact:" in line.lower():
                    impact = line.split(':')[1].strip()
                    current_indicator["impact"] = impact
                else:
                    current_indicator["remediation"].append(line)
        
        if current_indicator:
            indicators.append(current_indicator)
        
        return indicators
    
    async def _create_knowledge_gap(self, indicator: Dict[str, Any], 
                                   current_concept: str, user_id: str) -> Optional[KnowledgeGap]:
        """Create knowledge gap from indicator"""
        
        try:
            gap_id = f"{user_id}_{current_concept}_{datetime.now().timestamp()}"
            
            # Determine gap type
            gap_type = self._determine_gap_type(indicator["gap_type"])
            
            # Determine severity
            severity = self._determine_severity(indicator["severity"])
            
            # Calculate priority score
            priority_score = self._calculate_priority_score(indicator, current_concept)
            
            # Estimate time to fill gap
            estimated_time = self._estimate_filling_time(indicator)
            
            return KnowledgeGap(
                gap_id=gap_id,
                concept=current_concept,
                gap_type=gap_type,
                severity=severity,
                description=indicator["description"],
                missing_prerequisites=indicator["missing_prerequisites"],
                impact_on_learning=indicator["impact"],
                suggested_remediation=indicator["remediation"],
                estimated_time_to_fill=estimated_time,
                priority_score=priority_score
            )
            
        except Exception as e:
            print(f"Error creating knowledge gap: {e}")
            return None
    
    def _determine_gap_type(self, gap_type_str: str) -> GapType:
        """Determine gap type from string"""
        
        gap_type_mapping = {
            "foundational": GapType.FOUNDATIONAL,
            "prerequisite": GapType.PREREQUISITE,
            "conceptual": GapType.CONCEPTUAL,
            "procedural": GapType.PROCEDURAL,
            "application": GapType.APPLICATION
        }
        
        return gap_type_mapping.get(gap_type_str.lower(), GapType.FOUNDATIONAL)
    
    def _determine_severity(self, severity_str: str) -> GapSeverity:
        """Determine severity from string"""
        
        severity_mapping = {
            "low": GapSeverity.LOW,
            "medium": GapSeverity.MEDIUM,
            "high": GapSeverity.HIGH,
            "critical": GapSeverity.CRITICAL
        }
        
        return severity_mapping.get(severity_str.lower(), GapSeverity.MEDIUM)
    
    def _calculate_priority_score(self, indicator: Dict[str, Any], 
                                current_concept: str) -> float:
        """Calculate priority score for gap"""
        
        base_score = 0.5
        
        # Severity multiplier
        severity_multipliers = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8,
            "critical": 1.0
        }
        severity_mult = severity_multipliers.get(indicator["severity"], 0.6)
        
        # Impact multiplier
        impact_multipliers = {
            "low": 0.3,
            "moderate": 0.6,
            "high": 0.8,
            "critical": 1.0
        }
        impact_mult = impact_multipliers.get(indicator["impact"], 0.6)
        
        # Prerequisite importance
        prereq_importance = len(indicator["missing_prerequisites"]) * 0.1
        
        priority_score = base_score * severity_mult * impact_mult + prereq_importance
        
        return min(1.0, max(0.0, priority_score))
    
    def _estimate_filling_time(self, indicator: Dict[str, Any]) -> int:
        """Estimate time needed to fill gap"""
        
        base_time = 15  # 15 minutes base
        
        # Adjust based on gap type
        type_multipliers = {
            "foundational": 1.5,
            "prerequisite": 1.2,
            "conceptual": 1.0,
            "procedural": 0.8,
            "application": 1.3
        }
        type_mult = type_multipliers.get(indicator["gap_type"], 1.0)
        
        # Adjust based on severity
        severity_multipliers = {
            "low": 0.5,
            "medium": 1.0,
            "high": 1.5,
            "critical": 2.0
        }
        severity_mult = severity_multipliers.get(indicator["severity"], 1.0)
        
        # Adjust based on number of prerequisites
        prereq_mult = 1.0 + (len(indicator["missing_prerequisites"]) * 0.2)
        
        estimated_time = int(base_time * type_mult * severity_mult * prereq_mult)
        
        return min(120, max(5, estimated_time))  # Between 5 and 120 minutes
    
    def _prioritize_gaps(self, gaps: List[KnowledgeGap]) -> List[KnowledgeGap]:
        """Prioritize gaps by importance and urgency"""
        
        # Sort by priority score (descending)
        return sorted(gaps, key=lambda gap: gap.priority_score, reverse=True)
    
    async def create_gap_filling_lesson(self, gap: KnowledgeGap) -> GapFillingLesson:
        """Create a lesson to fill a specific knowledge gap"""
        
        try:
            lesson_id = f"gap_fill_{gap.gap_id}"
            
            # Generate lesson content
            lesson_content = await self._generate_gap_filling_content(gap)
            
            # Generate assessment questions
            assessment_questions = await self._generate_assessment_questions(gap)
            
            # Generate practice exercises
            practice_exercises = await self._generate_practice_exercises(gap)
            
            # Create lesson
            lesson = GapFillingLesson(
                lesson_id=lesson_id,
                gap_id=gap.gap_id,
                title=f"Filling Knowledge Gap: {gap.concept}",
                content=lesson_content,
                difficulty=self._determine_lesson_difficulty(gap),
                duration=gap.estimated_time_to_fill,
                learning_objectives=self._extract_learning_objectives(gap),
                prerequisites=gap.missing_prerequisites,
                assessment_questions=assessment_questions,
                practice_exercises=practice_exercises
            )
            
            # Store lesson
            self.filling_lessons[gap.gap_id] = lesson
            
            return lesson
            
        except Exception as e:
            print(f"Error creating gap filling lesson: {e}")
            return None
    
    async def _generate_gap_filling_content(self, gap: KnowledgeGap) -> str:
        """Generate content for gap filling lesson"""
        
        prompt = f"""
        Create a focused lesson to fill this knowledge gap:
        
        Concept: {gap.concept}
        Gap Type: {gap.gap_type.value}
        Description: {gap.description}
        Missing Prerequisites: {', '.join(gap.missing_prerequisites)}
        Impact: {gap.impact_on_learning}
        
        Create a lesson that:
        1. Addresses the specific gap
        2. Covers missing prerequisites
        3. Uses clear, simple explanations
        4. Includes examples and analogies
        5. Provides step-by-step guidance
        6. Is focused and concise (for {gap.estimated_time_to_fill} minutes)
        
        Format as a structured lesson with clear sections.
        """
        
        return await self.llm_service.generate_response(prompt)
    
    async def _generate_assessment_questions(self, gap: KnowledgeGap) -> List[str]:
        """Generate assessment questions for gap filling lesson"""
        
        prompt = f"""
        Create 3-5 assessment questions for this knowledge gap:
        
        Concept: {gap.concept}
        Gap Type: {gap.gap_type.value}
        Missing Prerequisites: {', '.join(gap.missing_prerequisites)}
        
        Questions should:
        1. Test understanding of the gap
        2. Verify prerequisite knowledge
        3. Be appropriate for the gap severity
        4. Include different question types (multiple choice, short answer, etc.)
        
        Format as a list of questions.
        """
        
        questions_text = await self.llm_service.generate_response(prompt)
        return self._parse_questions(questions_text)
    
    async def _generate_practice_exercises(self, gap: KnowledgeGap) -> List[str]:
        """Generate practice exercises for gap filling lesson"""
        
        prompt = f"""
        Create 3-5 practice exercises for this knowledge gap:
        
        Concept: {gap.concept}
        Gap Type: {gap.gap_type.value}
        Missing Prerequisites: {', '.join(gap.missing_prerequisites)}
        
        Exercises should:
        1. Practice the specific gap area
        2. Reinforce prerequisite knowledge
        3. Be progressive in difficulty
        4. Include solutions and explanations
        
        Format as a list of exercises.
        """
        
        exercises_text = await self.llm_service.generate_response(prompt)
        return self._parse_exercises(exercises_text)
    
    def _parse_questions(self, questions_text: str) -> List[str]:
        """Parse questions from text"""
        
        questions = []
        lines = questions_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith(('1.', '2.', '3.', '4.', '5.')) or 
                        line.startswith(('Q', 'Question'))):
                questions.append(line)
        
        return questions[:5]  # Limit to 5 questions
    
    def _parse_exercises(self, exercises_text: str) -> List[str]:
        """Parse exercises from text"""
        
        exercises = []
        lines = exercises_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith(('1.', '2.', '3.', '4.', '5.')) or 
                        line.startswith(('Exercise', 'Practice'))):
                exercises.append(line)
        
        return exercises[:5]  # Limit to 5 exercises
    
    def _determine_lesson_difficulty(self, gap: KnowledgeGap) -> str:
        """Determine lesson difficulty based on gap"""
        
        if gap.severity == GapSeverity.CRITICAL:
            return "easy"
        elif gap.severity == GapSeverity.HIGH:
            return "easy"
        elif gap.severity == GapSeverity.MEDIUM:
            return "medium"
        else:
            return "medium"
    
    def _extract_learning_objectives(self, gap: KnowledgeGap) -> List[str]:
        """Extract learning objectives from gap"""
        
        objectives = [
            f"Understand the foundational concept of {gap.concept}",
            f"Master the prerequisites: {', '.join(gap.missing_prerequisites)}",
            f"Apply the concept in practical scenarios"
        ]
        
        if gap.gap_type == GapType.CONCEPTUAL:
            objectives.append("Develop conceptual understanding through examples")
        elif gap.gap_type == GapType.PROCEDURAL:
            objectives.append("Learn step-by-step procedures")
        elif gap.gap_type == GapType.APPLICATION:
            objectives.append("Practice real-world applications")
        
        return objectives
    
    async def get_gap_filling_recommendations(self, user_id: str, 
                                            current_concept: str) -> Dict[str, Any]:
        """Get recommendations for filling knowledge gaps"""
        
        # Get user's knowledge gaps
        gaps = self.gap_database.get(f"{user_id}_{current_concept}", [])
        
        if not gaps:
            return {
                "status": "no_gaps",
                "message": "No knowledge gaps identified",
                "recommendations": []
            }
        
        # Get high-priority gaps
        high_priority_gaps = [gap for gap in gaps if gap.priority_score > 0.7]
        
        if not high_priority_gaps:
            return {
                "status": "low_priority",
                "message": "Knowledge gaps are low priority",
                "recommendations": []
            }
        
        # Create gap filling lessons for high-priority gaps
        recommendations = []
        for gap in high_priority_gaps[:3]:  # Limit to 3 recommendations
            lesson = await self.create_gap_filling_lesson(gap)
            if lesson:
                recommendations.append({
                    "gap_id": gap.gap_id,
                    "concept": gap.concept,
                    "gap_type": gap.gap_type.value,
                    "severity": gap.severity.value,
                    "lesson": {
                        "title": lesson.title,
                        "duration": lesson.duration,
                        "difficulty": lesson.difficulty,
                        "objectives": lesson.learning_objectives
                    },
                    "priority_score": gap.priority_score
                })
        
        return {
            "status": "gaps_identified",
            "message": f"Found {len(high_priority_gaps)} high-priority knowledge gaps",
            "recommendations": recommendations,
            "total_gaps": len(gaps),
            "high_priority_count": len(high_priority_gaps)
        }
    
    def store_gap(self, user_id: str, concept: str, gap: KnowledgeGap):
        """Store knowledge gap in database"""
        
        key = f"{user_id}_{concept}"
        if key not in self.gap_database:
            self.gap_database[key] = []
        
        self.gap_database[key].append(gap)
    
    def get_user_gaps(self, user_id: str, concept: str) -> List[KnowledgeGap]:
        """Get all knowledge gaps for a user and concept"""
        
        key = f"{user_id}_{concept}"
        return self.gap_database.get(key, [])
    
    def get_gap_filling_lesson(self, gap_id: str) -> Optional[GapFillingLesson]:
        """Get gap filling lesson by gap ID"""
        
        return self.filling_lessons.get(gap_id)

