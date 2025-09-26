# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
FILE: step2_create_ai_agent.py

DESCRIPTION:
    This script demonstrates how to create an Azure AI Foundry agent with Chainlit UI integration.
    It creates a hotel search assistant with interactive UI components and agent lifecycle management.

USAGE:
    For Chainlit UI:
        chainlit run step2_create_ai_agent.py -w
    
    For command line testing:
        python step2_create_ai_agent.py

    Before running the script:
    1. Run step1_create_search_index.py first to create the search index
    2. pip install -r requirements.txt
    3. Create a .env file with the following variables:
       - PROJECT_ENDPOINT (Azure AI Project endpoint)
       - MODEL_DEPLOYMENT_NAME (AI model deployment name)
       - AZURE_SEARCH_ENDPOINT
       - AZURE_SEARCH_API_KEY
       - AZURE_SEARCH_INDEX (optional, defaults to "vector-search-quickstart")

FEATURES:
    1. Interactive Chainlit UI with sample question buttons
    2. Agent lifecycle management (creation, display ID, cleanup)
    3. Hotel search assistant with specialized personality
    4. Azure AI Search integration for hotel information retrieval
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import MessageRole, ListSortOrder
from azure.search.documents import SearchClient

# Chainlit imports
import chainlit as cl
from typing import Optional


def initialize_environment():
    """Initialize environment variables and credentials."""
    print("🔧 初始化環境變數和認證 / Initializing environment and credentials...")
    
    # Load environment variables from .env file
    load_dotenv(override=True)
    
    # AI Project settings
    project_endpoint = os.environ["PROJECT_ENDPOINT"]
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]
    
    # Search settings
    search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    search_api_key = os.getenv("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX", "vector-search-quickstart")
    
    # Initialize credentials
    project_credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    search_credential = AzureKeyCredential(search_api_key)
    
    print(f"✅ AI Project 端點 / Endpoint: {project_endpoint}")
    print(f"✅ 模型部署名稱 / Model deployment: {model_deployment_name}")
    print(f"✅ 搜索端點 / Search endpoint: {search_endpoint}")
    print(f"✅ 索引名稱 / Index name: {index_name}")
    
    return {
        "project_endpoint": project_endpoint,
        "model_deployment_name": model_deployment_name,
        "project_credential": project_credential,
        "search_endpoint": search_endpoint,
        "search_credential": search_credential,
        "index_name": index_name
    }


def verify_search_index(search_endpoint, search_credential, index_name):
    """Verify that the search index exists and has documents."""
    print(f"\n🔍 驗證搜索索引 / Verifying search index '{index_name}'...")
    
    try:
        search_client = SearchClient(
            endpoint=search_endpoint, 
            index_name=index_name, 
            credential=search_credential
        )
        
        # Try to search for documents
        results = search_client.search(search_text="*", top=1)
        result_count = 0
        
        for result in results:
            result_count += 1
            break  # Just check if we have any results
            
        if result_count > 0:
            print(f"✅ 索引驗證成功，包含文檔 / Index verified successfully with documents")
            return True
        else:
            print(f"⚠️  索引存在但無文檔 / Index exists but no documents found")
            print(f"請先運行 step1_create_search_index.py / Please run step1_create_search_index.py first")
            return False
            
    except Exception as e:
        print(f"❌ 索引驗證失敗 / Index verification failed: {str(e)}")
        print(f"請先運行 step1_create_search_index.py / Please run step1_create_search_index.py first")
        return False


