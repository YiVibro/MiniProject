"""
Test Real LLM Service - Actual API Calls
"""
import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

from new_agent.real_llm_service import RealLLMService

async def test_basic_generation():
    """Test basic text generation"""
    print("="*60)
    print("🧪 TEST 1: Basic Text Generation")
    print("="*60)
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ FAILED: No API key found")
            return False
        
        service = RealLLMService(api_key, "gemini-2.5-flash")
        
        prompt = "Explain what Python is in exactly 2 sentences."
        print(f"\n📝 Prompt: {prompt}")
        print("\n⏳ Calling Gemini API...")
        
        response = await service.generate_response(prompt)
        
        print(f"\n✅ Response received ({len(response)} chars):")
        print("-"*60)
        print(response)
        print("-"*60)
        
        # Verify response is not fallback
        if "fallback content" in response.lower():
            print("\n⚠️  WARNING: Received fallback content (API may have failed)")
            return False
        
        print(f"\n📊 Stats:")
        print(f"   - Requests made: {service.request_count}")
        print(f"   - Total tokens: {service.total_tokens}")
        
        print("\n✅ PASSED: Basic generation works")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False

async def test_lesson_generation():
    """Test dynamic lesson content generation"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Dynamic Lesson Generation")
    print("="*60)
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        service = RealLLMService(api_key, "gemini-2.5-flash")
        
        prompt = """
        Create a beginner-level Python lesson about variables.
        
        Include:
        1. Clear introduction
        2. 3 key concepts
        3. 2 code examples
        4. 2 practice exercises
        
        Keep it concise but educational.
        """
        
        print(f"\n📝 Generating Python variables lesson...")
        print("\n⏳ Calling Gemini API...")
        
        response = await service.generate_response(prompt)
        
        print(f"\n✅ Lesson generated ({len(response)} chars):")
        print("-"*60)
        print(response[:500] + "..." if len(response) > 500 else response)
        print("-"*60)
        
        # Check for key components
        checks = {
            "Has code examples": "```" in response or "def " in response,
            "Has structure": any(marker in response for marker in ["#", "##", "1.", "2."]),
            "Good length": len(response) > 200,
            "Not fallback": "fallback content" not in response.lower()
        }
        
        print(f"\n📊 Content Quality Checks:")
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
        return False

async def test_structured_generation():
    """Test structured JSON generation"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Structured JSON Generation")
    print("="*60)
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        service = RealLLMService(api_key, "gemini-2.5-flash")
        
        schema = {
            "title": "string",
            "difficulty": "string",
            "objectives": "array",
            "estimated_time": "number"
        }
        
        prompt = "Create a lesson about Python functions for beginners"
        
        print(f"\n📝 Generating structured data...")
        print(f"Schema: {schema}")
        print("\n⏳ Calling Gemini API...")
        
        response = await service.generate_structured_response(prompt, schema)
        
        print(f"\n✅ Structured data received:")
        print("-"*60)
        import json
        print(json.dumps(response, indent=2))
        print("-"*60)
        
        # Verify structure
        checks = {
            "Has all keys": all(key in response for key in schema.keys()),
            "Correct types": (
                isinstance(response.get("title"), str) and
                isinstance(response.get("difficulty"), str) and
                isinstance(response.get("objectives"), list) and
                isinstance(response.get("estimated_time"), (int, float))
            ),
            "Valid content": len(str(response.get("title", ""))) > 5
        }
        
        print(f"\n📊 Structure Validation:")
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
        
        if all(checks.values()):
            print("\n✅ PASSED: Structured generation works")
            return True
        else:
            print("\n⚠️  WARNING: Structure validation failed")
            return False
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False

async def test_multiple_subjects():
    """Test generation for different subjects"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Multi-Subject Generation")
    print("="*60)
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        service = RealLLMService(api_key, "gemini-2.5-flash")
        
        subjects = [
            ("Python", "Explain list comprehensions"),
            ("Machine Learning", "Explain supervised learning"),
            ("Web Development", "Explain REST APIs")
        ]
        
        results = []
        
        for subject, topic in subjects:
            print(f"\n📝 Testing: {subject} - {topic}")
            prompt = f"As an expert in {subject}, {topic} in 2-3 sentences."
            
            response = await service.generate_response(prompt)
            success = len(response) > 50 and "fallback" not in response.lower()
            
            status = "✅" if success else "❌"
            print(f"{status} Response: {response[:100]}...")
            
            results.append(success)
        
        if all(results):
            print("\n✅ PASSED: All subjects generated successfully")
            return True
        else:
            print(f"\n⚠️  WARNING: {results.count(False)} subjects failed")
            return False
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False

async def run_llm_tests():
    """Run all LLM service tests"""
    print("\n🚀 Running LLM Service Tests...\n")
    
    tests = [
        ("Basic Generation", test_basic_generation()),
        ("Lesson Generation", test_lesson_generation()),
        ("Structured Generation", test_structured_generation()),
        ("Multi-Subject", test_multiple_subjects())
    ]
    
    results = {}
    for name, test_coro in tests:
        results[name] = await test_coro
    
    print("\n" + "="*60)
    print("📊 LLM SERVICE TEST RESULTS")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL LLM TESTS PASSED!")
        print("="*60)
        print("\n✅ Gemini API integration is working correctly")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("="*60)
        failed = [name for name, passed in results.items() if not passed]
        print(f"\n❌ Failed tests: {', '.join(failed)}")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(run_llm_tests())
    sys.exit(0 if success else 1)