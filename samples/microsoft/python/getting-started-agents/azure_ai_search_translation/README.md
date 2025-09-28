# Azure AI Search with Translation Support

This sample demonstrates how to use Azure AI Search agents with multi-language translation support, enabling users to interact with the search system in their preferred language.

## Features

- **Multi-language Support**: Supports English (en-US), Traditional Chinese (zh-TW), and Spanish (es-ES)
- **Automatic Language Detection**: Automatically detects user's preferred language from environment variables
- **Translated Queries**: Pre-translated common search queries in multiple languages
- **Localized Messages**: All agent messages, instructions, and error messages are localized
- **Extensible Translation System**: Easy to add new languages by creating JSON translation files

## Setup Instructions

### Prerequisites

1. **Azure AI Studio Project**: Set up an Azure AI Studio project with Azure AI Search tool configured
2. **Python Environment**: Python 3.8 or later
3. **Dependencies**: Install required packages

```bash
pip install -r requirements.txt
```

### Environment Variables

Set the following environment variables:

```bash
# Required
export PROJECT_ENDPOINT="https://your-project.cognitiveservices.azure.com/"
export MODEL_DEPLOYMENT_NAME="your-model-deployment-name"
export AZURE_AI_CONNECTION_ID="your-azure-ai-search-connection-id"

# Optional - Language preference
export AZURE_AI_LANGUAGE="en-US"  # Options: en-US, zh-TW, es-ES

# Optional - Enable language switching demo
export DEMO_LANGUAGE_SWITCHING="true"
```

## Usage

### Basic Usage

Run the sample with automatic language detection:

```bash
python azure_ai_search_with_translation.py
```

### Specify Language

Run with a specific language:

```bash
AZURE_AI_LANGUAGE="zh-TW" python azure_ai_search_with_translation.py
```

### Language Switching Demo

Enable the language switching demonstration:

```bash
DEMO_LANGUAGE_SWITCHING="true" python azure_ai_search_with_translation.py
```

## Translation System

### Translation Files

Translation files are located in the `translations/` directory:

- `en-US.json` - English (United States)
- `zh-TW.json` - Traditional Chinese (Taiwan)  
- `es-ES.json` - Spanish (Spain)

### Translation Structure

Each translation file follows this JSON structure:

```json
{
    "azure_ai_search": {
        "messages": {
            "agent_created": "Created agent, ID: {agent_id}",
            "thread_created": "Created thread, ID: {thread_id}",
            // ... more messages
        },
        "queries": {
            "temperature_rating": "What is the temperature rating of the cozynights sleeping bag?",
            // ... more queries
        },
        "instructions": {
            "agent_instructions": "You are a helpful agent...",
            // ... more instructions
        },
        "errors": {
            "connection_failed": "Failed to connect to Azure AI Search service",
            // ... more errors
        }
    }
}
```

### Adding New Languages

To add support for a new language:

1. Create a new translation file: `translations/{language-code}.json`
2. Copy the structure from `en-US.json`
3. Translate all text values while keeping the keys the same
4. The new language will be automatically detected and available

Example for French (fr-FR):

```json
{
    "azure_ai_search": {
        "messages": {
            "agent_created": "Agent créé, ID: {agent_id}",
            "thread_created": "Thread créé, ID: {thread_id}",
            // ... etc.
        }
    }
}
```

## Translation API Reference

### TranslationManager Class

The `TranslationManager` class handles all translation operations:

```python
from translation_utils import TranslationManager

# Initialize with language
translator = TranslationManager("zh-TW")

# Get translated text
text = translator.get_text("azure_ai_search.messages.agent_created", agent_id="12345")

# Shortcut methods
query = translator.get_query_translation("temperature_rating")
message = translator.get_message_translation("searching")
instruction = translator.get_instruction_translation("agent_instructions")
error = translator.get_error_translation("connection_failed")
```

### Utility Functions

```python
from translation_utils import get_available_languages, detect_user_language

# Get list of supported languages
languages = get_available_languages()  # Returns ['en-US', 'zh-TW', 'es-ES']

# Auto-detect user's language
user_lang = detect_user_language()  # Returns language based on environment
```

## Language Detection Priority

The system detects user language in the following priority order:

1. `AZURE_AI_LANGUAGE` environment variable
2. `LC_ALL` environment variable  
3. `LANG` environment variable
4. Fallback to `en-US`

## Sample Queries by Language

### English (en-US)
- "What is the temperature rating of the cozynights sleeping bag?"
- "Can you provide information about this product?"
- "Search for products matching my criteria"

### Traditional Chinese (zh-TW)
- "cozynights睡袋的溫度等級是多少？"
- "您能提供這個產品的信息嗎？"
- "搜索符合我條件的產品"

### Spanish (es-ES)
- "¿Cuál es la clasificación de temperatura del saco de dormir cozynights?"
- "¿Puede proporcionar información sobre este producto?"
- "Buscar productos que coincidan con mis criterios"

## Error Handling

The translation system includes comprehensive error handling:

- **Missing Translation**: Falls back to the key path if translation is not found
- **Missing Language File**: Falls back to English (en-US)
- **Format Errors**: Safely handles missing format parameters

## Best Practices

1. **Consistent Keys**: Always use consistent translation keys across all language files
2. **Parameter Formatting**: Use named parameters (e.g., `{agent_id}`) for better translation flexibility
3. **Cultural Adaptation**: Consider cultural differences, not just literal translations
4. **Testing**: Test with different languages to ensure proper text rendering
5. **Fallbacks**: Always provide fallback behavior for missing translations

## Integration with Existing Code

The translation system is designed to integrate seamlessly with existing Azure AI Search samples:

```python
# Before (original code)
print(f"Created agent, ID: {agent.id}")

# After (with translation)
print(translator.get_message_translation("agent_created", agent_id=agent.id))
```

## Troubleshooting

### Common Issues

1. **Missing Translation File**: Ensure translation files are in the `translations/` directory
2. **Encoding Issues**: Make sure all files use UTF-8 encoding
3. **Format Errors**: Check that all placeholders in translations match the code
4. **Language Not Detected**: Verify environment variables are set correctly

### Debug Mode

Set environment variable for verbose output:

```bash
export AZURE_AI_DEBUG="true"
```

## Performance Considerations

- Translation files are loaded once at initialization
- Translations are cached in memory for fast access
- Minimal overhead for production usage
- Language detection happens only once per session

## Contributing

To contribute new translations or improvements:

1. Add new language files following the established structure
2. Test translations with native speakers
3. Ensure all placeholders and formatting work correctly
4. Update this documentation with the new language information