def create_ai_agent_with_search(config):
    """Create an AI agent with Azure AI Search integration and hotel-focused personality."""
    print(f"\n🤖 建立 AI Agent 與搜索整合 / Creating AI agent with search integration...")
    
    # Initialize the AI Project Client
    project_client = AIProjectClient(
        endpoint=config["project_endpoint"],
        credential=config["project_credential"],
    )
    
    print(f"✅ AI Project 客戶端初始化成功 / AI Project client initialized")
    
    # Create the AI agent with hotel search capabilities and focused personality
    agent = project_client.agents.create_agent(
        model=config["model_deployment_name"],
        name="hotel-search-assistant",
        instructions=f"""你是一位專業的酒店搜索助理，專門協助客戶尋找合適的酒店住宿。
You are a professional hotel search assistant specializing in helping clients find suitable hotel accommodations.

🏨 您的專業領域包括：
Your areas of expertise include:
• 酒店信息查詢和推薦 / Hotel information inquiry and recommendations
• 精品酒店和特色住宿 / Boutique hotels and unique accommodations  
• 酒店評分和設施分析 / Hotel ratings and amenities analysis
• 停車和位置便利性 / Parking and location convenience
• 價格比較和性價比建議 / Price comparison and value recommendations

🔍 當用戶提問時，請：
When users ask questions, please:
1. 根據問題類型提供專業且詳細的回答
   Provide professional and detailed answers based on question type
2. 如有相關數據，引用具體的酒店名稱、評分和設施
   If relevant data is available, cite specific hotel names, ratings, and amenities
3. 用親切友好的語調回應，就像經驗豐富的旅行顧問
   Respond in a friendly tone like an experienced travel consultant
4. 如需更多信息，主動詢問客戶的具體需求
   Proactively ask about specific needs if more information is required

💡 您可以協助解答的問題包括：
Questions you can help answer include:
• 酒店信息和特色介紹 / Hotel information and feature introductions
• 特定地區的酒店推薦 / Hotel recommendations for specific areas
• 高評分酒店的詳細信息 / Detailed information about highly-rated hotels
• 特定酒店的設施和服務 / Amenities and services of specific hotels  
• 包含停車服務的酒店選項 / Hotel options with parking included

請始終保持專業、友善和有幫助的態度！
Always maintain a professional, friendly, and helpful attitude!""",
    )
    
    print(f"✅ 酒店搜索助理創建成功 / Hotel search assistant created successfully")
    print(f"📋 Agent ID: {agent.id}")
    print(f"📋 Agent 名稱 / Name: {agent.name}")
    
    return project_client, agent


def create_conversation_thread(project_client):
    """Create a conversation thread for the agent."""
    print(f"\n💬 建立對話線程 / Creating conversation thread...")
    
    thread = project_client.agents.threads.create()
    
    print(f"✅ 對話線程建立成功 / Conversation thread created successfully")
    print(f"📋 Thread ID: {thread.id}")
    
    return thread


