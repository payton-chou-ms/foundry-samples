#!/usr/bin/env python3
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Simple test script for Azure AI Search Agent components
Azure AI 搜索代理元件的簡單測試腳本

This script tests the basic functionality without Chainlit UI.
此腳本測試基本功能而不使用 Chainlit UI。
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import from the main project
sys.path.append(str(Path(__file__).parent.parent))

try:
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient
    from azure.ai.agents.models import AzureAISearchQueryType, AzureAISearchTool, MessageRole
    print("✅ Azure imports successful")
except ImportError as e:
    print(f"❌ Azure import failed: {e}")
    sys.exit(1)


def test_environment_setup():
    """Test environment variables and Azure connectivity.
    測試環境變數和 Azure 連接性。
    """
    print("🔍 Testing environment setup...")
    
    # Load environment variables
    load_dotenv()
    
    required_vars = [
        "PROJECT_ENDPOINT",
        "MODEL_DEPLOYMENT_NAME",
        "AZURE_AI_CONNECTION_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if not value or value.startswith("your-"):
            missing_vars.append(var)
        else:
            print(f"  ✅ {var}: {value[:30]}...")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please set up your .env file properly.")
        return False
    
    return True


def test_azure_client():
    """Test Azure AI Project client initialization.
    測試 Azure AI Project 客戶端初始化。
    """
    print("\n🔍 Testing Azure client initialization...")
    
    try:
        project_endpoint = os.environ["PROJECT_ENDPOINT"]
        
        client = AIProjectClient(
            endpoint=project_endpoint,
            credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
            api_version="latest",
        )
        
        print("  ✅ Azure AI Project client created successfully")
        return client
        
    except Exception as e:
        print(f"  ❌ Azure client initialization failed: {e}")
        return None


def test_search_tool():
    """Test Azure AI Search tool setup.
    測試 Azure AI Search 工具設定。
    """
    print("\n🔍 Testing Azure AI Search tool...")
    
    try:
        azure_ai_connection_id = os.environ["AZURE_AI_CONNECTION_ID"]
        search_index = os.environ.get("AZURE_SEARCH_INDEX", "vector-search-quickstart")
        
        ai_search = AzureAISearchTool(
            index_connection_id=azure_ai_connection_id,
            index_name=search_index,
            query_type=AzureAISearchQueryType.SIMPLE,
            top_k=3,
            filter="",
        )
        
        print("  ✅ Azure AI Search tool created successfully")
        print(f"     - Index: {search_index}")
        print(f"     - Connection ID: {azure_ai_connection_id[:20]}...")
        return ai_search
        
    except Exception as e:
        print(f"  ❌ Search tool creation failed: {e}")
        return None


def test_agent_creation(client, search_tool):
    """Test AI agent creation with search tools.
    測試使用搜索工具建立 AI 代理。
    """
    print("\n🔍 Testing AI agent creation...")
    
    try:
        model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]
        
        agent = client.agents.create_agent(
            model=model_deployment_name,
            name="test-search-agent",
            instructions="You are a helpful search assistant for testing purposes.",
            tools=search_tool.definitions,
            tool_resources=search_tool.resources,
        )
        
        print("  ✅ AI agent created successfully")
        print(f"     - Agent ID: {agent.id}")
        print(f"     - Model: {model_deployment_name}")
        return agent
        
    except Exception as e:
        print(f"  ❌ Agent creation failed: {e}")
        return None


def test_basic_conversation(client, agent):
    """Test basic conversation with the agent.
    測試與代理的基本對話。
    """
    print("\n🔍 Testing basic conversation...")
    
    try:
        # Create thread
        thread = client.agents.threads.create()
        print(f"  ✅ Thread created: {thread.id}")
        
        # Send message
        test_message = "Hello! Can you help me find hotels?"
        client.agents.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=test_message
        )
        print(f"  ✅ Message sent: {test_message}")
        
        # Create and process run (with timeout)
        print("  🤖 Processing agent response...")
        run = client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        print(f"  📊 Run status: {run.status}")
        
        if run.status == "completed":
            print("  ✅ Agent responded successfully")
            return True
        elif run.status == "failed":
            print(f"  ❌ Agent run failed: {getattr(run, 'last_error', 'Unknown error')}")
            return False
        else:
            print(f"  ⚠️  Unexpected run status: {run.status}")
            return False
            
    except Exception as e:
        print(f"  ❌ Conversation test failed: {e}")
        return False


def cleanup_resources(client, agent):
    """Clean up test resources.
    清理測試資源。
    """
    print("\n🧹 Cleaning up resources...")
    
    try:
        if agent:
            client.agents.delete_agent(agent.id)
            print("  ✅ Test agent deleted")
    except Exception as e:
        print(f"  ⚠️  Cleanup warning: {e}")


def main():
    """Main test function.
    主測試函數。
    """
    print("🧪 Azure AI Search Agent Component Tests")
    print("🧪 Azure AI 搜索代理元件測試")
    print("=" * 60)
    
    # Test 1: Environment setup
    if not test_environment_setup():
        print("\n❌ Environment setup failed. Please check your .env file.")
        sys.exit(1)
    
    # Test 2: Azure client
    client = test_azure_client()
    if not client:
        print("\n❌ Azure client test failed. Please check your credentials.")
        sys.exit(1)
    
    # Test 3: Search tool
    search_tool = test_search_tool()
    if not search_tool:
        print("\n❌ Search tool test failed. Please check your search configuration.")
        sys.exit(1)
    
    # Test 4: Agent creation
    agent = test_agent_creation(client, search_tool)
    if not agent:
        print("\n❌ Agent creation test failed.")
        sys.exit(1)
    
    # Test 5: Basic conversation
    conversation_success = test_basic_conversation(client, agent)
    
    # Cleanup
    cleanup_resources(client, agent)
    
    # Results
    print("\n" + "=" * 60)
    if conversation_success:
        print("🎉 All tests passed! The Chainlit app should work properly.")
        print("🎉 所有測試通過！Chainlit 應用程式應該可以正常運作。")
        print("\n💡 Next step: Run 'chainlit run app.py -w' to start the UI")
        print("💡 下一步：執行 'chainlit run app.py -w' 來啟動 UI")
    else:
        print("⚠️  Some tests failed. Please check the configuration before using Chainlit.")
        print("⚠️  某些測試失敗。請在使用 Chainlit 前檢查配置。")


if __name__ == "__main__":
    main()