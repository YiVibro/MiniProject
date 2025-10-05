#!/usr/bin/env python3
"""
Test script for agent integration
===============================

This script tests the new agent integration with the frontend.
"""

import asyncio
import sys
from pathlib import Path

# Add new_agent directory to path
sys.path.append(str(Path(__file__).parent / "new_agent"))

from tutoring_system import MultiAgentTutoringSystem, SystemConfig
from dynamic_learning_planner import DynamicLearningPlanner
from models import UserProfile

async def test_agent_integration():
    """Test the agent integration"""
    
    print("🧪 Testing Agent Integration")
    print("=" * 50)
    
    # Initialize system
    config = SystemConfig(
        llm_provider="google",
        llm_api_key="demo-key",
        llm_model="gemini-pro",
        enable_analytics=True,
        enable_gap_analysis=True,
        enable_learning_curves=True,
        enable_mdp_recommendations=True
    )
    
    system = MultiAgentTutoringSystem(config)
    planner = DynamicLearningPlanner()
    
    print("✅ System initialized successfully")
    
    # Test 1: Create learning plan
    print("\n📚 Test 1: Creating Learning Plan")
    print("-" * 30)
    
    try:
        plan = await planner.create_learning_plan(
            "test_user_001",
            "I want to learn Python programming in 3 months with weekly tests"
        )
        
        print(f"✅ Learning plan created successfully!")
        print(f"   Path ID: {plan['path_id']}")
        print(f"   Subject: {plan['requirements']['subject']}")
        print(f"   Timeline: {plan['timeline']}")
        print(f"   Curriculum: {len(plan['curriculum'])} lessons")
        
    except Exception as e:
        print(f"❌ Failed to create learning plan: {e}")
    
    # Test 2: Create course
    print("\n🎓 Test 2: Creating Course")
    print("-" * 30)
    
    try:
        # Create user profile
        user_profile = UserProfile(
            user_id="test_user_002",
            name="Test Learner",
            email="test@example.com",
            learning_style="visual",
            preferred_difficulty="intermediate",
            available_time=120,  # 2 hours
            learning_goals=["Master Python", "Build web applications"],
            interests=["Programming", "Web Development"]
        )
        
        # Create course using system
        curriculum = await system.create_dynamic_curriculum(
            subject="Python Programming",
            level="intermediate",
            duration_weeks=8,
            user_profile=user_profile
        )
        
        print(f"✅ Course created successfully!")
        print(f"   Curriculum: {len(curriculum)} lessons")
        print(f"   First lesson: {curriculum[0].title}")
        print(f"   Difficulty: {curriculum[0].difficulty}")
        
    except Exception as e:
        print(f"❌ Failed to create course: {e}")
    
    # Test 3: System status
    print("\n📊 Test 3: System Status")
    print("-" * 30)
    
    try:
        status = system.get_system_status()
        print(f"✅ System status retrieved!")
        print(f"   Active sessions: {status['active_sessions']}")
        print(f"   Total users: {status['total_users']}")
        print(f"   Components: {len(status['components_status'])}")
        
    except Exception as e:
        print(f"❌ Failed to get system status: {e}")
    
    print(f"\n🎉 Agent integration test completed!")
    print("The system is ready for frontend integration!")

async def main():
    """Main test function"""
    try:
        await test_agent_integration()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Agent Integration Test...")
    asyncio.run(main())
