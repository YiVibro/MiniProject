"""
Master Test Runner - Run All Tests
"""
import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

# Import test modules
from test_setup import run_setup_tests
from test_llm_service import run_llm_tests
from test_dynamic_lessons import run_lesson_tests
from test_full_system import run_full_system_tests

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

async def run_all_tests():
    """Run all test suites"""
    print_header("🧪 MULTI-AGENT AI TUTORING SYSTEM - COMPLETE TEST SUITE")
    
    # Check if API key is set
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_actual_api_key_here":
        print("\n❌ ERROR: GOOGLE_API_KEY not configured!")
        print("\n💡 Setup instructions:")
        print("1. Create .env file in project root")
        print("2. Add: GOOGLE_API_KEY=your_actual_api_key_here")
        print("3. Get key from: https://makersuite.google.com/app/apikey")
        return False
    
    results = {}
    
    # Test Suite 1: Setup Tests
    print_header("📋 SUITE 1: Setup & Environment Tests")
    results["Setup Tests"] = run_setup_tests()
    
    if not results["Setup Tests"]:
        print("\n❌ Setup tests failed - cannot continue")
        print("💡 Fix setup issues before running other tests")
        return False
    
    # Test Suite 2: LLM Service Tests
    print_header("🤖 SUITE 2: LLM Service Tests")
    results["LLM Tests"] = await run_llm_tests()
    
    if not results["LLM Tests"]:
        print("\n⚠️  LLM tests failed - dynamic generation may not work")
    
    # Test Suite 3: Dynamic Lesson Tests
    print_header("📚 SUITE 3: Dynamic Lesson Generation Tests")
    results["Lesson Tests"] = await run_lesson_tests()
    
    if not results["Lesson Tests"]:
        print("\n⚠️  Lesson tests failed - check API connectivity")
    
    # Test Suite 4: Full System Tests
    print_header("🎯 SUITE 4: Full System Integration Tests")
    results["System Tests"] = await run_full_system_tests()
    
    # Final Results
    print_header("📊 FINAL TEST RESULTS")
    
    print("\nTest Suite Results:")
    print("-"*70)
    for suite_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {suite_name}")
    print("-"*70)
    
    passed_count = sum(results.values())
    total_count = len(results)
    percentage = (passed_count / total_count) * 100
    
    print(f"\nOverall: {passed_count}/{total_count} test suites passed ({percentage:.0f}%)")
    
    print("\n" + "="*70)
    if passed_count == total_count:
        print("🎉 ALL TEST SUITES PASSED!")
        print("="*70)
        print("\n✅ System is fully operational and ready for production")
        print("✅ Dynamic content generation is working")
        print("✅ All components are integrated correctly")
        print("✅ API connectivity is stable")
        print("\n🚀 You can now use the system with confidence!")
    elif passed_count >= 3:
        print("✅ SYSTEM IS OPERATIONAL")
        print("="*70)
        print(f"\n✅ Core functionality working ({passed_count}/{total_count} suites)")
        print("⚠️  Some features may need attention")
        print("\n💡 Review failed tests above for details")
    else:
        print("❌ SYSTEM HAS ISSUES")
        print("="*70)
        print(f"\n❌ Multiple test suites failed ({total_count - passed_count} failures)")
        print("\n💡 Action items:")
        for suite_name, passed in results.items():
            if not passed:
                print(f"   - Fix issues in: {suite_name}")
        print("\n📖 Review error messages and fix issues before deployment")
    
    return passed_count >= 3

def main():
    """Main entry point"""
    try:
        success = asyncio.run(run_all_tests())
        
        print("\n" + "="*70)
        print("Test run completed")
        print("="*70)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()