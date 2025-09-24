# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
FILE: app.py

DESCRIPTION:
    Azure AI Search Agent with Chainlit Interactive Chat Interface
    Azure AI 搜索代理與 Chainlit 互動式聊天介面
    
    This application creates an AI agent integrated with Azure AI Search
    and provides a user-friendly chat interface using Chainlit.
    
    此應用程式建立一個整合 Azure AI Search 的 AI 代理，
    並使用 Chainlit 提供友善的聊天介面。

USAGE:
    chainlit run app.py -w

    Before running:
    1. Install dependencies: pip install -r requirements.txt
    2. Set up environment variables in .env file
    3. Ensure search index is created by running ../step1_create_search_index.py
    
    執行前準備：
    1. 安裝相依套件：pip install -r requirements.txt  
    2. 在 .env 檔案中設定環境變數
    3. 執行 ../step1_create_search_index.py 確保搜索索引已建立
"""

import os
from typing import Optional
from dotenv import load_dotenv

import chainlit as cl
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    AzureAISearchQueryType, 
    AzureAISearchTool, 
    ListSortOrder, 
    MessageRole
)

# Global variables for Azure resources
project_client: Optional[AIProjectClient] = None
agent_id: Optional[str] = None


def initialize_azure_resources():
    """Initialize Azure AI Project client and create the AI agent.
    
    初始化 Azure AI Project 客戶端並建立 AI 代理。
    """
    global project_client, agent_id
    
    # Load environment variables
    load_dotenv()
    
    # Get required environment variables
    project_endpoint = os.environ.get("PROJECT_ENDPOINT")
    model_deployment_name = os.environ.get("MODEL_DEPLOYMENT_NAME")
    azure_ai_connection_id = os.environ.get("AZURE_AI_CONNECTION_ID")
    search_index = os.environ.get("AZURE_SEARCH_INDEX", "vector-search-quickstart")
    
    if not all([project_endpoint, model_deployment_name, azure_ai_connection_id]):
        raise ValueError(
            "Missing required environment variables. Please check your .env file.\n"
            "缺少必要的環境變數。請檢查您的 .env 檔案。\n"
            "Required: PROJECT_ENDPOINT, MODEL_DEPLOYMENT_NAME, AZURE_AI_CONNECTION_ID"
        )
    
    print("🔧 初始化 Azure 資源... / Initializing Azure resources...")
    print(f"📍 Project Endpoint: {project_endpoint}")
    print(f"🤖 Model: {model_deployment_name}")
    print(f"🔍 Search Index: {search_index}")
    
    # Initialize the AI Project Client
    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
        api_version="latest",
    )
    
    # Initialize the Azure AI Search tool
    ai_search = AzureAISearchTool(
        index_connection_id=azure_ai_connection_id,
        index_name=search_index,
        query_type=AzureAISearchQueryType.SIMPLE,
        top_k=5,  # Return top 5 results
        filter="",  # No additional filters
    )
    
    # Create the AI agent with search capabilities
    agent = project_client.agents.create_agent(
        model=model_deployment_name,
        name="search-chat-agent",
        instructions="""你是一個專業的智能搜索助手，能夠使用 Azure AI Search 來幫助用戶找到相關資訊。

You are a professional intelligent search assistant that can use Azure AI Search to help users find relevant information.

當用戶提出問題時，請：
1. 理解用戶的查詢意圖
2. 使用搜索工具查找相關資訊  
3. 基於搜索結果提供準確、有用的回答
4. 如果需要，提供額外的上下文或解釋
5. 保持友善、專業的對話風格

When users ask questions, please:
1. Understand the user's query intent
2. Use search tools to find relevant information
3. Provide accurate, helpful answers based on search results
4. Provide additional context or explanations if needed
5. Maintain a friendly, professional conversational style

你特別善於：
- 酒店和住宿資訊搜索
- 地點和評分查詢
- 設施和服務說明
- 價格和可用性資訊

You are particularly good at:
- Hotel and accommodation information search
- Location and rating queries  
- Amenities and service descriptions
- Price and availability information

如果搜索沒有找到相關結果，請誠實地告知用戶，並建議他們嘗試不同的查詢方式。

If search doesn't find relevant results, honestly inform the user and suggest they try different query approaches.
""",
        tools=ai_search.definitions,
        tool_resources=ai_search.resources,
    )
    
    agent_id = agent.id
    print("✅ AI Agent 建立成功 / AI Agent created successfully")
    print(f"🆔 Agent ID: {agent_id}")
    

@cl.on_chat_start
async def start():
    """Initialize the chat session.
    
    初始化聊天會話。
    """
    try:
        # Initialize Azure resources if not already done
        if project_client is None or agent_id is None:
            initialize_azure_resources()
        
        # Create a new conversation thread
        thread = project_client.agents.threads.create()
        
        # Store thread ID in user session
        cl.user_session.set("thread_id", thread.id)
        
        # Send welcome message
        welcome_msg = """🎉 歡迎使用 Azure AI Search Agent！/ Welcome to Azure AI Search Agent!

