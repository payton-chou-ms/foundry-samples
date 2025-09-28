# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
FILE: azure_ai_search_with_translation.py

DESCRIPTION:
    This sample demonstrates how to use agent operations with the Azure AI Search tool from
    the Azure Agents service using a synchronous client, with enhanced translation support
    for multi-language interactions.

USAGE:
    python azure_ai_search_with_translation.py

    Before running the sample:

    pip install azure.ai.projects azure-identity

    Set these environment variables with your own values:
    PROJECT_ENDPOINT - the Azure AI Project endpoint, as found in your AI Studio Project.
    MODEL_DEPLOYMENT_NAME - the deployment name of the AI model.
    AZURE_AI_CONNECTION_ID - the connection ID for the Azure AI Search tool.
    AZURE_AI_LANGUAGE - (Optional) preferred language code (e.g., 'en-US', 'zh-TW', 'es-ES')
"""

# Import necessary libraries and modules
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import AzureAISearchQueryType, AzureAISearchTool, ListSortOrder, MessageRole
from translation_utils import TranslationManager, detect_user_language, get_available_languages


def main():
    """Main function to demonstrate Azure AI Search with translation support."""
    
    # Detect or get preferred language
    preferred_language = os.environ.get('AZURE_AI_LANGUAGE', detect_user_language())
    print(f"Available languages: {', '.join(get_available_languages())}")
    print(f"Using language: {preferred_language}")
    
    # Initialize translation manager
    translator = TranslationManager(preferred_language)
    
    # Retrieve endpoint and model deployment name from environment variables
    project_endpoint = os.environ["PROJECT_ENDPOINT"]
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

    # Initialize the AIProjectClient with the endpoint and credentials
    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
        api_version="latest",
    )

    with project_client:
        print(translator.get_message_translation("searching"))
        
        # Initialize the Azure AI Search tool with the required parameters
        ai_search = AzureAISearchTool(
            index_connection_id=os.environ["AZURE_AI_CONNECTION_ID"],
            index_name="sample_index",
            query_type=AzureAISearchQueryType.SIMPLE,
            top_k=3,
            filter="",
        )

        # Create an agent with translated instructions
        agent_instructions = translator.get_instruction_translation("agent_instructions")
        agent = project_client.agents.create_agent(
            model=model_deployment_name,
            name="multilingual-search-agent",
            instructions=agent_instructions,
            tools=ai_search.definitions,
            tool_resources=ai_search.resources,
        )
        print(translator.get_message_translation("agent_created", agent_id=agent.id))

        # Create a thread for communication with the agent
        thread = project_client.agents.threads.create()
        print(translator.get_message_translation("thread_created", thread_id=thread.id))

        # Demonstrate with translated queries
        queries = [
            translator.get_query_translation("temperature_rating"),
            translator.get_query_translation("product_information"),
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\n--- Query {i} ---")
            print(f"Query: {query}")
            
            # Send a message to the thread
            message = project_client.agents.messages.create(
                thread_id=thread.id,
                role=MessageRole.USER,
                content=query,
            )
            print(translator.get_message_translation("message_created", message_id=message['id']))

            print(translator.get_message_translation("processing_results"))
            
            # Create and process an agent run in the thread using the tools
            run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
            print(translator.get_message_translation("run_finished", status=run.status))

            if run.status == "failed":
                error_message = translator.get_error_translation("search_failed")
                print(f"{error_message}: {run.last_error}")
            else:
                print(translator.get_message_translation("search_completed"))

        # Fetch and display all messages from the thread
        print(f"\n--- {translator.get_text('azure_ai_search.messages.processing_results')} ---")
        messages = project_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        
        for message in messages.data:
            role_display = "User" if message.role == MessageRole.USER else "Assistant"
            print(f"{role_display}: {message.content}")

        # Clean up resources
        project_client.agents.delete_agent(agent.id)
        print(translator.get_message_translation("agent_deleted"))
        
        # Display final summary in user's language
        print("\n--- Summary ---")
        print(f"Language used: {preferred_language}")
        print(f"Processed {len(queries)} queries successfully")


def demonstrate_language_switching():
    """Demonstrate switching between different languages."""
    print("\n=== Language Switching Demo ===")
    
    available_langs = get_available_languages()
    
    for lang in available_langs:
        print(f"\n--- {lang} ---")
        translator = TranslationManager(lang)
        
        # Show sample translations
        print(translator.get_message_translation("searching"))
        print(translator.get_query_translation("temperature_rating"))
        print(translator.get_instruction_translation("agent_instructions"))


if __name__ == "__main__":
    try:
        main()
        
        # Optionally demonstrate language switching
        if os.environ.get("DEMO_LANGUAGE_SWITCHING", "").lower() == "true":
            demonstrate_language_switching()
            
    except KeyError as e:
        print(f"Missing environment variable: {e}")
        print("Please ensure the following environment variables are set:")
        print("- PROJECT_ENDPOINT")
        print("- MODEL_DEPLOYMENT_NAME")
        print("- AZURE_AI_CONNECTION_ID")
        print("- AZURE_AI_LANGUAGE (optional)")
    except Exception as e:
        print(f"Error: {e}")