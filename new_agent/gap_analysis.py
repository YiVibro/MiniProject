"""
Real-time Gap Analysis System
============================

This module implements real-time gap analysis using NLP-based misconception
classification to identify learning gaps and provide targeted interventions.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re
from pydantic import BaseModel, Field
from llm_service import GoogleLLMService

class Misconception(BaseModel):
    """Model for identified misconceptions"""
    misconception_id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    concept: str
    misconception_type: str
    user_response: str
    correct_understanding: str
    confidence: float = Field(ge=0.0, le=1.0)
    severity: str = Field(..., description="low, medium, high")
    suggested_intervention: str
    timestamp: datetime = Field(default_factory=datetime.now)

class LearningGap(BaseModel):
    """Model for identified learning gaps"""
    gap_id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    concept: str
    gap_type: str = Field(..., description="knowledge, skill, application, understanding")
    description: str
    user_responses: List[str]
    correct_answers: List[str]
    confidence: float = Field(ge=0.0, le=1.0)
    priority: str = Field(..., description="low, medium, high, critical")
    suggested_remediation: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)

class GapAnalysisResult(BaseModel):
    """Result of gap analysis"""
    user_id: str
    session_id: str
    misconceptions: List[Misconception]
    learning_gaps: List[LearningGap]
    overall_confidence: float
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    recommendations: List[str]

class GapAnalysisSystem:
    """Real-time gap analysis system with NLP-based misconception classification"""
    
    def __init__(self, llm_service: GoogleLLMService):
        self.llm_service = llm_service
        self.misconception_patterns = {
            "conceptual": ["doesn't understand", "confused about", "misunderstands"],
            "procedural": ["wrong steps", "incorrect method", "wrong approach"],
            "factual": ["incorrect fact", "wrong information", "false statement"],
            "application": ["can't apply", "wrong application", "misapplied"]
        }
        
        self.gap_indicators = {
            "knowledge": ["don't know", "unfamiliar", "never heard", "not sure"],
            "skill": ["can't do", "don't know how", "struggling with", "difficult"],
            "application": ["can't apply", "don't see how", "not relevant", "unclear"],
            "understanding": ["don't understand", "confused", "unclear", "not clear"]
        }
    
    async def analyze_responses(self, user_responses: List[str], 
                              correct_answers: List[str], 
                              concept: str, 
                              user_id: str, 
                              session_id: str) -> GapAnalysisResult:
        """Analyze user responses for misconceptions and learning gaps"""
        
        try:
            # Classify misconceptions
            misconceptions = await self._classify_misconceptions(
                user_responses, correct_answers, concept
            )
            
            # Identify learning gaps
            learning_gaps = await self._identify_learning_gaps(
                user_responses, correct_answers, concept
            )
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(misconceptions, learning_gaps)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(misconceptions, learning_gaps)
            
            return GapAnalysisResult(
                user_id=user_id,
                session_id=session_id,
                misconceptions=misconceptions,
                learning_gaps=learning_gaps,
                overall_confidence=overall_confidence,
                recommendations=recommendations
            )
            
        except Exception as e:
            # Return empty result on error
            return GapAnalysisResult(
                user_id=user_id,
                session_id=session_id,
                misconceptions=[],
                learning_gaps=[],
                overall_confidence=0.0,
                recommendations=[f"Analysis error: {str(e)}"]
            )
    
    async def _classify_misconceptions(self, user_responses: List[str], 
                                     correct_answers: List[str], 
                                     concept: str) -> List[Misconception]:
        """Classify misconceptions using NLP analysis"""
        
        misconceptions = []
        
        for i, (user_response, correct_answer) in enumerate(zip(user_responses, correct_answers)):
            if not self._is_response_correct(user_response, correct_answer):
                # Analyze the specific misconception
                misconception_analysis = await self._analyze_misconception(
                    user_response, correct_answer, concept
                )
                
                if misconception_analysis:
                    misconception = Misconception(
                        concept=concept,
                        misconception_type=misconception_analysis["type"],
                        user_response=user_response,
                        correct_understanding=correct_answer,
                        confidence=misconception_analysis["confidence"],
                        severity=misconception_analysis["severity"],
                        suggested_intervention=misconception_analysis["intervention"]
                    )
                    misconceptions.append(misconception)
        
        return misconceptions
    
    async def _analyze_misconception(self, user_response: str, correct_answer: str, 
                                    concept: str) -> Optional[Dict[str, Any]]:
        """Analyze a specific misconception"""
        
        prompt = f"""
        Analyze this misconception for the concept "{concept}":
        
        User Response: "{user_response}"
        Correct Answer: "{correct_answer}"
        
        Classify the misconception type and provide analysis:
        1. Misconception Type: conceptual, procedural, factual, or application
        2. Confidence Level: 0.0 to 1.0
        3. Severity: low, medium, or high
        4. Suggested Intervention: specific action to address this misconception
        
        Format as structured analysis.
        """
        
        try:
            analysis_text = await self.llm_service.generate_response(prompt)
            return self._parse_misconception_analysis(analysis_text)
        except Exception:
            return None
    
    def _parse_misconception_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse misconception analysis from LLM response"""
        
        # Extract misconception type
        misconception_type = "conceptual"  # Default
        if "procedural" in analysis_text.lower():
            misconception_type = "procedural"
        elif "factual" in analysis_text.lower():
            misconception_type = "factual"
        elif "application" in analysis_text.lower():
            misconception_type = "application"
        
        # Extract confidence (look for numbers between 0 and 1)
        confidence = 0.7  # Default
        confidence_match = re.search(r'(\d+\.?\d*)', analysis_text)
        if confidence_match:
            try:
                confidence = float(confidence_match.group(1))
                if confidence > 1.0:
                    confidence = confidence / 100  # Convert percentage to decimal
            except ValueError:
                pass
        
        # Extract severity
        severity = "medium"  # Default
        if "high" in analysis_text.lower():
            severity = "high"
        elif "low" in analysis_text.lower():
            severity = "low"
        
        # Extract intervention (look for intervention-related text)
        intervention = "Review the concept and practice with examples"
        intervention_match = re.search(r'intervention[:\s]+(.+)', analysis_text, re.IGNORECASE)
        if intervention_match:
            intervention = intervention_match.group(1).strip()
        
        return {
            "type": misconception_type,
            "confidence": min(max(confidence, 0.0), 1.0),
            "severity": severity,
            "intervention": intervention
        }
    
    async def _identify_learning_gaps(self, user_responses: List[str], 
                                    correct_answers: List[str], 
                                    concept: str) -> List[LearningGap]:
        """Identify learning gaps from user responses"""
        
        learning_gaps = []
        
        # Analyze patterns in responses
        gap_analysis = await self._analyze_learning_gaps(user_responses, correct_answers, concept)
        
        if gap_analysis:
            for gap_data in gap_analysis:
                learning_gap = LearningGap(
                    concept=concept,
                    gap_type=gap_data["type"],
                    description=gap_data["description"],
                    user_responses=user_responses,
                    correct_answers=correct_answers,
                    confidence=gap_data["confidence"],
                    priority=gap_data["priority"],
                    suggested_remediation=gap_data["remediation"]
                )
                learning_gaps.append(learning_gap)
        
        return learning_gaps
    
    async def _analyze_learning_gaps(self, user_responses: List[str], 
                                   correct_answers: List[str], 
                                   concept: str) -> List[Dict[str, Any]]:
        """Analyze learning gaps using NLP"""
        
        prompt = f"""
        Analyze these user responses for learning gaps in the concept "{concept}":
        
        User Responses: {user_responses}
        Correct Answers: {correct_answers}
        
        Identify specific learning gaps:
        1. Gap Type: knowledge, skill, application, or understanding
        2. Description: What specific gap exists
        3. Confidence: 0.0 to 1.0
        4. Priority: low, medium, high, or critical
        5. Remediation: Specific steps to address the gap
        
        Focus on patterns and underlying issues, not just wrong answers.
        """
        
        try:
            analysis_text = await self.llm_service.generate_response(prompt)
            return self._parse_gap_analysis(analysis_text)
        except Exception:
            return []
    
    def _parse_gap_analysis(self, analysis_text: str) -> List[Dict[str, Any]]:
        """Parse gap analysis from LLM response"""
        
        gaps = []
        lines = analysis_text.split('\n')
        
        current_gap = None
        for line in lines:
            line = line.strip()
            if line and (line.startswith(('1.', '2.', '3.', '4.', '5.')) or 
                        line.startswith(('Gap', 'Issue', 'Problem'))):
                if current_gap:
                    gaps.append(current_gap)
                
                current_gap = {
                    "type": "knowledge",  # Default
                    "description": line,
                    "confidence": 0.7,
                    "priority": "medium",
                    "remediation": []
                }
            elif current_gap and line:
                if "confidence" in line.lower() or "priority" in line.lower():
                    # Extract confidence and priority
                    if "high" in line.lower():
                        current_gap["priority"] = "high"
                    elif "low" in line.lower():
                        current_gap["priority"] = "low"
                    elif "critical" in line.lower():
                        current_gap["priority"] = "critical"
                else:
                    current_gap["remediation"].append(line)
        
        if current_gap:
            gaps.append(current_gap)
        
        return gaps[:3]  # Limit to 3 gaps
    
    def _is_response_correct(self, user_response: str, correct_answer: str) -> bool:
        """Check if user response is correct"""
        return user_response.lower().strip() == correct_answer.lower().strip()
    
    def _calculate_overall_confidence(self, misconceptions: List[Misconception], 
                                    learning_gaps: List[LearningGap]) -> float:
        """Calculate overall confidence in analysis"""
        
        if not misconceptions and not learning_gaps:
            return 0.0
        
        total_confidence = 0.0
        count = 0
        
        for misconception in misconceptions:
            total_confidence += misconception.confidence
            count += 1
        
        for gap in learning_gaps:
            total_confidence += gap.confidence
            count += 1
        
        return total_confidence / count if count > 0 else 0.0
    
    async def _generate_recommendations(self, misconceptions: List[Misconception], 
                                      learning_gaps: List[LearningGap]) -> List[str]:
        """Generate targeted recommendations based on analysis"""
        
        recommendations = []
        
        # Recommendations based on misconceptions
        if misconceptions:
            high_severity_misconceptions = [m for m in misconceptions if m.severity == "high"]
            if high_severity_misconceptions:
                recommendations.append("Address high-severity misconceptions immediately with targeted interventions")
            
            conceptual_misconceptions = [m for m in misconceptions if m.misconception_type == "conceptual"]
            if conceptual_misconceptions:
                recommendations.append("Focus on building conceptual understanding with visual aids and examples")
        
        # Recommendations based on learning gaps
        if learning_gaps:
            critical_gaps = [g for g in learning_gaps if g.priority == "critical"]
            if critical_gaps:
                recommendations.append("Prioritize addressing critical learning gaps before advancing")
            
            knowledge_gaps = [g for g in learning_gaps if g.gap_type == "knowledge"]
            if knowledge_gaps:
                recommendations.append("Provide foundational knowledge review and reinforcement")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Continue with current learning approach and monitor progress")
        
        return recommendations
    
    async def get_gap_analysis_summary(self, result: GapAnalysisResult) -> str:
        """Generate human-readable summary of gap analysis"""
        
        summary = f"""
# 📊 Learning Gap Analysis Summary

## 🔍 Analysis Overview
- **User ID:** {result.user_id}
- **Session ID:** {result.session_id}
- **Analysis Confidence:** {result.overall_confidence:.1%}
- **Timestamp:** {result.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## ❌ Misconceptions Identified ({len(result.misconceptions)})
"""
        
        for i, misconception in enumerate(result.misconceptions, 1):
            summary += f"""
**{i}. {misconception.concept}**
- Type: {misconception.misconception_type.title()}
- Severity: {misconception.severity.title()}
- User Response: "{misconception.user_response}"
- Correct Understanding: "{misconception.correct_understanding}"
- Intervention: {misconception.suggested_intervention}
"""
        
        summary += f"""
## 🎯 Learning Gaps Identified ({len(result.learning_gaps)})
"""
        
        for i, gap in enumerate(result.learning_gaps, 1):
            summary += f"""
**{i}. {gap.concept}**
- Type: {gap.gap_type.title()}
- Priority: {gap.priority.title()}
- Description: {gap.description}
- Remediation: {', '.join(gap.suggested_remediation[:2])}
"""
        
        summary += f"""
## 💡 Recommendations
"""
        
        for i, recommendation in enumerate(result.recommendations, 1):
            summary += f"{i}. {recommendation}\n"
        
        return summary