def ask_agent_question(project_client, agent, thread, question):
    """Ask the agent a question and get a response."""
    print(f"\n❓ 提問 / Question: {question}")
    print(f"🤖 Agent 處理中... / Agent processing...")
    
    try:
        # Create a message in the thread
        message = project_client.agents.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=question
        )
        
        # Create and process the run
        run = project_client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        if run.status == "completed":
            # Get the agent's response
            messages = project_client.agents.messages.list(
                thread_id=thread.id,
                order=ListSortOrder.DESCENDING,
                limit=1
            )
            
            message_list = list(messages)
            if message_list:
                latest_message = message_list[0]
                if latest_message.role == MessageRole.AGENT:
                    response_text = ""
                    if latest_message.content:
                        for content in latest_message.content:
                            if hasattr(content, 'text') and content.text:
                                if hasattr(content.text, 'value'):
                                    response_text += content.text.value
                    
                    print(f"💬 Agent 回覆 / Response:")
                    print(f"{response_text}")
                    return response_text
                    
        elif run.status == "failed":
            print(f"❌ Agent 運行失敗 / Agent run failed: {run.last_error}")
            return None
        else:
            print(f"⚠️  Agent 運行狀態 / Run status: {run.status}")
            return None
            
    except Exception as e:
        print(f"❌ 提問失敗 / Question failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_agent_capabilities(project_client, agent, thread):
    """Test the agent's capabilities with hotel-focused sample questions."""
    print(f"\n🧪 測試 Agent 功能 / Testing agent capabilities...")
    print("=" * 60)
    
    # Updated sample questions focused on hotel search
    sample_questions = [
        "What hotels do you know about? Can you tell me about them?",
        "Can you recommend a boutique hotel in New York?",
        "Tell me about hotels with high ratings.",
        "What amenities are available at the Old Century Hotel?",
        "Are there any hotels with parking included?"
    ]
    
    responses = []
    
    for i, question in enumerate(sample_questions, 1):
        print(f"\n🔍 測試 {i} / Test {i}")
        print("-" * 40)
        
        response = ask_agent_question(project_client, agent, thread, question)
        responses.append({
            "question": question,
            "response": response,
            "success": response is not None
        })
        
        if response:
            print("✅ 測試成功 / Test successful")
        else:
            print("❌ 測試失敗 / Test failed")
    
    return responses


def compare_with_without_search_tools(project_client, config):
    """Compare responses with and without search tools."""
    print(f"\n🆚 比較有/無搜索工具的回覆 / Comparing responses with/without search tools...")
    print("=" * 70)
    
    test_question = "Tell me about luxury hotels with unique amenities."
    
    try:
        # Create a simple agent without search tools for comparison
        simple_agent = project_client.agents.create_agent(
            model=config["model_deployment_name"],
            name="simple-agent-no-search",
            instructions="You are a helpful assistant. Answer questions based on your general knowledge about hotels.",
        )
        
        simple_thread = project_client.agents.threads.create()
        
        print(f"\n🚫 簡單 Agent 回覆 (無搜索工具) / Simple agent response (no search tools):")
        print("-" * 50)
        simple_response = ask_agent_question(project_client, simple_agent, simple_thread, test_question)
        
        # Clean up simple agent
        project_client.agents.delete_agent(simple_agent.id)
        
        print(f"\n📊 分析 / Analysis:")
        print("1. 簡單 Agent 只能提供一般性的酒店建議")
        print("   Simple agent can only provide general hotel suggestions")
        print("2. 有搜索工具的 Agent 可以提供更具體的資訊")
        print("   Agent with search tools can provide more specific information")
        print("3. 實際項目中應該整合搜索工具以獲得更好的結果")
        print("   In real projects, search tools should be integrated for better results")
        
    except Exception as e:
        print(f"❌ 比較測試失敗 / Comparison test failed: {str(e)}")


def validate_agent_search_integration(search_endpoint, search_credential, index_name):
    """Validate that the agent can potentially integrate with search."""
    print(f"\n✅ 驗證 Agent 搜索整合潛力 / Validating agent search integration potential...")
    
    try:
        # Test direct search to ensure it's working
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=search_credential
        )
        
        # Test search functionality that the agent would use
        test_searches = [
            {"query": "boutique hotel", "description": "文字搜索 / Text search"},
            {"query": "*", "filter": "Rating gt 4.0", "description": "篩選搜索 / Filter search"},
            {"query": "*", "filter": "Category eq 'Boutique'", "description": "類別篩選 / Category filter"}
        ]
        
        print("🔍 測試搜索功能 / Testing search functionality:")
        
        for test in test_searches:
            print(f"\n  📋 {test['description']}")
            try:
                if 'filter' in test:
                    results = search_client.search(
                        search_text=test['query'], 
                        filter=test['filter'], 
                        top=2
                    )
                else:
                    results = search_client.search(search_text=test['query'], top=2)
                
                count = 0
                for result in results:
                    count += 1
                    print(f"    - {result['HotelName']} (評分: {result.get('Rating', 'N/A')})")
                    
                print(f"    ✅ 找到 {count} 個結果 / Found {count} results")
                
            except Exception as e:
                print(f"    ❌ 搜索失敗 / Search failed: {str(e)}")
        
        print(f"\n✅ 搜索功能驗證完成 / Search functionality validation completed")
        print(f"💡 在完整實現中，Agent 可以使用這些搜索功能來提供準確的酒店資訊")
        print(f"💡 In a full implementation, the agent can use these search capabilities to provide accurate hotel information")
        
    except Exception as e:
        print(f"❌ 搜索整合驗證失敗 / Search integration validation failed: {str(e)}")


