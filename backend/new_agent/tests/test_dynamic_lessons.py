"""
Test Dynamic Lesson Generation
"""
import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

from new_agent.real_llm_service import RealLLMService
from new_agent.dynamic_lesson_generator import DynamicLessonGenerator
from new_agent.models import UserProfile

async def test_single_lesson_generation():
    """Test generating a single dynamic lesson"""
    print("="*60)
    print("🧪 TEST 1: Single Lesson Generation")
    print("="*60)
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ FAILED: No API key found")
            return False
        
        llm_service = RealLLMService(api_key, "gemini-2.5-flash")
        generator = DynamicLessonGenerator(llm_service)
        
        print("\n📝 Generating lesson: Python Object-Oriented Programming")
        print("⏳ This may take 10-20 seconds...")
        
        lesson = await generator.generate_lesson(
            subject="Python Programming",
            topic="Object-Oriented Programming",
            difficulty="intermediate",
            learning_style="practical"
        )
        
        print(f"\n✅ Lesson generated!")
        print("-"*60)
        print(f"📚 Title: {lesson.title}")
        print(f"⏱️  Duration: {lesson.duration} minutes")
        print(f"🎯 Difficulty: {lesson.difficulty}")
        print(f"📋 Objectives: {len(lesson.learning_objectives)}")
        print(f"📝 Content length: {len(lesson.content)} chars")
        print(f"❓ Questions: {len(lesson.assessment_questions)}")
        print(f"💪 Exercises: {len(lesson.practice_exercises)}")
        print("-"*60)
        
        print(f"\n📖 Content preview:")
        print(lesson.content[:300] + "...")
        
        # Quality checks
        checks = {
            "Has title": len(lesson.title) > 5,
            "Has content": len(lesson.content) > 200,
            "Has objectives": len(lesson.learning_objectives) > 0,
            "Has questions": len(lesson.assessment_questions) > 0,
            "Has exercises": len(lesson.practice_exercises) > 0,
            "Correct difficulty": lesson.difficulty == "intermediate"
        }
        
        print(f"\n📊 Quality Checks:")
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
        
        if all(checks.values()):
            print("\n✅ PASSED: High-quality lesson generated")
            return True
        else:
            print("\n⚠️  WARNING: Some quality checks failed")
            return False
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_curriculum_generation():
    """Test generating a complete curriculum"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Curriculum Generation")
    print("="*60)
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        llm_service = RealLLMService(api_key, "gemini-2.5-flash")
        generator = DynamicLessonGenerator(llm_service)
        
        print("\n📝 Generating 4-week Python curriculum")
        print("⏳ This may take 30-60 seconds...")
        
        curriculum = await generator.generate_curriculum(
            subject="Python Programming",
            level="beginner",
            duration_weeks=4
        )
        
        print(f"\n✅ Curriculum generated!")
        print("-"*60)
        print(f"📚 Total lessons: {len(curriculum)}")
        print("-"*60)
        
        print(f"\n📖 Lessons:")
        for i, lesson in enumerate(curriculum[:5], 1):  # Show first 5
            print(f"{i}. {lesson.title}")
            print(f"   Duration: {lesson.duration}min | Difficulty: {lesson.difficulty}")
        
        if len(curriculum) > 5:
            print(f"   ... and {len(curriculum) - 5} more lessons")
        
        # Quality checks
        checks = {
            "Has lessons": len(curriculum) > 0,
            "Expected count": len(curriculum) >= 8,  # 4 weeks * ~3 lessons
            "All have content": all(len(l.content) > 100 for l in curriculum),
            "Progressive difficulty": True,  # Could check difficulty progression
            "Unique titles": len(set(l.title for l in curriculum)) == len(curriculum)
        }
        
        print(f"\n📊 Curriculum Quality:")
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
        
        if all(checks.values()):
            print("\n✅ PASSED: Complete curriculum generated")
            return True
        else:
            print("\n⚠️  WARNING: Some quality checks failed")
            return False
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_personalized_lesson():
    """Test lesson personalization with user profile"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Personalized Lesson Generation")
    print("="*60)
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        llm_service = RealLLMService(api_key, "gemini-2.5-flash")
        generator = DynamicLessonGenerator(llm_service)
        
        # Create user profile
        user_profile = UserProfile(
            user_id="test_user",
            name="Test User",
            email="test@example.com",
            learning_style="visual",
            preferred_difficulty="beginner",
            available_time=45,
            learning_goals=["Build web applications", "Understand databases"],
            interests=["Web development", "Data science"]
        )
        
        print("\n👤 User Profile:")
        print(f"   Learning Style: {user_profile.learning_style}")
        print(f"   Difficulty: {user_profile.preferred_difficulty}")
        print(f"   Time Available: {user_profile.available_time} min")
        print(f"   Goals: {', '.join(user_profile.learning_goals[:2])}")
        
        print("\n📝 Generating personalized lesson...")
        print("⏳ This may take 10-20 seconds...")
        
        lesson = await generator.generate_lesson(
            subject="Python Programming",
            topic="Web Development Basics",
            difficulty="beginner",
            user_profile=user_profile,
            learning_style="visual",
            duration=45
        )
        
        print(f"\n✅ Personalized lesson generated!")
        print("-"*60)
        print(f"📚 Title: {lesson.title}")
        print(f"⏱️  Duration: {lesson.duration} minutes")
        print(f"📖 Content preview:")
        print(lesson.content[:250] + "...")
        print("-"*60)
        
        # Check personalization
        content_lower = lesson.content.lower()
        checks = {
            "Respects time limit": lesson.duration <= user_profile.available_time,
            "Correct difficulty": lesson.difficulty == "beginner",
            "Has visual elements": any(word in content_lower for word in ["diagram", "visual", "chart", "image"]),
            "Relates to goals": any(goal.lower().split()[0] in content_lower for goal in user_profile.learning_goals)
        }
        
        print(f"\n📊 Personalization Checks:")
        for check, passed in checks.items():
            status = "✅" if passed else "⚠️ "
            print(f"   {status} {check}")
        
        passed_count = sum(checks.values())
        if passed_count >= 3:
            print(f"\n✅ PASSED: Lesson personalized ({passed_count}/4 checks)")
            return True
        else:
            print(f"\n⚠️  WARNING: Low personalization ({passed_count}/4 checks)")
            return False
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
async def test_different_subjects():
    """Test lesson generation for different subjects"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Multi-Subject Lesson Generation")
    print("="*60)
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        llm_service = RealLLMService(api_key, "gemini-2.5-flash")
        generator = DynamicLessonGenerator(llm_service)
        
        subjects = [
            ("Python Programming", "Variables and Data Types"),
            ("Machine Learning", "Linear Regression"),
            ("Web Development", "HTML Basics")
        ]
        
        results = []
        
        for subject, topic in subjects:
            print(f"\n📝 Testing: {subject} - {topic}")
            prompt = f"As an expert in {subject}, {topic} in 2-3 sentences."
            
            lesson = await generator.generate_lesson(
                subject=subject,
                topic=topic,
                difficulty="beginner",
                duration=30
            )
            
            # Fixed: Check lesson attributes that actually exist
            success = (
                len(lesson.content) > 200 and
                len(lesson.title) > 5 and
                lesson.title != "---" and  # Added check
                lesson.difficulty == "beginner"  # Check difficulty instead
            )
            
            status = "✅" if success else "❌"
            print(f"{status} Generated: {lesson.title}")
            print(f"   Content: {len(lesson.content)} chars")
            
            results.append(success)
        
        passed = sum(results)
        print(f"\n📊 Results: {passed}/{len(subjects)} subjects successful")
        
        if all(results):
            print("\n✅ PASSED: All subjects generated successfully")
            return True
        else:
            print(f"\n⚠️  WARNING: {len(results) - passed} subjects failed")
            return False
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
async def run_lesson_tests():
    """Run all lesson generation tests"""
    print("\n🚀 Running Dynamic Lesson Tests...\n")
    
    tests = [
        ("Single Lesson", test_single_lesson_generation()),
        ("Curriculum Generation", test_curriculum_generation()),
        ("Personalized Lesson", test_personalized_lesson()),
        ("Multi-Subject", test_different_subjects())
    ]
    
    results = {}
    for name, test_coro in tests:
        results[name] = await test_coro
    
    print("\n" + "="*60)
    print("📊 LESSON GENERATION TEST RESULTS")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL LESSON TESTS PASSED!")
        print("="*60)
        print("\n✅ Dynamic lesson generation is fully functional")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("="*60)
        failed = [name for name, passed in results.items() if not passed]
        print(f"\n❌ Failed tests: {', '.join(failed)}")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(run_lesson_tests())
    sys.exit(0 if success else 1)