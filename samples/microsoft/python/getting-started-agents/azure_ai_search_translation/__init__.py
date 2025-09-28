# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Azure AI Search with Translation Support

This package provides translation-enhanced Azure AI Search agent functionality,
enabling multi-language support for search interactions.
"""

from .translation_utils import (
    TranslationManager,
    get_available_languages,
    detect_user_language
)

__version__ = "1.0.0"
__all__ = [
    "TranslationManager",
    "get_available_languages", 
    "detect_user_language"
]