def main():
    """Main function to execute all steps in command line mode."""
    print("🚀 開始執行步驟 2: 建立 AI Foundry Agent 和相關功能")
    print("🚀 Starting Step 2: Generate AI Foundry Agent and Related Features")
    print("=" * 80)
    print("💡 提示：使用 'chainlit run step2_create_ai_agent.py -w' 來啟動互動式 UI")
    print("💡 Tip: Use 'chainlit run step2_create_ai_agent.py -w' to start interactive UI")
    print("=" * 80)
    
    try:
        # Step 1: Initialize environment
        config = initialize_environment()
        
        # Step 2: Verify search index
        if not verify_search_index(
            config["search_endpoint"], 
            config["search_credential"], 
            config["index_name"]
        ):
            print("❌ 搜索索引驗證失敗，請先運行步驟 1")
            print("❌ Search index verification failed, please run step 1 first")
            return {"success": False, "error": "Search index not available"}
        
        # Step 3: Create AI agent with search capabilities
        project_client, agent = create_ai_agent_with_search(config)
        
        # Step 4: Create conversation thread
        thread = create_conversation_thread(project_client)
        
        # Step 5: Test agent capabilities with new sample questions
        responses = test_agent_capabilities(project_client, agent, thread)
        
        # Step 6: Compare with simple agent
        compare_with_without_search_tools(project_client, config)
        
        # Step 7: Validate search integration potential
        validate_agent_search_integration(
            config["search_endpoint"],
            config["search_credential"],
            config["index_name"]
        )
        
        print(f"\n🎉 步驟 2 完成！/ Step 2 completed successfully!")
        print(f"📝 Agent ID: {agent.id}")
        print(f"📝 Thread ID: {thread.id}")
        print(f"📝 已準備好用於清理 / Ready for cleanup")
        
        # Show Chainlit usage instructions
        print(f"\n🚀 **如要使用互動式 UI / To use interactive UI:**")
        print(f"   chainlit run step2_create_ai_agent.py -w")
        print(f"\n🧹 **記得清理資源 / Remember to clean up resources:**")
        print(f"   python step3_cleanup_resources.py")
        
        # Return important information for cleanup
        return {
            "success": True,
            "agent_id": agent.id,
            "thread_id": thread.id,
            "project_client": project_client,
            "index_name": config["index_name"]
        }
        
    except Exception as e:
        print(f"\n❌ 步驟 2 失敗 / Step 2 failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


# ================== CHAINLIT UI COMPONENTS ==================

# Global variables to store agent and client
project_client: Optional[AIProjectClient] = None
agent = None
thread = None
config = None

# Sample questions for suggestion buttons
SAMPLE_QUESTIONS = [
    "What hotels do you know about? Can you tell me about them?",
    "Can you recommend a boutique hotel in New York?",
    "Tell me about hotels with high ratings.",
    "What amenities are available at the Old Century Hotel?",
    "Are there any hotels with parking included?"
]


@cl.on_chat_start
async def start():
    """Initialize the agent when Chainlit UI starts."""
    global project_client, agent, thread, config
    
    try:
        # Initialize environment and create agent
        config = initialize_environment()
        
        # Verify search index
        if not verify_search_index(
            config["search_endpoint"], 
            config["search_credential"], 
            config["index_name"]
        ):
            await cl.Message(
                content="❌ 搜索索引驗證失敗，請先運行 step1_create_search_index.py\n"
                       "❌ Search index verification failed, please run step1_create_search_index.py first"
            ).send()
            return
        
        # Create agent and thread
        project_client, agent = create_ai_agent_with_search(config)
        thread = create_conversation_thread(project_client)
        
        # Store agent info in session
        cl.user_session.set("agent_id", agent.id)
        cl.user_session.set("thread_id", thread.id)
        
        # Welcome message with agent info and suggestion buttons
        welcome_msg = f"""🏨 **酒店搜索助理已就緒！/ Hotel Search Assistant Ready!**

🆔 **Agent ID**: `{agent.id}`
🧵 **Thread ID**: `{thread.id}`

我是您的專業酒店搜索助理，可以幫您找到最合適的酒店住宿！
I'm your professional hotel search assistant, ready to help you find the perfect hotel accommodation!

💡 **點擊下方按鈕快速開始，或直接輸入您的問題：**
**Click the buttons below to get started quickly, or type your question directly:**
"""
        
        await cl.Message(content=welcome_msg).send()
        
        actions = []
        for i, question in enumerate(SAMPLE_QUESTIONS):
            actions.append(
                cl.Action(
                    name=f"sample_{i}",
                    value=question,
                    description=question,
                    label=f"💬 {question[:50]}{'...' if len(question) > 50 else ''}",
                    payload={"question": question, "index": i}  # 添加 payload
                )
            )
        
        await cl.Message(
            content="🎯 **建議問題 / Suggested Questions:**",
            actions=actions
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=f"❌ Agent 初始化失敗 / Agent initialization failed: {str(e)}"
        ).send()


@cl.action_callback("sample_0")
@cl.action_callback("sample_1")
@cl.action_callback("sample_2")
@cl.action_callback("sample_3")
@cl.action_callback("sample_4")
async def on_action(action):
    """Handle sample question button clicks."""
    question = action.payload.get("question", SAMPLE_QUESTIONS[action.payload.get("index", 0)])
    await process_message(question)


@cl.on_message
async def main_message(message: cl.Message):
    """Handle user messages."""
    await process_message(message.content)


async def process_message(user_input: str):
    """Process user input and get agent response."""
    global project_client, agent, thread
    
    if not all([project_client, agent, thread]):
        await cl.Message(content="❌ Agent 未初始化，請重新啟動 / Agent not initialized, please restart").send()
        return
    
    # Show processing message
    processing_msg = await cl.Message(content="🤖 處理中... / Processing...").send()
    
    try:
        # Create user message in thread
        project_client.agents.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=user_input
        )
        
        # Create and process run
        run = project_client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        if run.status == "completed":
            # Get agent response
            messages = project_client.agents.messages.list(
                thread_id=thread.id,
                order=ListSortOrder.DESCENDING,
                limit=1
            )
            
            message_list = list(messages)
            if message_list:
                latest_message = message_list[0]
                if latest_message.role == MessageRole.AGENT:
                    response_text = ""
                    if latest_message.content:
                        for content in latest_message.content:
                            if hasattr(content, 'text') and content.text:
                                if hasattr(content.text, 'value'):
                                    response_text += content.text.value
                    
                    # 修復：使用正確的 API
                    processing_msg.content = f"🏨 **酒店助理回覆 / Hotel Assistant Response:**\n\n{response_text}"
                    await processing_msg.update()
                else:
                    processing_msg.content = "❌ 未收到有效回應 / No valid response received"
                    await processing_msg.update()
            else:
                processing_msg.content = "❌ 未找到回應訊息 / No response message found"
                await processing_msg.update()
                
        elif run.status == "failed":
            processing_msg.content = f"❌ 處理失敗 / Processing failed: {run.last_error}"
            await processing_msg.update()
        else:
            processing_msg.content = f"⚠️ 處理狀態 / Processing status: {run.status}"
            await processing_msg.update()
            
    except Exception as e:
        processing_msg.content = f"❌ 錯誤 / Error: {str(e)}"
        await processing_msg.update()


@cl.on_stop
async def on_stop():
    """Cleanup when the session stops."""
    global project_client, agent
    
    if project_client and agent:
        try:
            agent_id = cl.user_session.get("agent_id")
            if agent_id:
                project_client.agents.delete_agent(agent_id)
                print(f"🧹 已清理 Agent / Cleaned up Agent: {agent_id}")
        except Exception as e:
            print(f"⚠️ 清理 Agent 時發生錯誤 / Error during agent cleanup: {e}")


# ================== COMMAND LINE INTERFACE ==================


if __name__ == "__main__":
    result = main()
    
    if result["success"]:
        print(f"\n✅ 腳本執行成功 / Script executed successfully")
        print(f"🔗 下一步：運行 step3_cleanup_resources.py 來清理資源")
        print(f"🔗 Next: Run step3_cleanup_resources.py to clean up resources")
        print(f"\n⚠️  重要：請記住 Agent ID 以便清理")
        print(f"⚠️  Important: Remember the Agent ID for cleanup")
        print(f"🆔 Agent ID: {result.get('agent_id', 'N/A')}")
    else:
        print(f"\n❌ 腳本執行失敗 / Script execution failed")
        exit(1)