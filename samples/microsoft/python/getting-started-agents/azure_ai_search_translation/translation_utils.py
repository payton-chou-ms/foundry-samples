# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Translation utilities for Azure AI Search agent samples.

This module provides translation capabilities for the Azure AI Search agent,
enabling multi-language support for user messages and agent responses.
"""

import json
import os
# Remove unused imports - typing not needed for current functionality
from pathlib import Path


class TranslationManager:
    """Manages translations for Azure AI Search agent."""
    
    def __init__(self, language: str = "en-US"):
        """
        Initialize the translation manager.
        
        Args:
            language (str): Language code (e.g., 'en-US', 'zh-TW', 'es-ES')
        """
        self.language = language
        self.translations = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load translations from JSON file."""
        translations_dir = Path(__file__).parent / "translations"
        translation_file = translations_dir / f"{self.language}.json"
        
        if translation_file.exists():
            with open(translation_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        else:
            # Fallback to English if language not found
            fallback_file = translations_dir / "en-US.json"
            if fallback_file.exists():
                with open(fallback_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            else:
                print(f"Warning: No translations found for {self.language}")
                self.translations = {}
    
    def get_text(self, key_path: str, **kwargs) -> str:
        """
        Get translated text by key path.
        
        Args:
            key_path (str): Dot-separated path to the translation key 
                           (e.g., 'azure_ai_search.messages.agent_created')
            **kwargs: Format arguments for string formatting
            
        Returns:
            str: Translated and formatted text
        """
        keys = key_path.split('.')
        current = self.translations
        
        try:
            for key in keys:
                current = current[key]
            
            if isinstance(current, str) and kwargs:
                return current.format(**kwargs)
            return str(current)
        except (KeyError, TypeError):
            # Return the key path if translation not found
            return key_path
    
    def get_query_translation(self, query_key: str) -> str:
        """Get translated query text."""
        return self.get_text(f"azure_ai_search.queries.{query_key}")
    
    def get_message_translation(self, message_key: str, **kwargs) -> str:
        """Get translated message text."""
        return self.get_text(f"azure_ai_search.messages.{message_key}", **kwargs)
    
    def get_instruction_translation(self, instruction_key: str) -> str:
        """Get translated instruction text."""
        return self.get_text(f"azure_ai_search.instructions.{instruction_key}")
    
    def get_error_translation(self, error_key: str) -> str:
        """Get translated error text."""
        return self.get_text(f"azure_ai_search.errors.{error_key}")


def get_available_languages() -> list:
    """
    Get list of available languages.
    
    Returns:
        list: List of available language codes
    """
    translations_dir = Path(__file__).parent / "translations"
    if not translations_dir.exists():
        return ["en-US"]
    
    languages = []
    for file in translations_dir.glob("*.json"):
        languages.append(file.stem)
    
    return sorted(languages)


def detect_user_language() -> str:
    """
    Detect user's preferred language from environment variables.
    
    Returns:
        str: Language code, defaults to 'en-US'
    """
    # Check environment variables for language preference
    lang_env = os.environ.get('LANG', '')
    lc_all = os.environ.get('LC_ALL', '')
    azure_ai_language = os.environ.get('AZURE_AI_LANGUAGE', '')
    
    # Priority: AZURE_AI_LANGUAGE > LC_ALL > LANG
    for lang_var in [azure_ai_language, lc_all, lang_env]:
        if lang_var:
            # Extract language code (e.g., 'zh_TW.UTF-8' -> 'zh-TW')
            lang_code = lang_var.split('.')[0].replace('_', '-')
            available_langs = get_available_languages()
            
            if lang_code in available_langs:
                return lang_code
            
            # Try partial match (e.g., 'zh' matches 'zh-TW')
            for available_lang in available_langs:
                if available_lang.startswith(lang_code.split('-')[0]):
                    return available_lang
    
    return "en-US"