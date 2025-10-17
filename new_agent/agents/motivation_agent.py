"""
Motivation Agent - Progress Tracking and Gamification
=====================================================

This agent tracks user progress and provides gamified encouragement through
badges, streaks, and personalized motivation strategies.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base_agent import BaseAgent, AgentState, AgentResponse
from models import UserProgress, TestResult

class MotivationAgent(BaseAgent):
    """Agent responsible for motivation and gamification"""
    
    def __init__(self, llm_service):
        super().__init__("motivation", llm_service)
        self.badge_system = BadgeSystem()
        self.streak_tracker = StreakTracker()
        self.motivation_strategies = {
            "achievement": "Focus on accomplishments and milestones",
            "progress": "Emphasize continuous improvement",
            "social": "Encourage sharing and collaboration",
            "challenge": "Present learning as exciting challenges",
            "autonomy": "Highlight personal choice and control"
        }
    
    async def process(self, state: AgentState) -> AgentResponse:
        """Process motivation-related tasks"""
        try:
            action = state.metadata.get("action", "track_progress")
            
            if action == "track_progress":
                return await self._track_progress(state)
            elif action == "award_badges":
                return await self._award_badges(state)
            elif action == "update_streak":
                return await self._update_streak(state)
            elif action == "generate_motivation":
                return await self._generate_motivation(state)
            else:
                return self.create_response(
                    response="I can help with progress tracking, badges, streaks, and motivation. What would you like me to do?",
                    confidence=0.8
                )
                
        except Exception as e:
            return self.create_response(
                response="I encountered an error while processing your motivation request. Please try again.",
                confidence=0.1,
                metadata={"error": str(e)}
            )
    
    async def _track_progress(self, state: AgentState) -> AgentResponse:
        """Track and analyze user progress"""
        try:
            user_progress = state.metadata.get("user_progress")
            recent_activity = state.metadata.get("recent_activity", [])
            
            # Analyze progress patterns
            progress_analysis = await self._analyze_progress_patterns(user_progress, recent_activity)
            
            # Generate progress report
            progress_report = await self._generate_progress_report(progress_analysis)
            
            return self.create_response(
                response=progress_report,
                confidence=0.9,
                metadata={
                    "progress_analysis": progress_analysis,
                    "achievements": progress_analysis.get("achievements", []),
                    "recommendations": progress_analysis.get("recommendations", [])
                }
            )
            
        except Exception as e:
            return self.create_response(
                response="Error tracking progress. Please try again.",
                confidence=0.1,
                metadata={"error": str(e)}
            )
    
    async def _analyze_progress_patterns(self, user_progress: Optional[UserProgress], 
                                       recent_activity: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user progress patterns and trends"""
        
        if not user_progress:
            return {"error": "No progress data available"}
        
        # Calculate key metrics
        total_lessons = len(user_progress.completed_lessons)
        avg_score = sum(user_progress.test_scores) / len(user_progress.test_scores) if user_progress.test_scores else 0
        
        # Analyze trends
        recent_scores = user_progress.test_scores[-5:] if len(user_progress.test_scores) >= 5 else user_progress.test_scores
        trend = "improving" if len(recent_scores) >= 2 and recent_scores[-1] > recent_scores[0] else "stable"
        
        # Identify achievements
        achievements = self._identify_achievements(user_progress, recent_activity)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(user_progress, achievements)
        
        return {
            "total_lessons_completed": total_lessons,
            "average_score": round(avg_score, 1),
            "current_difficulty": user_progress.current_difficulty,
            "trend": trend,
            "achievements": achievements,
            "recommendations": recommendations,
            "streak_days": self.streak_tracker.get_current_streak(user_progress.user_id),
            "next_milestone": self._get_next_milestone(total_lessons)
        }
    
    def _identify_achievements(self, user_progress: UserProgress, 
                             recent_activity: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Identify new achievements based on progress"""
        achievements = []
        
        # Lesson completion achievements
        if len(user_progress.completed_lessons) >= 5:
            achievements.append({
                "badge": "🎓",
                "title": "First Steps",
                "description": "Completed 5 lessons"
            })
        
        if len(user_progress.completed_lessons) >= 10:
            achievements.append({
                "badge": "📚",
                "title": "Dedicated Learner",
                "description": "Completed 10 lessons"
            })
        
        # Score achievements
        if user_progress.test_scores and max(user_progress.test_scores) >= 90:
            achievements.append({
                "badge": "⭐",
                "title": "Excellence",
                "description": "Achieved 90% or higher on a test"
            })
        
        # Consistency achievements
        if len(user_progress.test_scores) >= 3 and all(score >= 80 for score in user_progress.test_scores[-3:]):
            achievements.append({
                "badge": "🔥",
                "title": "Consistent Performer",
                "description": "Scored 80%+ on last 3 tests"
            })
        
        return achievements
    
    async def _generate_recommendations(self, user_progress: UserProgress, 
                                      achievements: List[Dict[str, str]]) -> List[str]:
        """Generate personalized recommendations"""
        
        recommendations = []
        
        # Based on current difficulty
        if user_progress.current_difficulty == "easy" and user_progress.test_scores and max(user_progress.test_scores) >= 85:
            recommendations.append("You're excelling at the easy level! Consider trying medium difficulty lessons.")
        
        # Based on recent performance
        if user_progress.test_scores and len(user_progress.test_scores) >= 2:
            recent_avg = sum(user_progress.test_scores[-2:]) / 2
            if recent_avg < 70:
                recommendations.append("Your recent scores suggest you might benefit from reviewing previous lessons.")
            elif recent_avg >= 90:
                recommendations.append("Excellent performance! You're ready for more challenging content.")
        
        # Based on progress pace
        if len(user_progress.completed_lessons) > 0:
            recommendations.append("Keep up the great work! Consistency is key to learning success.")
        
        return recommendations
    
    def _get_next_milestone(self, current_lessons: int) -> Dict[str, Any]:
        """Get next milestone information"""
        milestones = [5, 10, 15, 20, 25, 50, 100]
        
        for milestone in milestones:
            if current_lessons < milestone:
                return {
                    "target": milestone,
                    "remaining": milestone - current_lessons,
                    "description": f"Complete {milestone} lessons"
                }
        
        return {
            "target": "Master",
            "remaining": 0,
            "description": "You've reached all milestones! 🎉"
        }
    
    async def _generate_progress_report(self, analysis: Dict[str, Any]) -> str:
        """Generate motivational progress report"""
        
        if "error" in analysis:
            return "I don't have enough data to generate a progress report yet. Keep learning and I'll track your progress!"
        
        report = f"""
# 📊 Your Learning Progress Report

## 🎯 Current Status
- **Lessons Completed:** {analysis['total_lessons_completed']}
- **Average Score:** {analysis['average_score']}%
- **Current Difficulty:** {analysis['current_difficulty'].title()}
- **Learning Trend:** {analysis['trend'].title()}
- **Study Streak:** {analysis['streak_days']} days

## 🏆 Recent Achievements
"""
        
        if analysis['achievements']:
            for achievement in analysis['achievements']:
                report += f"- {achievement['badge']} **{achievement['title']}**: {achievement['description']}\n"
        else:
            report += "- Keep learning to unlock achievements!\n"
        
        report += f"""
## 🎯 Next Milestone
**{analysis['next_milestone']['description']}** ({analysis['next_milestone']['remaining']} lessons to go)

## 💡 Recommendations
"""
        
        for recommendation in analysis['recommendations']:
            report += f"- {recommendation}\n"
        
        report += "\nKeep up the excellent work! 🚀"
        
        return report
    
    async def _award_badges(self, state: AgentState) -> AgentResponse:
        """Award badges based on achievements"""
        try:
            user_id = state.user_id
            achievement_type = state.metadata.get("achievement_type", "")
            
            # Check for badge eligibility
            new_badges = self.badge_system.check_eligibility(user_id, achievement_type)
            
            if new_badges:
                badge_message = await self._create_badge_message(new_badges)
                return self.create_response(
                    response=badge_message,
                    confidence=0.9,
                    metadata={"new_badges": new_badges}
                )
            else:
                return self.create_response(
                    response="Keep learning to earn more badges! 🏆",
                    confidence=0.8
                )
                
        except Exception as e:
            return self.create_response(
                response="Error awarding badges. Please try again.",
                confidence=0.1,
                metadata={"error": str(e)}
            )
    
    async def _create_badge_message(self, badges: List[Dict[str, str]]) -> str:
        """Create celebratory message for new badges"""
        
        if len(badges) == 1:
            badge = badges[0]
            return f"""
# 🎉 Congratulations!

You've earned a new badge:

**{badge['badge']} {badge['title']}**
{badge['description']}

Keep up the amazing work! 🚀
"""
        else:
            message = "# 🎉 Amazing! You've earned multiple badges:\n\n"
            for badge in badges:
                message += f"**{badge['badge']} {badge['title']}** - {badge['description']}\n"
            message += "\nYou're on fire! 🔥"
            return message
    
    async def _update_streak(self, state: AgentState) -> AgentResponse:
        """Update and track learning streak"""
        try:
            user_id = state.user_id
            activity_type = state.metadata.get("activity_type", "lesson_completed")
            
            # Update streak
            streak_info = self.streak_tracker.update_streak(user_id, activity_type)
            
            streak_message = await self._create_streak_message(streak_info)
            
            return self.create_response(
                response=streak_message,
                confidence=0.9,
                metadata={"streak_info": streak_info}
            )
            
        except Exception as e:
            return self.create_response(
                response="Error updating streak. Please try again.",
                confidence=0.1,
                metadata={"error": str(e)}
            )
    
    async def _create_streak_message(self, streak_info: Dict[str, Any]) -> str:
        """Create motivational streak message"""
        
        current_streak = streak_info.get("current_streak", 0)
        longest_streak = streak_info.get("longest_streak", 0)
        
        if current_streak == 0:
            return "Start your learning streak today! 🔥"
        elif current_streak == 1:
            return "Great start! You've begun your learning streak! 🔥"
        elif current_streak < 7:
            return f"Awesome! {current_streak} day streak! Keep it going! 🔥"
        elif current_streak < 30:
            return f"Impressive! {current_streak} day streak! You're building great habits! 🔥"
        else:
            return f"Incredible! {current_streak} day streak! You're a learning champion! 🏆"
    
    async def _generate_motivation(self, state: AgentState) -> AgentResponse:
        """Generate personalized motivation message"""
        try:
            user_mood = state.metadata.get("mood", "neutral")
            recent_performance = state.metadata.get("recent_performance", "good")
            learning_goals = state.metadata.get("learning_goals", [])
            
            motivation_message = await self._create_motivation_message(
                user_mood, recent_performance, learning_goals
            )
            
            return self.create_response(
                response=motivation_message,
                confidence=0.9,
                metadata={
                    "mood": user_mood,
                    "performance": recent_performance,
                    "motivation_type": "personalized"
                }
            )
            
        except Exception as e:
            return self.create_response(
                response="You're doing great! Keep up the excellent work! 💪",
                confidence=0.8,
                metadata={"error": str(e)}
            )
    
    async def _create_motivation_message(self, mood: str, performance: str, 
                                       goals: List[str]) -> str:
        """Create personalized motivation message"""
        
        prompt = f"""
        Create a personalized motivation message for a learner with:
        - Mood: {mood}
        - Recent Performance: {performance}
        - Learning Goals: {', '.join(goals) if goals else 'General learning'}
        
        Make it:
        - Encouraging and positive
        - Specific to their situation
        - Actionable and inspiring
        - Appropriate for their mood and performance
        
        Keep it concise but impactful.
        """
        
        return await self.llm_service.generate_response(prompt)
    
    def get_capabilities(self) -> List[str]:
        """Return motivation agent capabilities"""
        return [
            "Progress tracking and analysis",
            "Achievement and badge system",
            "Learning streak tracking",
            "Personalized motivation messages",
            "Performance trend analysis",
            "Milestone recognition",
            "Gamification elements",
            "Learning habit formation"
        ]

class BadgeSystem:
    """Manages badge system for gamification"""
    
    def __init__(self):
        self.badges = {
            "first_lesson": {"badge": "🎓", "title": "First Steps", "description": "Completed your first lesson"},
            "perfect_score": {"badge": "⭐", "title": "Perfectionist", "description": "Scored 100% on a test"},
            "week_streak": {"badge": "🔥", "title": "Week Warrior", "description": "7-day learning streak"},
            "month_streak": {"badge": "🏆", "title": "Monthly Master", "description": "30-day learning streak"},
            "helpful_peer": {"badge": "🤝", "title": "Helper", "description": "Helped another learner"},
            "quick_learner": {"badge": "⚡", "title": "Speed Demon", "description": "Completed lesson in record time"}
        }
    
    def check_eligibility(self, user_id: str, achievement_type: str) -> List[Dict[str, str]]:
        """Check if user is eligible for new badges"""
        # This would typically check against user's actual progress data
        # For now, return mock badges based on achievement type
        eligible_badges = []
        
        if achievement_type == "lesson_completed":
            eligible_badges.append(self.badges["first_lesson"])
        elif achievement_type == "perfect_score":
            eligible_badges.append(self.badges["perfect_score"])
        elif achievement_type == "week_streak":
            eligible_badges.append(self.badges["week_streak"])
        
        return eligible_badges

class StreakTracker:
    """Tracks learning streaks for gamification"""
    
    def __init__(self):
        self.streaks = {}  # In production, this would be stored in a database
    
    def get_current_streak(self, user_id: str) -> int:
        """Get current learning streak for user"""
        return self.streaks.get(user_id, {}).get("current_streak", 0)
    
    def update_streak(self, user_id: str, activity_type: str) -> Dict[str, Any]:
        """Update user's learning streak"""
        if user_id not in self.streaks:
            self.streaks[user_id] = {
                "current_streak": 0,
                "longest_streak": 0,
                "last_activity": None
            }
        
        user_streak = self.streaks[user_id]
        today = datetime.now().date()
        
        # Check if this is a new day
        if user_streak["last_activity"] != today:
            # Check if streak should continue (within 24 hours)
            if user_streak["last_activity"] and (today - user_streak["last_activity"]).days <= 1:
                user_streak["current_streak"] += 1
            else:
                user_streak["current_streak"] = 1
            
            user_streak["last_activity"] = today
            user_streak["longest_streak"] = max(user_streak["current_streak"], user_streak["longest_streak"])
        
        return {
            "current_streak": user_streak["current_streak"],
            "longest_streak": user_streak["longest_streak"],
            "last_activity": user_streak["last_activity"]
        }
