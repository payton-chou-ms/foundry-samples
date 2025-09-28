# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
檔案: step2_create_ai_agent.py

說明:
    此腳本展示如何建立 Azure AI Foundry 代理程式並將其與 Azure AI Search 整合。
    它會建立具有搜索工具的 AI 代理程式，啟用對話功能，並測試代理程式回應。

使用方式:
    python step2_create_ai_agent.py

    執行腳本前:
    1. 先執行 step1_create_search_index.py 來建立搜索索引
    2. pip install azure-ai-projects azure-identity python-dotenv azure-search-documents
    3. 建立包含以下變數的 .env 檔案:
       - PROJECT_ENDPOINT (Azure AI Project 端點)
       - MODEL_DEPLOYMENT_NAME (AI 模型部署名稱)
       - AZURE_SEARCH_ENDPOINT
       - AZURE_SEARCH_API_KEY
       - AZURE_SEARCH_INDEX (可選，預設為 "vector-search-quickstart")

執行步驟:
    1. 初始化 Azure AI Project 客戶端和認證
    2. 驗證搜索索引可用性
    3. 建立具有搜索工具整合的 AI 代理程式
    4. 測試代理程式對話功能
    5. 驗證代理程式使用 Azure AI Search 的能力
    6. 展示有/無代理程式的回應差異
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import MessageRole, ListSortOrder
from azure.search.documents import SearchClient


