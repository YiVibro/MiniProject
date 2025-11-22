"""
Quick Test - Fast smoke test for rapid development
"""
import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

async def quick_test():
    """Quick smoke test"""
    print("🚀 Quick Test - Checking if system is working...\n")
    
    # Check 1: API Key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return False
    print(f"✅ API key found ({api_key[:10]}...)")
    
    # Check 2: Imports
    try:
        from new_agent.real_llm_service import RealLLMService
        print("✅ Imports working")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Check 3: API Call
    try:
        print("⏳ Testing API call...")
        service = RealLLMService(api_key, "gemini-2.5-flash")
        response = await service.generate_response("Say 'Hello' in one word")
        print(f"✅ API working - Response: {response[:50]}")
    except Exception as e:
        print(f"❌ API failed: {e}")
        return False
    
    # Check 4: Lesson Generation
    try:
        print("⏳ Testing lesson generation...")
        from new_agent.dynamic_lesson_generator import DynamicLessonGenerator
        generator = DynamicLessonGenerator(service)
        lesson = await generator.generate_lesson(
            subject="Python",
            topic="Variables",
            difficulty="beginner",
            duration=15
        )
        print(f"✅ Lesson generated - Title: {lesson.title}")
    except Exception as e:
        print(f"❌ Lesson generation failed: {e}")
        return False
    
    print("\n🎉 All quick tests passed! System is working.")
    return True

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)