我是您的智能搜索助手，能夠幫您搜索和查找相關資訊。您可以用中文或英文與我對話。

I'm your intelligent search assistant, able to help you search and find relevant information. You can chat with me in Chinese or English.

📝 **範例查詢 / Example Queries:**
- "請推薦一些高評分的酒店" / "Please recommend some high-rated hotels"
- "有哪些酒店提供停車服務？" / "Which hotels offer parking facilities?"  
- "告訴我關於精品酒店的資訊" / "Tell me about boutique hotels"
- "搜尋紐約的酒店" / "Search for hotels in New York"

💡 **提示 / Tip:** 儘量具體描述您的需求，這樣我可以為您提供更準確的搜索結果！
Try to be specific about your needs so I can provide more accurate search results!"""
        
        await cl.Message(
            content=welcome_msg,
            author="Azure AI Search Agent"
        ).send()
        
        print("✅ 聊天會話已啟動 / Chat session started")
        print(f"🔗 Thread ID: {thread.id}")
        
    except Exception as e:
        error_msg = f"❌ 初始化失敗 / Initialization failed: {str(e)}"
        print(error_msg)
        await cl.Message(
            content=f"抱歉，初始化過程中發生錯誤。請檢查您的設定。\n\nSorry, an error occurred during initialization. Please check your configuration.\n\n錯誤詳情 / Error details: {str(e)}",
            author="System"
        ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages and generate responses using the AI agent.
    
    處理傳入訊息並使用 AI 代理生成回覆。
    """
    try:
        # Get thread ID from session
        thread_id = cl.user_session.get("thread_id")
        
        if not thread_id:
            await cl.Message(
                content="❌ 找不到聊天會話。請重新整理頁面。\n\nChat session not found. Please refresh the page.",
                author="System"
            ).send()
            return
        
        # Show typing indicator
        async with cl.Step(name="🤖 AI Agent 思考中... / AI Agent thinking...") as step:
            
            # Create user message in the thread
            project_client.agents.messages.create(
                thread_id=thread_id,
                role=MessageRole.USER,
                content=message.content
            )
            
            step.output = f"📝 用戶訊息已發送 / User message sent: {message.content[:100]}..."
            
            # Create and process the agent run
            run = project_client.agents.runs.create_and_process(
                thread_id=thread_id,
                agent_id=agent_id
            )
            
            step.output = f"🚀 代理執行狀態 / Agent run status: {run.status}"
        
        if run.status == "completed":
            # Get the latest messages from the thread
            messages = project_client.agents.messages.list(
                thread_id=thread_id,
                order=ListSortOrder.DESCENDING,
                limit=5  # Get last 5 messages to find the agent response
            )
            
            # Find the latest agent response
            agent_response = None
            for msg in messages.data:
                if msg.role == MessageRole.AGENT:
                    # Extract text content from the message
                    response_text = ""
                    if msg.content:
                        for content in msg.content:
                            if hasattr(content, 'text') and content.text:
                                if hasattr(content.text, 'value'):
                                    response_text += content.text.value
                                else:
                                    response_text += str(content.text)
                    
                    if response_text.strip():
                        agent_response = response_text
                        break
            
            if agent_response:
                await cl.Message(
                    content=agent_response,
                    author="Azure AI Search Agent"
                ).send()
            else:
                await cl.Message(
                    content="抱歉，我沒有收到有效的回覆。請再試一次。\n\nSorry, I didn't receive a valid response. Please try again.",
                    author="Azure AI Search Agent"
                ).send()
        
        elif run.status == "failed":
            error_details = run.last_error if hasattr(run, 'last_error') else "未知錯誤 / Unknown error"
            await cl.Message(
                content=f"❌ 處理您的請求時發生錯誤 / Error processing your request:\n\n{error_details}",
                author="System"
            ).send()
        
        else:
            await cl.Message(
                content=f"⚠️ 代理執行異常狀態 / Agent run in unexpected status: {run.status}",
                author="System"
            ).send()
    
    except Exception as e:
        error_msg = f"處理訊息時發生錯誤 / Error processing message: {str(e)}"
        print(f"❌ {error_msg}")
        await cl.Message(
            content=f"❌ {error_msg}",
            author="System"
        ).send()


@cl.on_chat_end
def end():
    """Clean up when chat session ends.
    
    聊天會話結束時進行清理。
    """
    print("💬 聊天會話已結束 / Chat session ended")
    # Note: We're not deleting the agent here as it might be shared across sessions
    # In a production environment, you might want to implement proper cleanup logic


if __name__ == "__main__":
    # This will be called when running with: chainlit run app.py
    print("🚀 啟動 Azure AI Search Agent with Chainlit...")
    print("🚀 Starting Azure AI Search Agent with Chainlit...")
    print("📍 請在瀏覽器中開啟 http://localhost:8000")
    print("📍 Please open http://localhost:8000 in your browser")