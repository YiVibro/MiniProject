"""
Markov Decision Process (MDP) Model for Personalized Learning Paths
===================================================================

This module implements an MDP-based system to recommend personalized learning paths
using reinforcement learning principles and user behavior modeling.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import numpy as np
from pydantic import BaseModel, Field
from dataclasses import dataclass
from enum import Enum

class LearningState(Enum):
    """Learning states in the MDP"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class Action(Enum):
    """Available actions in the MDP"""
    EASY_LESSON = "easy_lesson"
    MEDIUM_LESSON = "medium_lesson"
    HARD_LESSON = "hard_lesson"
    REVIEW = "review"
    PRACTICE = "practice"
    ASSESSMENT = "assessment"
    BREAK = "break"

class Reward(Enum):
    """Reward types in the MDP"""
    COMPLETION = "completion"
    MASTERY = "mastery"
    ENGAGEMENT = "engagement"
    EFFICIENCY = "efficiency"

@dataclass
class MDPState:
    """State in the MDP"""
    user_id: str
    current_learning_state: LearningState
    proficiency_level: float  # 0.0 to 1.0
    engagement_level: float   # 0.0 to 1.0
    fatigue_level: float     # 0.0 to 1.0
    recent_performance: List[float]
    learning_style: str
    time_available: int  # minutes
    session_count: int

@dataclass
class MDPAction:
    """Action in the MDP"""
    action_type: Action
    lesson_id: Optional[str]
    difficulty: str
    duration: int  # minutes
    expected_outcome: str

@dataclass
class MDPReward:
    """Reward in the MDP"""
    reward_type: Reward
    value: float
    timestamp: datetime
    context: Dict[str, Any]

