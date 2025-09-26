#!/usr/bin/env python3
"""
Demo script to showcase the new agent configuration and UI features
without requiring Azure credentials.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

def demo_sample_questions():
    """Demo the sample questions functionality."""
    print("🚕 Microsoft Fabric Taxi Data Analysis Agent - Demo")
    print("=" * 60)
    
    # Import sample questions
    try:
        from sample_agents_fabric import SAMPLE_QUESTIONS, get_query_by_selection, display_menu
        from taxi_query_functions import taxi_query_functions
        
        print(f"✅ Successfully loaded {len(SAMPLE_QUESTIONS)} sample questions from sample.txt")
        print(f"✅ Successfully loaded {len(taxi_query_functions)} taxi query functions")
        print()
        
        # Show the sample questions
        print("📝 Sample Questions (used for agent personality definition):")
        print("-" * 50)
        for i, question in enumerate(SAMPLE_QUESTIONS, 1):
            print(f"{i}. {question}")
            print()
        
        # Demo query selection
        print("🎯 Demo: Query Selection Function")
        print("-" * 30)
        test_selection = "1"
        selected_query = get_query_by_selection(test_selection)
        print(f"Input: '{test_selection}'")
        print(f"Output: {selected_query[:60]}...")
        print()
        
        # Show menu format
        print("📋 CLI Menu Preview:")
        print("-" * 20)
        display_menu()
        
        print("\n🔧 Implementation Features:")
        print("- ✅ Agent configuration based on sample.txt questions")
        print("- ✅ Simplified CLI menu (1-5, 9, 0)")
        print("- ✅ Chainlit UI with hint buttons")
        print("- ✅ Agent lifecycle management")
        print("- ✅ Agent ID display in both interfaces")
        
        print("\n🚀 Usage:")
        print("CLI:     python sample_agents_fabric.py")
        print("Web UI:  chainlit run chainlit_app.py")
        
        print("\n✨ Demo completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all files are in the same directory.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    demo_sample_questions()