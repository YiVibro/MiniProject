"""
Smart Learning Curve Tracking System
====================================

This module implements real-time learning curve tracking that detects student
struggles and automatically adjusts content difficulty in real-time.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from pydantic import BaseModel, Field
from dataclasses import dataclass
from enum import Enum

class StruggleType(Enum):
    """Types of learning struggles"""
    CONCEPTUAL = "conceptual"
    PROCEDURAL = "procedural"
    APPLICATION = "application"
    RETENTION = "retention"
    ENGAGEMENT = "engagement"

class DifficultyLevel(Enum):
    """Difficulty levels"""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"

@dataclass
class LearningPoint:
    """Individual learning data point"""
    timestamp: datetime
    concept: str
    difficulty: DifficultyLevel
    performance: float  # 0.0 to 1.0
    time_spent: int  # minutes
    attempts: int
    engagement: float  # 0.0 to 1.0
    struggle_indicators: List[StruggleType]

@dataclass
class LearningCurve:
    """Learning curve for a concept"""
    concept: str
    data_points: List[LearningPoint]
    trend: str  # "improving", "plateauing", "declining", "volatile"
    current_difficulty: DifficultyLevel
    recommended_difficulty: DifficultyLevel
    confidence: float
    last_updated: datetime

class LearningCurveTracker:
    """Tracks learning curves and adjusts difficulty in real-time"""
    
    def __init__(self):
        self.learning_curves = {}  # concept -> LearningCurve
        self.struggle_thresholds = {
            StruggleType.CONCEPTUAL: 0.3,
            StruggleType.PROCEDURAL: 0.4,
            StruggleType.APPLICATION: 0.35,
            StruggleType.RETENTION: 0.25,
            StruggleType.ENGAGEMENT: 0.2
        }
        self.performance_windows = {
            "short": 5,  # last 5 attempts
            "medium": 10,  # last 10 attempts
            "long": 20  # last 20 attempts
        }
    
    def add_learning_point(self, user_id: str, concept: str, 
                          performance: float, time_spent: int, 
                          attempts: int, engagement: float) -> LearningPoint:
        """Add a new learning data point"""
        
        # Detect struggle indicators
        struggle_indicators = self._detect_struggle_indicators(
            performance, time_spent, attempts, engagement
        )
        
        # Determine current difficulty
        current_difficulty = self._determine_difficulty_from_performance(performance)
        
        # Create learning point
        learning_point = LearningPoint(
            timestamp=datetime.now(),
            concept=concept,
            difficulty=current_difficulty,
            performance=performance,
            time_spent=time_spent,
            attempts=attempts,
            engagement=engagement,
            struggle_indicators=struggle_indicators
        )
        
        # Update learning curve
        self._update_learning_curve(user_id, concept, learning_point)
        
        return learning_point
    
    def _detect_struggle_indicators(self, performance: float, time_spent: int, 
                                   attempts: int, engagement: float) -> List[StruggleType]:
        """Detect struggle indicators from learning data"""
        
        struggles = []
        
        # Conceptual struggle: low performance despite high time spent
        if performance < 0.5 and time_spent > 30:
            struggles.append(StruggleType.CONCEPTUAL)
        
        # Procedural struggle: high attempts with low performance
        if attempts > 3 and performance < 0.6:
            struggles.append(StruggleType.PROCEDURAL)
        
        # Application struggle: declining performance over time
        if performance < 0.4:
            struggles.append(StruggleType.APPLICATION)
        
        # Retention struggle: inconsistent performance
        if performance < 0.3:
            struggles.append(StruggleType.RETENTION)
        
        # Engagement struggle: low engagement
        if engagement < 0.3:
            struggles.append(StruggleType.ENGAGEMENT)
        
        return struggles
    
    def _determine_difficulty_from_performance(self, performance: float) -> DifficultyLevel:
        """Determine difficulty level from performance"""
        
        if performance >= 0.9:
            return DifficultyLevel.VERY_HARD
        elif performance >= 0.8:
            return DifficultyLevel.HARD
        elif performance >= 0.6:
            return DifficultyLevel.MEDIUM
        elif performance >= 0.4:
            return DifficultyLevel.EASY
        else:
            return DifficultyLevel.VERY_EASY
    
    def _update_learning_curve(self, user_id: str, concept: str, 
                              learning_point: LearningPoint):
        """Update learning curve with new data point"""
        
        curve_key = f"{user_id}_{concept}"
        
        if curve_key not in self.learning_curves:
            self.learning_curves[curve_key] = LearningCurve(
                concept=concept,
                data_points=[],
                trend="improving",
                current_difficulty=DifficultyLevel.MEDIUM,
                recommended_difficulty=DifficultyLevel.MEDIUM,
                confidence=0.5,
                last_updated=datetime.now()
            )
        
        curve = self.learning_curves[curve_key]
        curve.data_points.append(learning_point)
        
        # Keep only recent data points (last 50)
        if len(curve.data_points) > 50:
            curve.data_points = curve.data_points[-50:]
        
        # Update curve analysis
        self._analyze_learning_curve(curve)
    
    def _analyze_learning_curve(self, curve: LearningCurve):
        """Analyze learning curve and update recommendations"""
        
        if len(curve.data_points) < 3:
            return
        
        # Calculate trend
        trend = self._calculate_trend(curve.data_points)
        curve.trend = trend
        
        # Calculate confidence
        confidence = self._calculate_confidence(curve.data_points)
        curve.confidence = confidence
        
        # Update recommended difficulty
        recommended_difficulty = self._calculate_recommended_difficulty(curve)
        curve.recommended_difficulty = recommended_difficulty
        
        curve.last_updated = datetime.now()
    
    def _calculate_trend(self, data_points: List[LearningPoint]) -> str:
        """Calculate learning trend from data points"""
        
        if len(data_points) < 3:
            return "improving"
        
        # Get recent performance values
        recent_performances = [point.performance for point in data_points[-10:]]
        
        # Calculate trend using linear regression
        x = np.arange(len(recent_performances))
        y = np.array(recent_performances)
        
        # Simple linear regression
        slope = np.polyfit(x, y, 1)[0]
        
        # Calculate volatility
        volatility = np.std(recent_performances)
        
        if volatility > 0.3:
            return "volatile"
        elif slope > 0.05:
            return "improving"
        elif slope < -0.05:
            return "declining"
        else:
            return "plateauing"
    
    def _calculate_confidence(self, data_points: List[LearningPoint]) -> float:
        """Calculate confidence in learning curve analysis"""
        
        if len(data_points) < 5:
            return 0.3
        
        # More data points = higher confidence
        data_confidence = min(1.0, len(data_points) / 20.0)
        
        # Consistent performance = higher confidence
        performances = [point.performance for point in data_points[-10:]]
        consistency = 1.0 - np.std(performances)
        consistency_confidence = max(0.0, consistency)
        
        # Recent data = higher confidence
        recent_confidence = 1.0 if data_points[-1].timestamp > datetime.now() - timedelta(hours=24) else 0.7
        
        # Combine confidence factors
        total_confidence = (data_confidence + consistency_confidence + recent_confidence) / 3.0
        
        return min(1.0, max(0.0, total_confidence))
    
    def _calculate_recommended_difficulty(self, curve: LearningCurve) -> DifficultyLevel:
        """Calculate recommended difficulty based on learning curve"""
        
        if len(curve.data_points) < 3:
            return DifficultyLevel.MEDIUM
        
        # Get recent performance data
        recent_points = curve.data_points[-5:]
        avg_performance = np.mean([point.performance for point in recent_points])
        avg_engagement = np.mean([point.engagement for point in recent_points])
        
        # Calculate struggle severity
        struggle_severity = self._calculate_struggle_severity(recent_points)
        
        # Adjust difficulty based on performance and struggles
        if struggle_severity > 0.7:
            # High struggle - reduce difficulty
            if curve.current_difficulty == DifficultyLevel.VERY_HARD:
                return DifficultyLevel.HARD
            elif curve.current_difficulty == DifficultyLevel.HARD:
                return DifficultyLevel.MEDIUM
            elif curve.current_difficulty == DifficultyLevel.MEDIUM:
                return DifficultyLevel.EASY
            else:
                return DifficultyLevel.VERY_EASY
        elif avg_performance > 0.8 and avg_engagement > 0.7:
            # High performance and engagement - increase difficulty
            if curve.current_difficulty == DifficultyLevel.VERY_EASY:
                return DifficultyLevel.EASY
            elif curve.current_difficulty == DifficultyLevel.EASY:
                return DifficultyLevel.MEDIUM
            elif curve.current_difficulty == DifficultyLevel.MEDIUM:
                return DifficultyLevel.HARD
            else:
                return DifficultyLevel.VERY_HARD
        elif curve.trend == "plateauing" and avg_performance > 0.6:
            # Plateauing with decent performance - slightly increase difficulty
            if curve.current_difficulty == DifficultyLevel.EASY:
                return DifficultyLevel.MEDIUM
            elif curve.current_difficulty == DifficultyLevel.MEDIUM:
                return DifficultyLevel.HARD
            else:
                return curve.current_difficulty
        else:
            # Maintain current difficulty
            return curve.current_difficulty
    
    def _calculate_struggle_severity(self, recent_points: List[LearningPoint]) -> float:
        """Calculate struggle severity from recent data points"""
        
        if not recent_points:
            return 0.0
        
        # Count struggle indicators
        total_struggles = 0
        for point in recent_points:
            total_struggles += len(point.struggle_indicators)
        
        # Calculate severity as proportion of struggles
        max_possible_struggles = len(recent_points) * len(StruggleType)
        severity = total_struggles / max_possible_struggles if max_possible_struggles > 0 else 0.0
        
        return min(1.0, severity)
    
    def get_learning_curve_analysis(self, user_id: str, concept: str) -> Dict[str, Any]:
        """Get comprehensive learning curve analysis"""
        
        curve_key = f"{user_id}_{concept}"
        curve = self.learning_curves.get(curve_key)
        
        if not curve:
            return {
                "concept": concept,
                "status": "no_data",
                "message": "No learning data available for this concept"
            }
        
        # Calculate additional metrics
        recent_performance = np.mean([point.performance for point in curve.data_points[-5:]]) if curve.data_points else 0.0
        avg_engagement = np.mean([point.engagement for point in curve.data_points[-5:]]) if curve.data_points else 0.0
        total_time = sum(point.time_spent for point in curve.data_points)
        total_attempts = sum(point.attempts for point in curve.data_points)
        
        # Identify specific struggles
        recent_struggles = []
        for point in curve.data_points[-5:]:
            recent_struggles.extend(point.struggle_indicators)
        
        struggle_counts = {}
        for struggle in recent_struggles:
            struggle_counts[struggle.value] = struggle_counts.get(struggle.value, 0) + 1
        
        return {
            "concept": concept,
            "status": "analyzed",
            "trend": curve.trend,
            "confidence": curve.confidence,
            "current_difficulty": curve.current_difficulty.value,
            "recommended_difficulty": curve.recommended_difficulty.value,
            "recent_performance": round(recent_performance, 2),
            "avg_engagement": round(avg_engagement, 2),
            "total_time_minutes": total_time,
            "total_attempts": total_attempts,
            "data_points": len(curve.data_points),
            "struggle_indicators": struggle_counts,
            "last_updated": curve.last_updated.isoformat(),
            "recommendations": self._generate_curve_recommendations(curve)
        }
    
    def _generate_curve_recommendations(self, curve: LearningCurve) -> List[str]:
        """Generate recommendations based on learning curve"""
        
        recommendations = []
        
        if curve.trend == "declining":
            recommendations.append("Consider reviewing foundational concepts")
            recommendations.append("Reduce difficulty level to rebuild confidence")
        elif curve.trend == "plateauing":
            recommendations.append("Try different learning approaches or resources")
            recommendations.append("Consider increasing difficulty gradually")
        elif curve.trend == "volatile":
            recommendations.append("Focus on consistent practice and review")
            recommendations.append("Identify specific areas of confusion")
        elif curve.trend == "improving":
            recommendations.append("Continue with current approach")
            recommendations.append("Consider advancing to next difficulty level")
        
        # Add struggle-specific recommendations
        recent_struggles = []
        for point in curve.data_points[-3:]:
            recent_struggles.extend(point.struggle_indicators)
        
        if StruggleType.CONCEPTUAL in recent_struggles:
            recommendations.append("Use visual aids and analogies for conceptual understanding")
        if StruggleType.PROCEDURAL in recent_struggles:
            recommendations.append("Practice step-by-step procedures with guided examples")
        if StruggleType.APPLICATION in recent_struggles:
            recommendations.append("Focus on real-world applications and practice problems")
        if StruggleType.ENGAGEMENT in recent_struggles:
            recommendations.append("Try gamification or interactive learning methods")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def get_difficulty_adjustment(self, user_id: str, concept: str) -> Dict[str, Any]:
        """Get real-time difficulty adjustment recommendation"""
        
        curve_key = f"{user_id}_{concept}"
        curve = self.learning_curves.get(curve_key)
        
        if not curve or len(curve.data_points) < 3:
            return {
                "adjustment": "maintain",
                "new_difficulty": "medium",
                "confidence": 0.5,
                "reason": "Insufficient data for adjustment"
            }
        
        current_difficulty = curve.current_difficulty.value
        recommended_difficulty = curve.recommended_difficulty.value
        
        if current_difficulty != recommended_difficulty:
            return {
                "adjustment": "change",
                "new_difficulty": recommended_difficulty,
                "confidence": curve.confidence,
                "reason": f"Learning curve analysis suggests {recommended_difficulty} difficulty",
                "trend": curve.trend,
                "performance": np.mean([point.performance for point in curve.data_points[-3:]])
            }
        else:
            return {
                "adjustment": "maintain",
                "new_difficulty": current_difficulty,
                "confidence": curve.confidence,
                "reason": "Current difficulty is appropriate",
                "trend": curve.trend
            }
    
    def get_struggle_alerts(self, user_id: str, concept: str) -> List[Dict[str, Any]]:
        """Get alerts for learning struggles"""
        
        curve_key = f"{user_id}_{concept}"
        curve = self.learning_curves.get(curve_key)
        
        if not curve:
            return []
        
        alerts = []
        
        # Check for recent struggles
        recent_points = curve.data_points[-3:] if len(curve.data_points) >= 3 else curve.data_points
        
        for point in recent_points:
            for struggle in point.struggle_indicators:
                alert = {
                    "type": struggle.value,
                    "severity": "high" if point.performance < 0.3 else "medium",
                    "timestamp": point.timestamp.isoformat(),
                    "concept": concept,
                    "suggestion": self._get_struggle_suggestion(struggle)
                }
                alerts.append(alert)
        
        return alerts
    
    def _get_struggle_suggestion(self, struggle: StruggleType) -> str:
        """Get suggestion for specific struggle type"""
        
        suggestions = {
            StruggleType.CONCEPTUAL: "Use visual diagrams and step-by-step explanations",
            StruggleType.PROCEDURAL: "Practice with guided examples and checklists",
            StruggleType.APPLICATION: "Work through real-world examples and case studies",
            StruggleType.RETENTION: "Use spaced repetition and regular review sessions",
            StruggleType.ENGAGEMENT: "Try interactive activities and gamification elements"
        }
        
        return suggestions.get(struggle, "Review the material and practice more")