class MDPLearningPath:
    """MDP-based learning path recommendation system"""
    
    def __init__(self):
        self.states = {}  # user_id -> MDPState
        self.transitions = {}  # (state, action) -> next_state_probabilities
        self.rewards = {}  # (state, action, next_state) -> reward
        self.policy = {}  # state -> action_probabilities
        
        # Initialize transition probabilities
        self._initialize_transitions()
        
        # Initialize reward structure
        self._initialize_rewards()
    
    def _initialize_transitions(self):
        """Initialize state transition probabilities"""
        
        # Define transition probabilities based on learning theory
        self.transitions = {
            # From BEGINNER state
            (LearningState.BEGINNER, Action.EASY_LESSON): {
                LearningState.BEGINNER: 0.3,
                LearningState.INTERMEDIATE: 0.6,
                LearningState.ADVANCED: 0.1
            },
            (LearningState.BEGINNER, Action.MEDIUM_LESSON): {
                LearningState.BEGINNER: 0.7,
                LearningState.INTERMEDIATE: 0.3,
                LearningState.ADVANCED: 0.0
            },
            (LearningState.BEGINNER, Action.HARD_LESSON): {
                LearningState.BEGINNER: 0.9,
                LearningState.INTERMEDIATE: 0.1,
                LearningState.ADVANCED: 0.0
            },
            (LearningState.BEGINNER, Action.REVIEW): {
                LearningState.BEGINNER: 0.8,
                LearningState.INTERMEDIATE: 0.2,
                LearningState.ADVANCED: 0.0
            },
            
            # From INTERMEDIATE state
            (LearningState.INTERMEDIATE, Action.EASY_LESSON): {
                LearningState.BEGINNER: 0.1,
                LearningState.INTERMEDIATE: 0.8,
                LearningState.ADVANCED: 0.1
            },
            (LearningState.INTERMEDIATE, Action.MEDIUM_LESSON): {
                LearningState.BEGINNER: 0.1,
                LearningState.INTERMEDIATE: 0.4,
                LearningState.ADVANCED: 0.5
            },
            (LearningState.INTERMEDIATE, Action.HARD_LESSON): {
                LearningState.BEGINNER: 0.3,
                LearningState.INTERMEDIATE: 0.6,
                LearningState.ADVANCED: 0.1
            },
            (LearningState.INTERMEDIATE, Action.REVIEW): {
                LearningState.BEGINNER: 0.2,
                LearningState.INTERMEDIATE: 0.7,
                LearningState.ADVANCED: 0.1
            },
            
            # From ADVANCED state
            (LearningState.ADVANCED, Action.EASY_LESSON): {
                LearningState.INTERMEDIATE: 0.2,
                LearningState.ADVANCED: 0.7,
                LearningState.EXPERT: 0.1
            },
            (LearningState.ADVANCED, Action.MEDIUM_LESSON): {
                LearningState.INTERMEDIATE: 0.1,
                LearningState.ADVANCED: 0.6,
                LearningState.EXPERT: 0.3
            },
            (LearningState.ADVANCED, Action.HARD_LESSON): {
                LearningState.INTERMEDIATE: 0.1,
                LearningState.ADVANCED: 0.4,
                LearningState.EXPERT: 0.5
            },
            (LearningState.ADVANCED, Action.REVIEW): {
                LearningState.INTERMEDIATE: 0.1,
                LearningState.ADVANCED: 0.8,
                LearningState.EXPERT: 0.1
            },
            
            # From EXPERT state
            (LearningState.EXPERT, Action.EASY_LESSON): {
                LearningState.ADVANCED: 0.1,
                LearningState.EXPERT: 0.9
            },
            (LearningState.EXPERT, Action.MEDIUM_LESSON): {
                LearningState.ADVANCED: 0.1,
                LearningState.EXPERT: 0.9
            },
            (LearningState.EXPERT, Action.HARD_LESSON): {
                LearningState.ADVANCED: 0.2,
                LearningState.EXPERT: 0.8
            },
            (LearningState.EXPERT, Action.REVIEW): {
                LearningState.ADVANCED: 0.1,
                LearningState.EXPERT: 0.9
            }
        }
    
    def _initialize_rewards(self):
        """Initialize reward structure"""
        
        # Define rewards based on learning outcomes
        self.rewards = {
            # Completion rewards
            (LearningState.BEGINNER, Action.EASY_LESSON, LearningState.INTERMEDIATE): 10.0,
            (LearningState.INTERMEDIATE, Action.MEDIUM_LESSON, LearningState.ADVANCED): 15.0,
            (LearningState.ADVANCED, Action.HARD_LESSON, LearningState.EXPERT): 20.0,
            
            # Mastery rewards
            (LearningState.BEGINNER, Action.REVIEW, LearningState.BEGINNER): 5.0,
            (LearningState.INTERMEDIATE, Action.REVIEW, LearningState.INTERMEDIATE): 8.0,
            (LearningState.ADVANCED, Action.REVIEW, LearningState.ADVANCED): 12.0,
            
            # Engagement rewards
            (LearningState.BEGINNER, Action.PRACTICE, LearningState.BEGINNER): 3.0,
            (LearningState.INTERMEDIATE, Action.PRACTICE, LearningState.INTERMEDIATE): 5.0,
            (LearningState.ADVANCED, Action.PRACTICE, LearningState.ADVANCED): 7.0,
            
            # Efficiency rewards (staying in same state but learning)
            (LearningState.BEGINNER, Action.EASY_LESSON, LearningState.BEGINNER): 2.0,
            (LearningState.INTERMEDIATE, Action.MEDIUM_LESSON, LearningState.INTERMEDIATE): 3.0,
            (LearningState.ADVANCED, Action.HARD_LESSON, LearningState.ADVANCED): 4.0,
        }
    
    def get_user_state(self, user_id: str) -> Optional[MDPState]:
        """Get current state for user"""
        return self.states.get(user_id)
    
    def update_user_state(self, user_id: str, new_state: MDPState):
        """Update user state"""
        self.states[user_id] = new_state
    
    def recommend_action(self, user_id: str, context: Dict[str, Any]) -> MDPAction:
        """Recommend next action using MDP policy"""
        
        current_state = self.get_user_state(user_id)
        if not current_state:
            # Initialize new user state
            current_state = self._initialize_user_state(user_id, context)
            self.update_user_state(user_id, current_state)
        
        # Get available actions for current state
        available_actions = self._get_available_actions(current_state, context)
        
        # Calculate action values using value iteration
        action_values = self._calculate_action_values(current_state, available_actions)
        
        # Select best action
        best_action = max(action_values.items(), key=lambda x: x[1])
        
        return self._create_action(best_action[0], context)
    
    def _initialize_user_state(self, user_id: str, context: Dict[str, Any]) -> MDPState:
        """Initialize new user state"""
        
        return MDPState(
            user_id=user_id,
            current_learning_state=LearningState.BEGINNER,
            proficiency_level=0.0,
            engagement_level=0.5,
            fatigue_level=0.0,
            recent_performance=[],
            learning_style=context.get("learning_style", "balanced"),
            time_available=context.get("time_available", 30),
            session_count=0
        )
    
    def _get_available_actions(self, state: MDPState, context: Dict[str, Any]) -> List[Action]:
        """Get available actions for current state"""
        
        available_actions = []
        
        # Always available actions
        available_actions.extend([Action.REVIEW, Action.PRACTICE, Action.ASSESSMENT])
        
        # Add difficulty-based actions
        if state.current_learning_state == LearningState.BEGINNER:
            available_actions.append(Action.EASY_LESSON)
            if state.proficiency_level > 0.3:
                available_actions.append(Action.MEDIUM_LESSON)
        elif state.current_learning_state == LearningState.INTERMEDIATE:
            available_actions.extend([Action.EASY_LESSON, Action.MEDIUM_LESSON])
            if state.proficiency_level > 0.6:
                available_actions.append(Action.HARD_LESSON)
        elif state.current_learning_state == LearningState.ADVANCED:
            available_actions.extend([Action.MEDIUM_LESSON, Action.HARD_LESSON])
        elif state.current_learning_state == LearningState.EXPERT:
            available_actions.extend([Action.MEDIUM_LESSON, Action.HARD_LESSON])
        
        # Add break if fatigue is high
        if state.fatigue_level > 0.7:
            available_actions.append(Action.BREAK)
        
        # Filter by time available
        if state.time_available < 15:
            available_actions = [a for a in available_actions if a in [Action.REVIEW, Action.PRACTICE, Action.BREAK]]
        
        return available_actions
    
    def _calculate_action_values(self, state: MDPState, available_actions: List[Action]) -> Dict[Action, float]:
        """Calculate action values using MDP principles"""
        
        action_values = {}
        
        for action in available_actions:
            # Calculate expected reward for this action
            expected_reward = self._calculate_expected_reward(state, action)
            
            # Calculate future value (discounted)
            future_value = self._calculate_future_value(state, action)
            
            # Combine immediate and future values
            total_value = expected_reward + 0.9 * future_value  # 0.9 discount factor
            
            action_values[action] = total_value
        
        return action_values
    
    def _calculate_expected_reward(self, state: MDPState, action: Action) -> float:
        """Calculate expected immediate reward for action"""
        
        # Base reward for action type
        base_rewards = {
            Action.EASY_LESSON: 2.0,
            Action.MEDIUM_LESSON: 3.0,
            Action.HARD_LESSON: 4.0,
            Action.REVIEW: 1.5,
            Action.PRACTICE: 2.5,
            Action.ASSESSMENT: 3.0,
            Action.BREAK: 0.5
        }
        
        base_reward = base_rewards.get(action, 1.0)
        
        # Adjust based on user state
        proficiency_bonus = state.proficiency_level * 2.0
        engagement_bonus = state.engagement_level * 1.5
        fatigue_penalty = state.fatigue_level * -1.0
        
        return base_reward + proficiency_bonus + engagement_bonus + fatigue_penalty
    
    def _calculate_future_value(self, state: MDPState, action: Action) -> float:
        """Calculate future value of action using transition probabilities"""
        
        if (state.current_learning_state, action) not in self.transitions:
            return 0.0
        
        transition_probs = self.transitions[(state.current_learning_state, action)]
        future_value = 0.0
        
        for next_state, prob in transition_probs.items():
            # Calculate reward for this transition
            reward_key = (state.current_learning_state, action, next_state)
            reward = self.rewards.get(reward_key, 0.0)
            
            # Add to future value
            future_value += prob * reward
        
        return future_value
    
    def _create_action(self, action_type: Action, context: Dict[str, Any]) -> MDPAction:
        """Create MDP action from action type"""
        
        # Map action types to lesson parameters
        action_mapping = {
            Action.EASY_LESSON: {"difficulty": "easy", "duration": 20},
            Action.MEDIUM_LESSON: {"difficulty": "medium", "duration": 30},
            Action.HARD_LESSON: {"difficulty": "hard", "duration": 45},
            Action.REVIEW: {"difficulty": "review", "duration": 15},
            Action.PRACTICE: {"difficulty": "practice", "duration": 25},
            Action.ASSESSMENT: {"difficulty": "assessment", "duration": 20},
            Action.BREAK: {"difficulty": "break", "duration": 10}
        }
        
        params = action_mapping.get(action_type, {"difficulty": "medium", "duration": 30})
        
        return MDPAction(
            action_type=action_type,
            lesson_id=context.get("lesson_id"),
            difficulty=params["difficulty"],
            duration=params["duration"],
            expected_outcome=self._get_expected_outcome(action_type)
        )
    
    def _get_expected_outcome(self, action_type: Action) -> str:
        """Get expected outcome description for action"""
        
        outcomes = {
            Action.EASY_LESSON: "Build confidence with manageable content",
            Action.MEDIUM_LESSON: "Challenge yourself with moderate difficulty",
            Action.HARD_LESSON: "Push your limits with advanced content",
            Action.REVIEW: "Reinforce previous learning",
            Action.PRACTICE: "Apply knowledge through exercises",
            Action.ASSESSMENT: "Test your understanding",
            Action.BREAK: "Rest and recharge"
        }
        
        return outcomes.get(action_type, "Continue learning")
    
    def update_from_feedback(self, user_id: str, action: MDPAction, 
                           outcome: Dict[str, Any], reward: float):
        """Update MDP model based on user feedback"""
        
        current_state = self.get_user_state(user_id)
        if not current_state:
            return
        
        # Update state based on outcome
        new_state = self._update_state_from_outcome(current_state, action, outcome)
        
        # Update transition probabilities based on actual outcome
        self._update_transitions(current_state.current_learning_state, action, new_state.current_learning_state)
        
        # Update rewards based on actual reward received
        self._update_rewards(current_state.current_learning_state, action, new_state.current_learning_state, reward)
        
        # Update user state
        self.update_user_state(user_id, new_state)
    
    def _update_state_from_outcome(self, current_state: MDPState, action: MDPAction, 
                                 outcome: Dict[str, Any]) -> MDPState:
        """Update state based on action outcome"""
        
        # Update proficiency based on performance
        performance = outcome.get("performance", 0.5)
        proficiency_change = (performance - 0.5) * 0.1
        new_proficiency = max(0.0, min(1.0, current_state.proficiency_level + proficiency_change))
        
        # Update engagement based on completion and satisfaction
        engagement_change = outcome.get("engagement_change", 0.0)
        new_engagement = max(0.0, min(1.0, current_state.engagement_level + engagement_change))
        
        # Update fatigue based on session length and difficulty
        fatigue_change = outcome.get("fatigue_change", 0.1)
        new_fatigue = max(0.0, min(1.0, current_state.fatigue_level + fatigue_change))
        
        # Update learning state based on proficiency
        new_learning_state = self._determine_learning_state(new_proficiency)
        
        # Update performance history
        new_performance = current_state.recent_performance + [performance]
        if len(new_performance) > 10:  # Keep only last 10 performances
            new_performance = new_performance[-10:]
        
        return MDPState(
            user_id=current_state.user_id,
            current_learning_state=new_learning_state,
            proficiency_level=new_proficiency,
            engagement_level=new_engagement,
            fatigue_level=new_fatigue,
            recent_performance=new_performance,
            learning_style=current_state.learning_style,
            time_available=current_state.time_available - action.duration,
            session_count=current_state.session_count + 1
        )
    
    def _determine_learning_state(self, proficiency: float) -> LearningState:
        """Determine learning state based on proficiency level"""
        
        if proficiency < 0.25:
            return LearningState.BEGINNER
        elif proficiency < 0.5:
            return LearningState.INTERMEDIATE
        elif proficiency < 0.75:
            return LearningState.ADVANCED
        else:
            return LearningState.EXPERT
    
    def _update_transitions(self, from_state: LearningState, action: Action, 
                          to_state: LearningState):
        """Update transition probabilities based on actual outcomes"""
        
        # Simple update: increase probability of observed transition
        key = (from_state, action)
        if key in self.transitions:
            # Increase probability of observed transition by small amount
            self.transitions[key][to_state] = min(1.0, self.transitions[key][to_state] + 0.01)
            
            # Normalize probabilities
            total = sum(self.transitions[key].values())
            for state in self.transitions[key]:
                self.transitions[key][state] /= total
    
    def _update_rewards(self, from_state: LearningState, action: Action, 
                       to_state: LearningState, actual_reward: float):
        """Update rewards based on actual outcomes"""
        
        key = (from_state, action, to_state)
        if key in self.rewards:
            # Update reward using exponential moving average
            self.rewards[key] = 0.9 * self.rewards[key] + 0.1 * actual_reward
        else:
            # Add new reward
            self.rewards[key] = actual_reward
    
    def get_learning_path_recommendation(self, user_id: str, 
                                       num_steps: int = 5) -> List[MDPAction]:
        """Get multi-step learning path recommendation"""
        
        path = []
        current_state = self.get_user_state(user_id)
        
        if not current_state:
            return path
        
        for _ in range(num_steps):
            # Get next action recommendation
            action = self.recommend_action(user_id, {})
            path.append(action)
            
            # Simulate taking the action (update state)
            # This is a simplified simulation - in practice, you'd wait for actual user feedback
            simulated_outcome = {
                "performance": 0.7,  # Simulated performance
                "engagement_change": 0.05,
                "fatigue_change": 0.1
            }
            
            self.update_from_feedback(user_id, action, simulated_outcome, 5.0)
            current_state = self.get_user_state(user_id)
        
        return path

