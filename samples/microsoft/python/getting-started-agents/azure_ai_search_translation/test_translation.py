#!/usr/bin/env python3
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Test script for Azure AI Search translation functionality.

This script validates that the translation system works correctly
without requiring actual Azure AI Search connections.
"""

import os
import sys
from pathlib import Path

def setup_module_path():
    """Setup module path for imports."""
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))

# Setup path before importing our modules
setup_module_path()

# Now we can import our translation modules
from translation_utils import TranslationManager, get_available_languages, detect_user_language  # noqa: E402


def test_translation_loading():
    """Test that translation files load correctly."""
    print("Testing translation file loading...")
    
    available_languages = get_available_languages()
    print(f"Available languages: {available_languages}")
    
    for lang in available_languages:
        print(f"  Testing {lang}...")
        translator = TranslationManager(lang)
        
        # Test basic translation access
        agent_message = translator.get_message_translation("agent_created", agent_id="test-123")
        print(f"    Agent created message: {agent_message}")
        
        query = translator.get_query_translation("temperature_rating")
        print(f"    Sample query: {query}")
        
    print("✅ Translation loading test passed\n")


def test_language_detection():
    """Test automatic language detection."""
    print("Testing language detection...")
    
    # Save original environment
    original_lang = os.environ.get('LANG', '')
    original_lc_all = os.environ.get('LC_ALL', '')
    original_azure_lang = os.environ.get('AZURE_AI_LANGUAGE', '')
    
    try:
        # Test AZURE_AI_LANGUAGE priority
        os.environ['AZURE_AI_LANGUAGE'] = 'zh-TW'
        os.environ['LC_ALL'] = 'es_ES.UTF-8'
        os.environ['LANG'] = 'en_US.UTF-8'
        
        detected = detect_user_language()
        print(f"  With AZURE_AI_LANGUAGE=zh-TW: {detected}")
        assert detected == 'zh-TW', f"Expected zh-TW, got {detected}"
        
        # Test LC_ALL fallback
        del os.environ['AZURE_AI_LANGUAGE']
        detected = detect_user_language()
        print(f"  With LC_ALL=es_ES.UTF-8: {detected}")
        assert detected == 'es-ES', f"Expected es-ES, got {detected}"
        
        # Test LANG fallback
        del os.environ['LC_ALL']
        detected = detect_user_language()
        print(f"  With LANG=en_US.UTF-8: {detected}")
        assert detected == 'en-US', f"Expected en-US, got {detected}"
        
        # Test default fallback
        del os.environ['LANG']
        detected = detect_user_language()
        print(f"  With no language env vars: {detected}")
        assert detected == 'en-US', f"Expected en-US, got {detected}"
        
    finally:
        # Restore original environment
        for key, value in [('LANG', original_lang), 
                          ('LC_ALL', original_lc_all), 
                          ('AZURE_AI_LANGUAGE', original_azure_lang)]:
            if value:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]
    
    print("✅ Language detection test passed\n")


def test_translation_formatting():
    """Test translation string formatting."""
    print("Testing translation formatting...")
    
    translator = TranslationManager("en-US")
    
    # Test message with formatting
    message = translator.get_message_translation("agent_created", agent_id="test-agent-123")
    print(f"  Formatted message: {message}")
    assert "test-agent-123" in message, "Agent ID not found in formatted message"
    
    # Test message without formatting
    simple_message = translator.get_message_translation("searching")
    print(f"  Simple message: {simple_message}")
    assert simple_message != "azure_ai_search.messages.searching", "Translation not found"
    
    # Test fallback for missing key
    missing = translator.get_text("nonexistent.key.path")
    print(f"  Missing key fallback: {missing}")
    assert missing == "nonexistent.key.path", "Fallback not working correctly"
    
    print("✅ Translation formatting test passed\n")


def test_all_languages_consistency():
    """Test that all languages have consistent keys."""
    print("Testing language consistency...")
    
    available_languages = get_available_languages()
    if len(available_languages) < 2:
        print("  Skipping consistency test - need at least 2 languages")
        return
    
    # Test key consistency across languages
    test_keys = [
        "azure_ai_search.messages.agent_created",
        "azure_ai_search.queries.temperature_rating", 
        "azure_ai_search.instructions.agent_instructions",
        "azure_ai_search.errors.connection_failed"
    ]
    
    for lang in available_languages:
        if lang == "en-US":
            continue
            
        print(f"  Checking {lang} consistency...")
        translator = TranslationManager(lang)
        
        for key in test_keys:
            translation = translator.get_text(key)
            # Translation should exist and not be the key itself
            assert translation != key, f"Missing translation for {key} in {lang}"
            print(f"    {key}: ✅")
    
    print("✅ Language consistency test passed\n")


def run_all_tests():
    """Run all tests."""
    print("=== Azure AI Search Translation Tests ===\n")
    
    try:
        test_translation_loading()
        test_language_detection()
        test_translation_formatting()
        test_all_languages_consistency()
        
        print("🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)