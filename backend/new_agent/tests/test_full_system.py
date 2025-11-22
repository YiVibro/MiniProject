"""
Test Complete Tutoring System Integration
"""
import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

from new_agent.enhanced_tutoring_system import EnhancedTutoringSystem, SystemConfig
from new_agent.models import UserProfile

async def test_system_initialization():
    """Test system initialization"""
    print("="*60)
    print("🧪 TEST 1: System Initialization")
    print("="*60)
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ FAILED: No API key found")
            return False
        
        config = SystemConfig(
            llm_provider="google",
            llm_api_key=api_key,
            llm_model="gemini-1.5-flash",
            enable_analytics=True,
            enable_gap_analysis=True,
            enable_learning_curves=True,
            enable_mdp_recommendations=True
        )
        
        print("\n⏳ Initializing Enhanced Tutoring System...")
        system = EnhancedTutoringSystem(config)
        
        print("\n✅ System initialized!")
        print("-"*60)
        
        # Check components
        components = {
            "LLM Service": system.llm_service is not None,
            "Assessment System": system.assessment_system is not None,
            "Gap Analysis": system.gap_analysis_system is not None,
            "Learning Curves": system.learning_curve_tracker is not None,
            "Knowledge Agent": system.knowledge_agent is not None,
            "Practice Agent": system.practice_agent is not None,
            "Motivation Agent": system.motivation_agent is not None,
            "Planner Agent": system.planner_agent is not None,
            "Lesson Generator": system.lesson_generator is not None
        }
        
        print("📊 Component Status:")
        for component, status in components.items():
            symbol = "✅" if status else "❌"
            print(f"   {symbol} {component}")
        
        if all(components.values()):
            print("\n✅ PASSED: All components initialized")
            return True, system
        else:
            print("\n❌ FAILED: Some components missing")
            return False, None
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_dynamic_lesson_creation(system):
    """Test creating a dynamic lesson through the system"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Dynamic Lesson Creation")
    print("="*60)
    
    try:
        user_profile = UserProfile(
            user_id="test_user_001",
            name="Test User",
            email="test@example.com",
            learning_style="practical",
            preferred_difficulty="intermediate",
            available_time=30,
            learning_goals=["Learn Python"],
            interests=["Programming"]
        )
        
        system.user_profiles["test_user_001"] = user_profile
        
        print("\n📝 Creating dynamic lesson...")
        print("   Subject: Python Programming")
        print("   Topic: Functions and Modules")
        print("⏳ This may take 10-20 seconds...")
        
        lesson = await system.create_dynamic_lesson(
            subject="Python Programming",
            topic="Functions and Modules",
            difficulty="intermediate",
            user_profile=user_profile
        )
        
        print(f"\n✅ Lesson created!")
        print("-"*60)
        print(f"📚 ID: {lesson.lesson_id}")
        print(f"📖 Title: {lesson.title}")
        print(f"⏱️  Duration: {lesson.duration} minutes")
        print(f"🎯 Objectives: {len(lesson.learning_objectives)}")
        print(f"📝 Content: {len(lesson.content)} chars")
        print("-"*60)
        
        # Verify lesson is stored
        stored = lesson.lesson_id in system.lessons
        dynamic = lesson.lesson_id in system.dynamic_lessons
        
        checks = {
            "Lesson stored in system": stored,
            "Marked as dynamic": dynamic,
            "Has valid content": len(lesson.content) > 200,
            "Has objectives": len(lesson.learning_objectives) > 0,
            "Correct difficulty": lesson.difficulty == "intermediate"
        }
        
        print(f"\n📊 Verification:")
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
        
        if all(checks.values()):
            print("\n✅ PASSED: Dynamic lesson creation works")
            return True, lesson
        else:
            print("\n❌ FAILED: Some checks failed")
            return False, None
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_learning_session(system, lesson):
    """Test complete learning session"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Learning Session Flow")
    print("="*60)
    
    try:
        user_id = "test_user_001"
        
        print("\n📝 Starting learning session...")
        session_id = await system.start_learning_session(user_id, lesson.lesson_id)
        
        print(f"✅ Session started: {session_id}")
        
        # Test explanation request
        print("\n📝 Requesting concept explanation...")
        explanation_result = await system.process_user_interaction(
            session_id,
            "concept_explanation_requested",
            {
                "concept": "Python functions",
                "difficulty": "intermediate",
                "learning_style": "practical"
            }
        )
        
        print(f"✅ Explanation received ({len(explanation_result['explanation'])} chars)")
        print(f"   Preview: {explanation_result['explanation'][:100]}...")
        
        # Test practice request
        print("\n📝 Requesting practice questions...")
        practice_result = await system.process_user_interaction(
            session_id,
            "practice_requested",
            {
                "lesson_content": lesson.content[:500],
                "difficulty": "intermediate",
                "num_questions": 3
            }
        )
        
        questions = practice_result.get('practice_content', {}).get('questions', [])
        print(f"✅ Practice questions generated: {len(questions)}")
        
        # End session
        print("\n📝 Ending session...")
        summary = await system.end_learning_session(session_id)
        
        print(f"✅ Session ended")
        print(f"   Duration: {summary['duration_minutes']} minutes")
        print(f"   Engagement: {summary['engagement_score']:.2f}")
        
        checks = {
            "Session created": session_id is not None,
            "Explanation received": len(explanation_result.get('explanation', '')) > 50,
            "Practice generated": len(questions) > 0,
            "Session summary": 'duration_minutes' in summary
        }
        
        print(f"\n📊 Session Flow:")
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
        
        if all(checks.values()):
            print("\n✅ PASSED: Complete learning session works")
            return True
        else:
            print("\n❌ FAILED: Some checks failed")
            return False
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_personalized_learning_path(system):
    """Test creating personalized learning path"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Personalized Learning Path")
    print("="*60)
    
    try:
        user_id = "test_user_002"
        user_profile = UserProfile(
            user_id=user_id,
            name="Test User 2",
            email="test2@example.com",
            learning_style="visual",
            preferred_difficulty="beginner",
            available_time=60,
            learning_goals=["Master Python", "Build web apps"],
            interests=["Web development", "Data science"]
        )
        
        system.user_profiles[user_id] = user_profile
        
        print("\n📝 Creating personalized learning path...")
        print("   Request: 'I want to learn Python for web development in 3 months'")
        print("⏳ This may take 30-60 seconds...")
        
        path_id = await system.create_personalized_learning_path(
            user_id=user_id,
            user_request="I want to learn Python for web development in 3 months with weekly tests",
            user_profile=user_profile
        )
        
        print(f"\n✅ Learning path created!")
        print(f"   Path ID: {path_id}")
        
        # Get learning path details
        learning_path = system.learning_paths.get(path_id)
        
        if learning_path:
            print("-"*60)
            print(f"📚 Title: {learning_path.title}")
            print(f"⏱️  Duration: {learning_path.estimated_duration} minutes")
            print(f"📖 Lessons: {len(learning_path.lessons)}")
            print(f"🎯 Milestones: {len(learning_path.milestones)}")
            print("-"*60)
        
        checks = {
            "Path created": path_id is not None,
            "Path stored": learning_path is not None,
            "Has lessons": len(learning_path.lessons) > 0 if learning_path else False,
            "Has milestones": len(learning_path.milestones) > 0 if learning_path else False
        }
        
        print(f"\n📊 Learning Path:")
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
        
        if all(checks.values()):
            print("\n✅ PASSED: Personalized learning path created")
            return True
        else:
            print("\n❌ FAILED: Some checks failed")
            return False
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_system_status(system):
    """Test system status and metrics"""
    print("\n" + "="*60)
    print("🧪 TEST 5: System Status & Metrics")
    print("="*60)
    
    try:
        status = system.get_system_status()
        
        print("\n📊 System Status:")
        print("-"*60)
        print(f"Total Users: {status['total_users']}")
        print(f"Active Sessions: {status['active_sessions']}")
        print(f"Total Lessons: {status['total_lessons']}")
        print(f"Learning Paths: {status['total_learning_paths']}")
        print(f"Dynamic Lessons: {status.get('dynamic_lessons', 0)}")
        print("-"*60)
        
        print(f"\n🔧 Components:")
        for component, state in status['components_status'].items():
            symbol = "✅" if state == "active" else "⚠️ "
            print(f"   {symbol} {component}: {state}")
        
        checks = {
            "Has metrics": 'system_metrics' in status,
            "Has users": status['total_users'] > 0,
            "Has lessons": status['total_lessons'] > 0,
            "Dynamic generation enabled": status.get('dynamic_generation_enabled', False)
        }
        
        print(f"\n📊 Status Checks:")
        for check, passed in checks.items():
            status_symbol = "✅" if passed else "⚠️ "
            print(f"   {status_symbol} {check}")
        
        if sum(checks.values()) >= 3:
            print("\n✅ PASSED: System status tracking works")
            return True
        else:
            print("\n⚠️  WARNING: Some status checks failed")
            return False
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def run_full_system_tests():
    """Run all full system integration tests"""
    print("\n🚀 Running Full System Integration Tests...\n")
    
    # Test 1: Initialize system
    init_passed, system = await test_system_initialization()
    if not init_passed or not system:
        print("\n❌ Cannot continue - system initialization failed")
        return False
    
    # Test 2: Create dynamic lesson
    lesson_passed, lesson = await test_dynamic_lesson_creation(system)
    if not lesson_passed or not lesson:
        print("\n⚠️  Skipping session test - lesson creation failed")
        session_passed = False
    else:
        # Test 3: Learning session
        session_passed = await test_learning_session(system, lesson)
    
    # Test 4: Learning path
    path_passed = await test_personalized_learning_path(system)
    
    # Test 5: System status
    status_passed = await test_system_status(system)
    
    # Results
    results = {
        "System Initialization": init_passed,
        "Dynamic Lesson Creation": lesson_passed,
        "Learning Session": session_passed,
        "Personalized Learning Path": path_passed,
        "System Status": status_passed
    }
    
    print("\n" + "="*60)
    print("📊 FULL SYSTEM TEST RESULTS")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print("\n" + "="*60)
    print(f"Results: {passed_count}/{total_count} tests passed")
    print("="*60)
    
    if passed_count == total_count:
        print("\n🎉 ALL SYSTEM TESTS PASSED!")
        print("\n✅ The complete tutoring system is fully functional")
        print("✅ Dynamic content generation is working")
        print("✅ All agents are operational")
        print("✅ Integration is successful")
    elif passed_count >= 3:
        print("\n⚠️  MOST TESTS PASSED")
        print(f"\n✅ {passed_count}/{total_count} core features working")
        print("⚠️  Some features may need attention")
    else:
        print("\n❌ MULTIPLE TESTS FAILED")
        failed = [name for name, passed in results.items() if not passed]
        print(f"\n❌ Failed tests: {', '.join(failed)}")
        print("\n💡 Review errors above and fix issues")
    
    return passed_count >= 3

if __name__ == "__main__":
    success = asyncio.run(run_full_system_tests())
    sys.exit(0 if success else 1)
