"""
Planner Agent - Optimized Study Plan Creation
============================================

This agent creates optimized study plans based on timelines, objectives,
and user preferences using advanced planning algorithms.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from .base_agent import BaseAgent, AgentState, AgentResponse
from models import Lesson, UserProgress, LearningPath

class PlannerAgent(BaseAgent):
    """Agent responsible for creating optimized study plans"""
    
    def __init__(self, llm_service):
        super().__init__("planner", llm_service)
        self.planning_strategies = {
            "spaced_repetition": "Schedule reviews at increasing intervals",
            "pomodoro": "25-minute focused study sessions with breaks",
            "progressive_overload": "Gradually increase difficulty and duration",
            "interleaving": "Mix different topics in single study sessions",
            "active_recall": "Focus on testing and retrieval practice"
        }
    
    async def process(self, state: AgentState) -> AgentResponse:
        """Process planning-related tasks"""
        try:
            action = state.metadata.get("action", "create_study_plan")
            
            if action == "create_study_plan":
                return await self._create_study_plan(state)
            elif action == "optimize_schedule":
                return await self._optimize_schedule(state)
            elif action == "adjust_plan":
                return await self._adjust_plan(state)
            elif action == "create_review_plan":
                return await self._create_review_plan(state)
            else:
                return self.create_response(
                    response="I can help with study planning, schedule optimization, and plan adjustments. What would you like me to do?",
                    confidence=0.8
                )
                
        except Exception as e:
            return self.create_response(
                response="I encountered an error while processing your planning request. Please try again.",
                confidence=0.1,
                metadata={"error": str(e)}
            )
    
    async def _create_study_plan(self, state: AgentState) -> AgentResponse:
        """Create personalized study plan"""
        try:
            goals = state.metadata.get("goals", [])
            timeline = state.metadata.get("timeline", "4 weeks")
            available_time = state.metadata.get("available_time", "1 hour per day")
            learning_style = state.metadata.get("learning_style", "balanced")
            current_level = state.metadata.get("current_level", "beginner")
            
            # Generate study plan
            study_plan = await self._generate_study_plan(
                goals, timeline, available_time, learning_style, current_level
            )
            
            return self.create_response(
                response=f"Created personalized study plan for {timeline}",
                confidence=0.9,
                metadata={
                    "study_plan": study_plan,
                    "timeline": timeline,
                    "goals": goals,
                    "strategy": study_plan.get("strategy", "balanced")
                }
            )
            
        except Exception as e:
            return self.create_response(
                response="Error creating study plan. Please try again.",
                confidence=0.1,
                metadata={"error": str(e)}
            )
    
    async def _generate_study_plan(self, goals: List[str], timeline: str, 
                                 available_time: str, learning_style: str, 
                                 current_level: str) -> Dict[str, Any]:
        """Generate comprehensive study plan"""
        
        prompt = f"""
        Create a detailed study plan with the following parameters:
        
        Goals: {', '.join(goals)}
        Timeline: {timeline}
        Available Time: {available_time}
        Learning Style: {learning_style}
        Current Level: {current_level}
        
        Include:
        1. Weekly breakdown with specific topics
        2. Daily study schedule with time allocation
        3. Milestone checkpoints
        4. Review and practice sessions
        5. Assessment schedule
        6. Flexibility for adjustments
        
        Format as a structured plan that can be followed step-by-step.
        """
        
        plan_text = await self.llm_service.generate_response(prompt)
        
        # Parse the plan into structured format
        structured_plan = self._parse_study_plan(plan_text, timeline, goals)
        
        return structured_plan
    
    def _parse_study_plan(self, plan_text: str, timeline: str, goals: List[str]) -> Dict[str, Any]:
        """Parse generated study plan into structured format"""
        
        # Extract timeline in weeks
        timeline_weeks = self._extract_timeline_weeks(timeline)
        
        # Parse weekly breakdown
        weeks = self._parse_weekly_breakdown(plan_text, timeline_weeks)
        
        # Extract milestones
        milestones = self._extract_milestones(plan_text)
        
        # Extract study strategy
        strategy = self._extract_study_strategy(plan_text)
        
        return {
            "timeline_weeks": timeline_weeks,
            "goals": goals,
            "weekly_breakdown": weeks,
            "milestones": milestones,
            "strategy": strategy,
            "total_estimated_hours": timeline_weeks * 7,  # Assume 1 hour per day
            "flexibility_notes": self._extract_flexibility_notes(plan_text)
        }
    
    def _extract_timeline_weeks(self, timeline: str) -> int:
        """Extract number of weeks from timeline string"""
        import re
        
        # Look for numbers followed by week/month
        numbers = re.findall(r'(\d+)', timeline)
        if numbers:
            weeks = int(numbers[0])
            if 'month' in timeline.lower():
                weeks *= 4  # Convert months to weeks
            return weeks
        return 4  # Default to 4 weeks
    
    def _parse_weekly_breakdown(self, plan_text: str, total_weeks: int) -> List[Dict[str, Any]]:
        """Parse weekly breakdown from plan text"""
        weeks = []
        
        # Look for week patterns
        import re
        week_patterns = re.findall(r'Week \d+.*?(?=Week \d+|$)', plan_text, re.DOTALL | re.IGNORECASE)
        
        for i, week_text in enumerate(week_patterns[:total_weeks]):
            week_data = {
                "week_number": i + 1,
                "topics": self._extract_week_topics(week_text),
                "focus_areas": self._extract_focus_areas(week_text),
                "estimated_hours": 7,  # Default 1 hour per day
                "key_activities": self._extract_key_activities(week_text)
            }
            weeks.append(week_data)
        
        # Fill remaining weeks if needed
        while len(weeks) < total_weeks:
            week_data = {
                "week_number": len(weeks) + 1,
                "topics": ["Review and Practice"],
                "focus_areas": ["Consolidation"],
                "estimated_hours": 7,
                "key_activities": ["Review previous weeks", "Practice problems", "Self-assessment"]
            }
            weeks.append(week_data)
        
        return weeks
    
    def _extract_week_topics(self, week_text: str) -> List[str]:
        """Extract topics from week text"""
        topics = []
        lines = week_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('Week', 'Focus', 'Activities')):
                # Clean up the line
                clean_line = line.replace('•', '').replace('-', '').strip()
                if clean_line and len(clean_line) > 3:
                    topics.append(clean_line)
        
        return topics[:5]  # Limit to 5 topics per week
    
    def _extract_focus_areas(self, week_text: str) -> List[str]:
        """Extract focus areas from week text"""
        focus_areas = []
        
        # Look for common focus area keywords
        keywords = ['theory', 'practice', 'application', 'review', 'assessment', 'projects']
        
        for keyword in keywords:
            if keyword.lower() in week_text.lower():
                focus_areas.append(keyword.title())
        
        return focus_areas if focus_areas else ['Learning']
    
    def _extract_key_activities(self, week_text: str) -> List[str]:
        """Extract key activities from week text"""
        activities = []
        lines = week_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['study', 'practice', 'review', 'read', 'watch', 'complete']):
                activities.append(line)
        
        return activities[:3]  # Limit to 3 key activities
    
    def _extract_milestones(self, plan_text: str) -> List[Dict[str, Any]]:
        """Extract milestones from plan text"""
        milestones = []
        
        # Look for milestone patterns
        import re
        milestone_patterns = re.findall(r'(Week \d+|End of \w+|Midpoint|Final)', plan_text, re.IGNORECASE)
        
        for i, milestone in enumerate(milestone_patterns[:5]):  # Limit to 5 milestones
            milestones.append({
                "milestone_id": i + 1,
                "name": milestone,
                "description": f"Key checkpoint at {milestone}",
                "estimated_completion": f"Week {i + 1}" if "Week" in milestone else milestone
            })
        
        return milestones
    
    def _extract_study_strategy(self, plan_text: str) -> str:
        """Extract study strategy from plan text"""
        strategies = list(self.planning_strategies.keys())
        
        for strategy in strategies:
            if strategy.replace('_', ' ') in plan_text.lower():
                return strategy
        
        return "balanced"  # Default strategy
    
    def _extract_flexibility_notes(self, plan_text: str) -> List[str]:
        """Extract flexibility notes from plan text"""
        notes = []
        
        # Look for flexibility-related keywords
        flexibility_keywords = ['adjust', 'flexible', 'adapt', 'modify', 'change', 'optional']
        
        lines = plan_text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in flexibility_keywords):
                notes.append(line.strip())
        
        return notes[:3]  # Limit to 3 notes
    
    async def _optimize_schedule(self, state: AgentState) -> AgentResponse:
        """Optimize existing study schedule"""
        try:
            current_schedule = state.metadata.get("current_schedule", {})
            constraints = state.metadata.get("constraints", {})
            preferences = state.metadata.get("preferences", {})
            
            # Optimize schedule
            optimized_schedule = await self._apply_optimization(
                current_schedule, constraints, preferences
            )
            
            return self.create_response(
                response="Schedule optimized based on your constraints and preferences",
                confidence=0.9,
                metadata={"optimized_schedule": optimized_schedule}
            )
            
        except Exception as e:
            return self.create_response(
                response="Error optimizing schedule. Please try again.",
                confidence=0.1,
                metadata={"error": str(e)}
            )
    
    async def _apply_optimization(self, schedule: Dict[str, Any], 
                                constraints: Dict[str, Any], 
                                preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Apply optimization algorithms to schedule"""
        
        prompt = f"""
        Optimize this study schedule based on the given constraints and preferences:
        
        Current Schedule: {schedule}
        Constraints: {constraints}
        Preferences: {preferences}
        
        Apply these optimization principles:
        1. Spaced repetition for better retention
        2. Optimal study times based on preferences
        3. Balanced workload distribution
        4. Buffer time for unexpected events
        5. Review sessions at optimal intervals
        
        Provide the optimized schedule with explanations for changes.
        """
        
        optimization_text = await self.llm_service.generate_response(prompt)
        
        return {
            "original_schedule": schedule,
            "optimized_schedule": optimization_text,
            "optimization_notes": self._extract_optimization_notes(optimization_text),
            "improvements": self._identify_improvements(schedule, optimization_text)
        }
    
    def _extract_optimization_notes(self, optimization_text: str) -> List[str]:
        """Extract optimization notes from text"""
        notes = []
        lines = optimization_text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['improved', 'optimized', 'better', 'enhanced']):
                notes.append(line.strip())
        
        return notes[:5]  # Limit to 5 notes
    
    def _identify_improvements(self, original: Dict[str, Any], optimized: str) -> List[str]:
        """Identify specific improvements made"""
        improvements = [
            "Better time distribution",
            "Improved review scheduling",
            "Enhanced flexibility",
            "Optimized study sessions"
        ]
        return improvements
    
    async def _adjust_plan(self, state: AgentState) -> AgentResponse:
        """Adjust existing study plan based on progress"""
        try:
            current_plan = state.metadata.get("current_plan", {})
            progress_data = state.metadata.get("progress_data", {})
            adjustment_reason = state.metadata.get("adjustment_reason", "performance")
            
            # Adjust plan
            adjusted_plan = await self._make_adjustments(
                current_plan, progress_data, adjustment_reason
            )
            
            return self.create_response(
                response="Study plan adjusted based on your progress",
                confidence=0.9,
                metadata={"adjusted_plan": adjusted_plan}
            )
            
        except Exception as e:
            return self.create_response(
                response="Error adjusting plan. Please try again.",
                confidence=0.1,
                metadata={"error": str(e)}
            )
    
    async def _make_adjustments(self, current_plan: Dict[str, Any], 
                              progress_data: Dict[str, Any], 
                              reason: str) -> Dict[str, Any]:
        """Make adjustments to study plan"""
        
        prompt = f"""
        Adjust this study plan based on the progress data and adjustment reason:
        
        Current Plan: {current_plan}
        Progress Data: {progress_data}
        Adjustment Reason: {reason}
        
        Make appropriate adjustments:
        1. If behind schedule: accelerate or extend timeline
        2. If ahead of schedule: add more challenging content
        3. If struggling: provide more practice and review
        4. If excelling: introduce advanced topics
        
        Explain the reasoning for each adjustment.
        """
        
        adjustment_text = await self.llm_service.generate_response(prompt)
        
        return {
            "original_plan": current_plan,
            "adjusted_plan": adjustment_text,
            "adjustment_reason": reason,
            "key_changes": self._extract_key_changes(adjustment_text)
        }
    
    def _extract_key_changes(self, adjustment_text: str) -> List[str]:
        """Extract key changes from adjustment text"""
        changes = []
        lines = adjustment_text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['changed', 'modified', 'adjusted', 'updated']):
                changes.append(line.strip())
        
        return changes[:5]  # Limit to 5 changes
    
    async def _create_review_plan(self, state: AgentState) -> AgentResponse:
        """Create focused review plan"""
        try:
            topics_to_review = state.metadata.get("topics_to_review", [])
            review_timeline = state.metadata.get("review_timeline", "1 week")
            review_goals = state.metadata.get("review_goals", ["reinforce learning"])
            
            # Create review plan
            review_plan = await self._generate_review_plan(
                topics_to_review, review_timeline, review_goals
            )
            
            return self.create_response(
                response=f"Created review plan for {len(topics_to_review)} topics",
                confidence=0.9,
                metadata={"review_plan": review_plan}
            )
            
        except Exception as e:
            return self.create_response(
                response="Error creating review plan. Please try again.",
                confidence=0.1,
                metadata={"error": str(e)}
            )
    
    async def _generate_review_plan(self, topics: List[str], timeline: str, 
                                  goals: List[str]) -> Dict[str, Any]:
        """Generate focused review plan"""
        
        prompt = f"""
        Create a focused review plan for these topics:
        
        Topics: {', '.join(topics)}
        Timeline: {timeline}
        Goals: {', '.join(goals)}
        
        Include:
        1. Daily review schedule
        2. Spaced repetition intervals
        3. Practice exercises for each topic
        4. Self-assessment checkpoints
        5. Progress tracking methods
        
        Focus on reinforcement and retention.
        """
        
        review_text = await self.llm_service.generate_response(prompt)
        
        return {
            "topics": topics,
            "timeline": timeline,
            "goals": goals,
            "review_schedule": review_text,
            "estimated_hours": len(topics) * 2,  # 2 hours per topic
            "review_strategy": "spaced_repetition"
        }
    
    def get_capabilities(self) -> List[str]:
        """Return planner agent capabilities"""
        return [
            "Personalized study plan creation",
            "Schedule optimization",
            "Timeline management",
            "Milestone planning",
            "Progress-based plan adjustments",
            "Review plan generation",
            "Learning strategy selection",
            "Flexibility and adaptation"
        ]
