#!/usr/bin/env python3
"""
Test script to verify the Chainlit agent application structure and basic functionality
without requiring actual Azure credentials or Databricks connection.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

def test_application_structure():
    """Test the application structure and key components."""
    print("🧪 Testing application structure...")
    
    # Add the current directory to Python path for imports
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    try:
        # Test that all key files exist
        required_files = [
            'chainlit_agent_adb_genie.py',
            'requirements.txt',
            '.env.template',
            'CHAINLIT_README.md',
            '.chainlit/config.toml'
        ]
        
        for file_name in required_files:
            file_path = current_dir / file_name
            if not file_path.exists():
                print(f"❌ Missing required file: {file_name}")
                return False
            else:
                print(f"✅ Found: {file_name}")
        
        # Test requirements.txt contains chainlit
        requirements_path = current_dir / 'requirements.txt'
        with open(requirements_path) as f:
            requirements = f.read()
            if 'chainlit' not in requirements:
                print("❌ chainlit not found in requirements.txt")
                return False
            else:
                print("✅ chainlit found in requirements.txt")
        
        # Test application structure by parsing the file
        app_path = current_dir / 'chainlit_agent_adb_genie.py'
        with open(app_path) as f:
            app_content = f.read()
        
        # Check for required components
        required_components = [
            '@cl.on_chat_start',
            '@cl.on_message', 
            '@cl.on_stop',
            '@cl.action_callback',
            'SAMPLE_QUESTIONS',
            'AGENT_INSTRUCTIONS',
            'ask_genie'
        ]
        
        for component in required_components:
            if component not in app_content:
                print(f"❌ Missing component: {component}")
                return False
            else:
                print(f"✅ Found component: {component}")
        
        # Verify agent instructions match sample.txt content
        if 'samples.nyctaxi.trips' not in app_content:
            print("❌ Agent instructions don't reference the correct dataset")
            return False
        else:
            print("✅ Agent instructions reference correct dataset")
            
        if 'fare statistics' not in app_content.lower():
            print("❌ Agent instructions don't include fare statistics capability")
            return False
        else:
            print("✅ Agent instructions include fare statistics")
        
        print("\n✅ All application structure tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing application structure: {e}")
        return False

def test_sample_questions():
    """Test that sample questions are properly configured."""
    print("\n🧪 Testing sample questions configuration...")
    
    current_dir = Path(__file__).parent
    app_path = current_dir / 'chainlit_agent_adb_genie.py'
    
    with open(app_path) as f:
        content = f.read()
    
    # Extract sample questions using regex
    import re
    sample_questions_match = re.search(r'SAMPLE_QUESTIONS = \[(.*?)\]', content, re.DOTALL)
    
    if not sample_questions_match:
        print("❌ Could not find SAMPLE_QUESTIONS")
        return False
    
    questions_str = sample_questions_match.group(1)
    questions = re.findall(r'"([^"]+)"', questions_str)
    
    if len(questions) != 5:
        print(f"❌ Expected 5 sample questions, found {len(questions)}")
        return False
    
    print(f"✅ Found {len(questions)} sample questions:")
    for i, question in enumerate(questions, 1):
        print(f"   {i}. {question.split('(')[0].strip()}")
    
    # Check for expected question types
    expected_topics = [
        ('fare', ['fare']),
        ('time-based', ['hour', 'day', 'week', 'time']),
        ('distance', ['distance']),
        ('geographic', ['zip code', 'pickup', 'dropoff']),
        ('outlier', ['outlier', 'unusual'])
    ]
    
    for topic_name, keywords in expected_topics:
        if not any(any(keyword.lower() in q.lower() for keyword in keywords) for q in questions):
            print(f"❌ Missing question about {topic_name}")
            return False
    
    print("✅ All expected question topics found")
    return True

def test_chainlit_config():
    """Test Chainlit configuration."""
    print("\n🧪 Testing Chainlit configuration...")
    
    current_dir = Path(__file__).parent
    config_path = current_dir / '.chainlit' / 'config.toml'
    
    if not config_path.exists():
        print("❌ Chainlit config.toml not found")
        return False
    
    with open(config_path) as f:
        config_content = f.read()
    
    # Check for key configuration items
    required_config = [
        'name = "Databricks Taxi Data Analysis Agent"',
        'enable_telemetry = false',
        'show_readme_as_default = true'
    ]
    
    for config_item in required_config:
        if config_item not in config_content:
            print(f"❌ Missing config: {config_item}")
            return False
        else:
            print(f"✅ Found config: {config_item}")
    
    return True

def test_environment_template():
    """Test environment template."""
    print("\n🧪 Testing environment template...")
    
    current_dir = Path(__file__).parent
    env_template_path = current_dir / '.env.template'
    
    with open(env_template_path) as f:
        template_content = f.read()
    
    required_vars = [
        'FOUNDRY_PROJECT_ENDPOINT',
        'FOUNDRY_DATABRICKS_CONNECTION_NAME',
        'MODEL_DEPLOYMENT_NAME'
    ]
    
    for var in required_vars:
        if var not in template_content:
            print(f"❌ Missing environment variable: {var}")
            return False
        else:
            print(f"✅ Found environment variable: {var}")
    
    return True

def main():
    """Run all tests."""
    print("🚀 Starting Chainlit Agent Application Tests\n")
    
    tests = [
        test_application_structure,
        test_sample_questions,
        test_chainlit_config,
        test_environment_template
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "="*50)
    if all(results):
        print("🎉 ALL TESTS PASSED!")
        print("\nThe Chainlit agent application is properly structured and ready to use.")
        print("\nTo run the application:")
        print("1. Copy .env.template to .env and fill in your values")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run: chainlit run chainlit_agent_adb_genie.py")
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        failed_count = len([r for r in results if not r])
        print(f"Failed: {failed_count}/{len(tests)} tests")
        return 1

if __name__ == "__main__":
    exit(main())