# 導入必要的套件
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    AzureAISearchQueryType,
    AzureAISearchTool,
    ListSortOrder,
    MessageRole,
)
from azure.identity import DefaultAzureCredential

print("📦 正在設置 Azure AI Foundry Agent...")

# 載入 .env（若存在）
load_dotenv(override=True)

# 從環境變數獲取必要的設定
project_endpoint = os.environ.get("PROJECT_ENDPOINT")
# 兼容不同命名：優先 AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME，否則使用 MODEL_DEPLOYMENT_NAME
model_deployment_name = (
    os.environ.get("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME")
    or os.environ.get("MODEL_DEPLOYMENT_NAME")
)
azure_ai_connection_id = os.environ.get("AZURE_AI_CONNECTION_ID")  # （目前未直接使用，可用於 future）
index_name = os.environ.get("AZURE_SEARCH_INDEX", "vector-search-quickstart")

# 檢查必要的環境變數
missing_vars = []
if not project_endpoint:
    missing_vars.append("PROJECT_ENDPOINT")
if not model_deployment_name:
    missing_vars.append("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME")

if missing_vars:
    print(f"❌ 缺少必要的環境變數: {', '.join(missing_vars)}")
    print("🔧 請在 .env 文件中設置以下變數:")
    for var in missing_vars:
        print(f"   {var}=<your_value>")
    raise SystemExit(1)
else:
    print("✅ 環境變數檢查通過")
    print(f"   Project Endpoint: {project_endpoint}")
    print(f"   Model Deployment: {model_deployment_name}")
    print(f"   使用索引: {index_name}")


def create_agent_and_thread():
    """封裝 agent 與 thread 建立流程，失敗時回傳 None。"""
    try:
        print("🔧 正在初始化 AIProjectClient...")
        project_client_local = AIProjectClient(
            endpoint=project_endpoint,
            credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
        )
        print("✅ AIProjectClient 初始化成功")

        print("🔍 正在設置 Azure AI Search 工具...")
        ai_search_tool_local = AzureAISearchTool(
            index_connection_id="nqkdsearch",
            index_name=index_name,
            query_type=AzureAISearchQueryType.SEMANTIC,
            top_k=3,
            filter="",
        )
        print("✅ Azure AI Search 工具設置完成 (使用 SEMANTIC 查詢類型)")

        print("🤖 正在創建 AI Agent...")
        agent_local = project_client_local.agents.create_agent(
            model=model_deployment_name,
            name="hotel-search-agent",
            instructions=(
                "你是一個專業的飯店推薦助手。你可以根據用戶的需求，使用 Azure AI Search 來搜索和推薦合適的飯店。\n\n"
                "請使用搜索工具來查找相關的飯店資訊，然後提供詳細的推薦與說明。"
            ),
            tools=ai_search_tool_local.definitions,
            tool_resources=ai_search_tool_local.resources,
        )
        print(f"✅ AI Agent 創建成功! Agent ID: {agent_local.id}")
        print(f"   Agent 名稱: {agent_local.name}")
        print(
            f"   可用工具數量: {len(ai_search_tool_local.definitions) if ai_search_tool_local.definitions else 0}"
        )
        thread_local = project_client_local.agents.threads.create()
        print(f"🧵 Created thread ID: {thread_local.id}")
        return project_client_local, agent_local, thread_local
    except Exception as e:
        print(f"❌ 創建 Agent 或 Thread 時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


project_client, agent, thread = create_agent_and_thread()
if not agent or not thread:
    raise SystemExit(1)

def run_queries(queries):
    print(f"\n🤖 Testing AI Agent with {len(queries)} different queries...")
    print("=" * 60)
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 50)
        try:
            project_client.agents.messages.create(
                thread_id=thread.id,
                role=MessageRole.USER,
                content=query,
            )
            run = project_client.agents.runs.create_and_process(
                thread_id=thread.id, agent_id=agent.id
            )
            print(f"✅ Run Status: {run.status}")
            if run.status == "completed":
                messages = project_client.agents.messages.list(
                    thread_id=thread.id,
                    order=ListSortOrder.DESCENDING,
                    limit=1,
                )
                message_list = list(messages)
                if message_list:
                    latest_message = message_list[0]
                    if latest_message.role == MessageRole.AGENT:
                        print("🤖 Agent Response:")
                        if latest_message.content:
                            for content in latest_message.content:
                                if getattr(content, "text", None):
                                    val = getattr(getattr(content, "text", None), "value", None)
                                    print(val if val else str(content.text))
                                else:
                                    print(str(content))
                        else:
                            print("📭 No content in response")
                    else:
                        print(f"⚠️ Latest message role: {latest_message.role}")
                else:
                    print("📭 No messages found")
            elif run.status == "failed":
                print(f"❌ Run failed: {run.last_error}")
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            import traceback
            traceback.print_exc()
        print("\n" + "=" * 60)


if __name__ == "__main__":
    test_queries = [
        "What are the best hotels for budget-conscious travelers?",
        "Can you recommend luxury hotels with spa facilities?",
        "What hotels are near the city center?",
        "Tell me about hotels with good ratings and reviews.",
    ]
    run_queries(test_queries)