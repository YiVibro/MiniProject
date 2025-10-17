"""
Data Models for Multi-Agent AI Tutoring System
=============================================

This module contains all the data models and structures used throughout
the adaptive learning system.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
from dataclasses import dataclass

class DifficultyLevel(Enum):
    """Difficulty levels for content"""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"

class LearningStyle(Enum):
    """Learning style preferences"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    ANALYTICAL = "analytical"
    PRACTICAL = "practical"

class UserProgress(BaseModel):
    """User progress tracking model"""
    user_id: str
    completed_lessons: List[str] = Field(default_factory=list)
    test_scores: List[float] = Field(default_factory=list)
    current_difficulty: str = "medium"
    learning_style: str = "balanced"
    total_time_spent: int = 0  # minutes
    streak_days: int = 0
    last_activity: Optional[datetime] = None
    proficiency_scores: Dict[str, float] = Field(default_factory=dict)
    learning_goals: List[str] = Field(default_factory=list)

class Lesson(BaseModel):
    """Lesson model"""
    lesson_id: str
    title: str
    content: str
    difficulty: str
    duration: int  # minutes
    learning_objectives: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    assessment_questions: List[Dict[str, Any]] = Field(default_factory=list)
    practice_exercises: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Assessment(BaseModel):
    """Assessment model"""
    assessment_id: str
    lesson_id: str
    questions: List[Dict[str, Any]]
    time_limit: int  # minutes
    passing_score: float = 0.7
    difficulty: str = "medium"
    created_at: datetime = Field(default_factory=datetime.now)

class TestResult(BaseModel):
    """Test result model"""
    result_id: str
    user_id: str
    assessment_id: str
    score: float
    answers: List[Dict[str, Any]]
    time_taken: int  # minutes
    completed_at: datetime = Field(default_factory=datetime.now)
    feedback: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)

class LearningPath(BaseModel):
    """Learning path model"""
    path_id: str
    user_id: str
    title: str
    description: str
    lessons: List[str]  # lesson IDs
    estimated_duration: int  # minutes
    difficulty_progression: List[str]
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "active"  # active, completed, paused

class UserProfile(BaseModel):
    """User profile model"""
    user_id: str
    name: str
    email: str
    learning_style: str = "balanced"
    preferred_difficulty: str = "medium"
    available_time: int = 60  # minutes per day
    learning_goals: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None

class SessionData(BaseModel):
    """Learning session data"""
    session_id: str
    user_id: str
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    lessons_completed: List[str] = Field(default_factory=list)
    assessments_taken: List[str] = Field(default_factory=list)
    total_time: int = 0  # minutes
    engagement_score: float = 0.0
    difficulty_adjustments: List[Dict[str, Any]] = Field(default_factory=list)

class ConceptMastery(BaseModel):
    """Concept mastery tracking"""
    user_id: str
    concept: str
    mastery_level: float = 0.0  # 0.0 to 1.0
    attempts: int = 0
    last_practiced: Optional[datetime] = None
    struggle_indicators: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)

class AdaptiveContent(BaseModel):
    """Adaptive content model"""
    content_id: str
    base_content: str
    difficulty_variations: Dict[str, str] = Field(default_factory=dict)
    learning_style_adaptations: Dict[str, str] = Field(default_factory=dict)
    engagement_elements: List[str] = Field(default_factory=list)
    accessibility_features: List[str] = Field(default_factory=list)

class FeedbackData(BaseModel):
    """Feedback data model"""
    feedback_id: str
    user_id: str
    session_id: str
    content_id: str
    feedback_type: str  # positive, negative, neutral
    rating: float = 0.0  # 0.0 to 5.0
    comments: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PerformanceMetrics(BaseModel):
    """Performance metrics model"""
    user_id: str
    concept: str
    accuracy: float = 0.0
    speed: float = 0.0  # questions per minute
    engagement: float = 0.0
    retention: float = 0.0
    confidence: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)

class GapAnalysisResult(BaseModel):
    """Gap analysis result model"""
    user_id: str
    session_id: str
    misconceptions: List[Dict[str, Any]] = Field(default_factory=list)
    learning_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    overall_confidence: float = 0.0
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    recommendations: List[str] = Field(default_factory=list)

class LearningCurveData(BaseModel):
    """Learning curve data model"""
    user_id: str
    concept: str
    data_points: List[Dict[str, Any]] = Field(default_factory=list)
    trend: str = "improving"
    current_difficulty: str = "medium"
    recommended_difficulty: str = "medium"
    confidence: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.now)

class MDPRecommendation(BaseModel):
    """MDP recommendation model"""
    user_id: str
    recommended_action: str
    confidence: float = 0.0
    expected_outcome: str = ""
    reasoning: str = ""
    alternatives: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)

class SystemMetrics(BaseModel):
    """System performance metrics"""
    total_users: int = 0
    active_sessions: int = 0
    lessons_completed: int = 0
    average_engagement: float = 0.0
    system_uptime: float = 0.0
    error_rate: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)

# Additional utility classes
@dataclass
class LearningObjective:
    """Learning objective structure"""
    objective_id: str
    description: str
    difficulty: str
    prerequisites: List[str]
    assessment_criteria: List[str]
    estimated_time: int  # minutes

@dataclass
class ContentAdaptation:
    """Content adaptation structure"""
    original_content: str
    adapted_content: str
    adaptation_type: str  # difficulty, style, accessibility
    adaptation_reason: str
    confidence: float

@dataclass
class UserInteraction:
    """User interaction structure"""
    interaction_id: str
    user_id: str
    session_id: str
    interaction_type: str  # click, scroll, answer, pause
    timestamp: datetime
    data: Dict[str, Any]

class LearningAnalytics(BaseModel):
    """Learning analytics model"""
    user_id: str
    session_id: str
    concept: str
    performance_trend: str = "stable"
    engagement_trend: str = "stable"
    difficulty_preference: str = "medium"
    learning_velocity: float = 0.0
    retention_rate: float = 0.0
    struggle_patterns: List[str] = Field(default_factory=list)
    success_patterns: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
