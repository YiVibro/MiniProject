"""
Test Setup and Environment Configuration
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv

def test_environment_setup():
    """Test if environment is properly configured"""
    print("="*60)
    print("🧪 TEST 1: Environment Setup")
    print("="*60)
    
    # Load .env file
    env_path = Path(__file__).parent.parent.parent.parent / '.env'
    load_dotenv(env_path)
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ FAILED: GOOGLE_API_KEY not found in environment")
        print(f"   Looked for .env file at: {env_path}")
        print("\n💡 Fix: Create .env file with:")
        print("   GOOGLE_API_KEY=your_actual_api_key_here")
        return False
    
    if api_key == "your_actual_api_key_here" or api_key == "demo-key":
        print("❌ FAILED: GOOGLE_API_KEY is still placeholder")
        print("\n💡 Fix: Replace with actual API key from:")
        print("   https://makersuite.google.com/app/apikey")
        return False
    
    print(f"✅ PASSED: API key found (length: {len(api_key)} chars)")
    print(f"   Key preview: {api_key[:10]}...{api_key[-4:]}")
    return True

def test_dependencies():
    """Test if required packages are installed"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Package Dependencies")
    print("="*60)
    
    required_packages = {
        'google.generativeai': 'google-generativeai',
        'dotenv': 'python-dotenv',
        'pydantic': 'pydantic',
        'asyncio': 'asyncio (built-in)',
    }
    
    all_installed = True
    for module, package in required_packages.items():
        try:
            __import__(module.split('.')[0])
            print(f"✅ {package:<30} - Installed")
        except ImportError:
            print(f"❌ {package:<30} - Missing")
            all_installed = False
    
    if not all_installed:
        print("\n💡 Fix: Install missing packages:")
        print("   pip install google-generativeai python-dotenv pydantic")
        return False
    
    print("\n✅ PASSED: All required packages installed")
    return True

def test_imports():
    """Test if all module imports work"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Module Imports")
    print("="*60)
    
    modules_to_test = [
        ('new_agent.models', 'Data Models'),
        ('new_agent.llm_service', 'LLM Service'),
        ('new_agent.real_llm_service', 'Real LLM Service'),
        ('new_agent.tutoring_system', 'Tutoring System'),
        ('new_agent.dynamic_lesson_generator', 'Lesson Generator'),
        ('new_agent.enhanced_tutoring_system', 'Enhanced System'),
        ('new_agent.agents.knowledge_agent', 'Knowledge Agent'),
        ('new_agent.agents.practice_agent', 'Practice Agent'),
        ('new_agent.agents.motivation_agent', 'Motivation Agent'),
        ('new_agent.agents.planner_agent', 'Planner Agent'),
    ]
    
    all_imported = True
    for module_path, name in modules_to_test:
        try:
            __import__(module_path)
            print(f"✅ {name:<30} - OK")
        except Exception as e:
            print(f"❌ {name:<30} - FAILED: {str(e)[:40]}")
            all_imported = False
    
    if not all_imported:
        print("\n💡 Fix: Check import errors above and fix module paths")
        return False
    
    print("\n✅ PASSED: All modules import successfully")
    return True

def run_setup_tests():
    """Run all setup tests"""
    print("\n🚀 Running Setup Tests...\n")
    
    results = {
        "Environment Setup": test_environment_setup(),
        "Package Dependencies": test_dependencies(),
        "Module Imports": test_imports()
    }
    
    print("\n" + "="*60)
    print("📊 SETUP TEST RESULTS")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL SETUP TESTS PASSED!")
        print("="*60)
        print("\n✅ System is ready for testing")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("="*60)
        print("\n❌ Fix the issues above before proceeding")
    
    return all_passed

if __name__ == "__main__":
    success = run_setup_tests()
    sys.exit(0 if success else 1)