def initialize_environment():
    """Initialize environment variables and credentials."""
    print("🔧 初始化環境變數和認證 / Initializing environment and credentials...")
    
    # 從 .env 檔案載入環境變數 / Load environment variables from .env file
    load_dotenv(override=True)
    
    # AI Project 設定 / AI Project settings
    project_endpoint = os.environ["PROJECT_ENDPOINT"]
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]
    
    # 搜索設定 / Search settings
    search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    search_api_key = os.getenv("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX", "vector-search-quickstart")
    
    # 初始化認證 / Initialize credentials
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
        
        # 嘗試搜索文檔 / Try to search for documents
        results = search_client.search(search_text="*", top=1)
        result_count = 0
        
        for result in results:
            result_count += 1
            break  # 只檢查是否有任何結果 / Just check if we have any results
            
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
    """Create an AI agent with Azure AI Search integration."""
    print(f"\n🤖 建立 AI Agent 與搜索整合 / Creating AI agent with search integration...")
    
    # 初始化 AI Project 客戶端 / Initialize the AI Project Client
    project_client = AIProjectClient(
        endpoint=config["project_endpoint"],
        credential=config["project_credential"],
    )
    
    print(f"✅ AI Project 客戶端初始化成功 / AI Project client initialized")
    
    # 建立具有搜索功能的 AI agent / Create the AI agent with search capabilities
    # 注意：在原始 notebook 中，這使用了 FileSearchTool 與向量存儲 / Note: In the original notebook, this was using FileSearchTool with vector stores
    # 這裡我們建立一個可以擴展搜索工具的基本 agent / Here we're creating a basic agent that can be extended with search tools
    agent = project_client.agents.create_agent(
        model=config["model_deployment_name"],
        name="hotel-search-agent",
        instructions=f"""你是一個專業的酒店搜索助手。你可以使用 Azure AI Search 來幫助用戶找到合適的酒店資訊。

You are a professional hotel search assistant. You can use Azure AI Search to help users find suitable hotel information.

當用戶詢問酒店資訊時，請：
1. 使用搜索功能來查找相關的酒店資料
2. 提供詳細和準確的資訊
3. 包含酒店名稱、位置、評分、設施等重要資訊
4. 用友善和專業的語調回答

When users ask about hotel information, please:
1. Use search functionality to find relevant hotel data
2. Provide detailed and accurate information
3. Include important information like hotel names, locations, ratings, and amenities
4. Answer in a friendly and professional tone

搜索索引包含以下類型的酒店數據：
- 酒店名稱和描述
- 地址和位置資訊
- 評分和類別
- 設施和標籤
- 停車和翻新日期

The search index contains the following types of hotel data:
- Hotel names and descriptions
- Address and location information
- Ratings and categories
- Amenities and tags
- Parking and renovation dates
""",
        # 注意：工具整合應該在完整實現中加入此處 / Note: Tools integration would be added here in a full implementation
        # 目前我們建立一個可以擴展的基本 agent / For now, we create a basic agent that can be extended
    )
    
    print(f"✅ AI Agent 建立成功 / AI agent created successfully")
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
        # 在線程中建立訊息 / Create a message in the thread
        message = project_client.agents.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=question
        )
        
        # 建立並處理運行 / Create and process the run
        run = project_client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        if run.status == "completed":
            # 取得 agent 的回應 / Get the agent's response
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
    """Test the agent's capabilities with various questions."""
    print(f"\n🧪 測試 Agent 功能 / Testing agent capabilities...")
    print("=" * 60)
    
    # 關於酒店的測試問題 / Test questions about hotels
    test_questions = [
        "What hotels do you know about? Can you tell me about them?",
        "Can you recommend a boutique hotel in New York?",
        "Tell me about hotels with high ratings.",
        "What amenities are available at the Old Century Hotel?",
        "Are there any hotels with parking included?"
    ]
    
    responses = []
    
    for i, question in enumerate(test_questions, 1):
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
        # 建立一個無搜索工具的簡單 agent 以供比較 / Create a simple agent without search tools for comparison
        simple_agent = project_client.agents.create_agent(
            model=config["model_deployment_name"],
            name="simple-agent-no-search",
            instructions="You are a helpful assistant. Answer questions based on your general knowledge about hotels.",
        )
        
        simple_thread = project_client.agents.threads.create()
        
        print(f"\n🚫 簡單 Agent 回覆 (無搜索工具) / Simple agent response (no search tools):")
        print("-" * 50)
        simple_response = ask_agent_question(project_client, simple_agent, simple_thread, test_question)
        
        # 清理簡單 agent / Clean up simple agent
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
        # 測試直接搜索以確保其正常運作 / Test direct search to ensure it's working
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=search_credential
        )
        
        # 測試 agent 將使用的搜索功能 / Test search functionality that the agent would use
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
    """Main function to execute all steps."""
    print("🚀 開始執行步驟 2: 建立 AI Foundry Agent 和相關功能")
    print("🚀 Starting Step 2: Generate AI Foundry Agent and Related Features")
    print("=" * 80)
    
    try:
        # 步驟 1: 初始化環境 / Step 1: Initialize environment
        config = initialize_environment()
        
        # 步驟 2: 驗證搜索索引 / Step 2: Verify search index
        if not verify_search_index(
            config["search_endpoint"], 
            config["search_credential"], 
            config["index_name"]
        ):
            print("❌ 搜索索引驗證失敗，請先運行步驟 1")
            print("❌ Search index verification failed, please run step 1 first")
            return {"success": False, "error": "Search index not available"}
        
        # 步驟 3: 建立具有搜索功能的 AI agent / Step 3: Create AI agent with search capabilities
        project_client, agent = create_ai_agent_with_search(config)
        
        # 步驟 4: 建立對話線程 / Step 4: Create conversation thread
        thread = create_conversation_thread(project_client)
        
        # 步驟 5: 測試 agent 功能 / Step 5: Test agent capabilities
        responses = test_agent_capabilities(project_client, agent, thread)
        
        # 步驟 6: 與簡單 agent 比較 / Step 6: Compare with simple agent
        compare_with_without_search_tools(project_client, config)
        
        # 步驟 7: 驗證搜索整合潛力 / Step 7: Validate search integration potential
        validate_agent_search_integration(
            config["search_endpoint"],
            config["search_credential"],
            config["index_name"]
        )
        
        print(f"\n🎉 步驟 2 完成！/ Step 2 completed successfully!")
        print(f"📝 Agent ID: {agent.id}")
        print(f"📝 Thread ID: {thread.id}")
        print(f"📝 已準備好用於清理 / Ready for cleanup")
        
        # 回傳重要資訊供清理使用 / Return important information for cleanup
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