# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agents with continuous dialogue capability
    to analyze taxi trip data from Microsoft Fabric lakehouse. The agent can handle
    various types of queries including basic statistics, trends, anomalies, and
    geographic analysis.

PREREQUISITES:
    1) Set up a Microsoft Fabric lakehouse with taxi trip data
    2) Configure your Azure AI Foundry project with appropriate model deployment
    
USAGE:
    python sample_agents_fabric.py
 
    Before running the sample:
 
    pip install azure-ai-projects azure-identity python-dotenv

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

# <imports>
import os
import time
from typing import Set
from dotenv import load_dotenv

from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential

# Load environment variables
load_dotenv()

# Import taxi query functions
from taxi_query_functions import taxi_query_functions
# </imports>

# <predefined_queries>
PREDEFINED_QUERIES = {
    "1": {
        "title": "基礎查詢與彙總",
        "queries": [
            "2025-08-01 這一天的總行程數與總收入是多少？",
            "請按月份統計 2024 年的搭車趟數與總車資。",
            "目前系統內有多少不同的計程車（medallion）與活躍駕駛？"
        ]
    },
    "2": {
        "title": "歷史趨勢",
        "queries": [
            "過去一年每月的總收入與平均車資趨勢，並計算環比與年比。",
            "哪些區域在最近 6 個月的叫車量成長最多？列出 Top 10。"
        ]
    },
    "3": {
        "title": "異常與極端",
        "queries": [
            "自 2025-01-01 起最大的車資為何？請列出前 10 筆並附行程細節。",
            "找出異常短程但車資偏高的行程（例如距離 < 1km 且車資 > 50 美元），近 90 天。"
        ]
    },
    "4": {
        "title": "地理分布與比較",
        "queries": [
            "近 30 天哪個行政區的叫車量最多？請提供 Top 10 區域和佔比。",
            "比較 A 市與 B 市在 2025 年上半年的行程數與平均小費。"
        ]
    },
    "5": {
        "title": "時間分析",
        "queries": [
            "近 60 天日間（7:00–19:00）與夜間（19:00–7:00）的行程量與平均車資差異。",
            "平日與假日的每小時叫車分布，找出尖峰時段。"
        ]
    },
    "6": {
        "title": "乘客/駕駛行為",
        "queries": [
            "最常見的乘客數（passenger_count）是多少？按比例排序。",
            "哪些時段的小費率（tip / fare）最高？請列出 Top 5 小時區間。"
        ]
    },
    "7": {
        "title": "指定欄位統計",
        "queries": [
            "車資（fare_amount）的平均、最大、最小、P90、P99 在 2025-01~2025-06 各月分別是多少？",
            "針對支付方式（payment_type）計算占比與平均車資。"
        ]
    },
    "8": {
        "title": "綜合儀表板需求",
        "queries": [
            "建立一個月度 KPI 摘要：行程數、總收入、平均車資、平均距離、平均小費率、Top 5 區域。"
        ]
    }
}
# </predefined_queries>

def display_menu():
    """Display the interactive menu for query selection."""
    print("\n" + "="*80)
    print("🚕 計程車數據分析助手 - Microsoft Fabric Agent")
    print("="*80)
    print("\n請選擇查詢類型：")
    
    for key, category in PREDEFINED_QUERIES.items():
        print(f"\n{key}. {category['title']}")
        for i, query in enumerate(category["queries"], 1):
            print(f"   {key}.{i} {query}")
    
    print("\n0. 退出程式")
    print("9. 自定義查詢（直接輸入您的問題）")
    print("\n" + "="*80)

def get_query_by_selection(selection: str) -> str:
    """Get predefined query by selection number."""
    if "." in selection:
        category, query_num = selection.split(".")
        if category in PREDEFINED_QUERIES:
            queries = PREDEFINED_QUERIES[category]["queries"]
            try:
                query_index = int(query_num) - 1
                if 0 <= query_index < len(queries):
                    return queries[query_index]
            except ValueError:
                pass
    return None

def process_message_with_retry(project_client, thread_id: str, agent_id: str, max_retries: int = 3):
    """Process agent run with retry mechanism."""
    for attempt in range(max_retries):
        try:
            # Create and process the run
            run = project_client.agents.runs.create_and_process(
                thread_id=thread_id, 
                agent_id=agent_id
            )
            
            # Wait for completion if still processing
            while run.status in ["queued", "in_progress"]:
                time.sleep(1)
                run = project_client.agents.runs.get(thread_id=thread_id, run_id=run.id)
            
            if run.status == "completed":
                return run
            elif run.status == "failed":
                print(f"❌ Run failed (attempt {attempt + 1}/{max_retries}): {run.last_error}")
                if attempt == max_retries - 1:
                    return run
            else:
                print(f"⚠️  Run finished with status: {run.status}")
                return run
                
        except Exception as e:
            print(f"❌ Error in attempt {attempt + 1}/{max_retries}: {str(e)}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2)  # Wait before retry
    
    return None

def display_messages(project_client, thread_id: str):
    """Display the conversation messages in a formatted way."""
    try:
        messages = project_client.agents.messages.list(thread_id=thread_id)
        
        # Convert to list and reverse to show chronologically
        message_list = list(messages)
        message_list.reverse()
        
        print("\n" + "🔄 對話歷史:")
        print("-" * 60)
        
        for message in message_list:
            role = message.role
            content = message.content
            
            if role == "user":
                print(f"👤 您: {content}")
            elif role == "assistant":
                print(f"🤖 助手: {content}")
            print("-" * 60)
            
    except Exception as e:
        print(f"❌ Error displaying messages: {str(e)}")

# <client_initialization>
# Create the project client
project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.environ["PROJECT_ENDPOINT"],
)
# </client_initialization>

def main():
    """Main function to run the continuous dialogue agent."""
    
    # Check required environment variables
    required_vars = ["PROJECT_ENDPOINT", "MODEL_DEPLOYMENT_NAME"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment.")
        return
    
    with project_client:
        try:
            # <agent_creation>
            # Create function tool with taxi query functions
            functions = FunctionTool(functions=taxi_query_functions)
            toolset = ToolSet()
            toolset.add(functions)

            agent = project_client.agents.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="TaxiDataAnalysisAgent",
                instructions="""你是一個專業的計程車數據分析助手，專門分析 Microsoft Fabric lakehouse 中的計程車行程數據。

你的職責包括：
1. 回答關於計程車行程數據的各種查詢
2. 提供統計分析、趋勢分析和異常檢測
3. 生成清晰、有結構的報告
4. 用繁體中文回答問題，但保留英文的技術術語和欄位名稱

當用戶詢問數據查詢時，請：
- 使用適當的函數來獲取數據
- 提供清晰、有組織的回答
- 包含具體的數字和統計信息
- 如有必要，提供數據洞察和建議

請始終保持專業和友善的語調。""",
                toolset=toolset,
            )
            print(f"✅ 成功建立代理，ID: {agent.id}")
            # </agent_creation>

            # <thread_management>
            # Create a thread for continuous conversation
            thread = project_client.agents.threads.create()
            print(f"✅ 成功建立對話線程，ID: {thread.id}")
            # </thread_management>

            # Main conversation loop
            print("\n🎯 歡迎使用計程車數據分析助手！")
            print("您可以選擇預設查詢或輸入自定義問題。")
            
            while True:
                try:
                    display_menu()
                    user_choice = input("\n請選擇 (例如: 1.1, 2.2, 9 或 0): ").strip()
                    
                    if user_choice == "0":
                        print("\n👋 謝謝使用，再見！")
                        break
                    elif user_choice == "9":
                        custom_query = input("\n請輸入您的查詢: ").strip()
                        if not custom_query:
                            print("❌ 查詢不能為空")
                            continue
                        user_message = custom_query
                    else:
                        predefined_query = get_query_by_selection(user_choice)
                        if predefined_query:
                            user_message = predefined_query
                            print(f"\n📋 選擇的查詢: {predefined_query}")
                        else:
                            print("❌ 無效的選擇，請重新選擇")
                            continue
                    
                    # Create message in thread
                    print("\n🔄 處理查詢中...")
                    message = project_client.agents.messages.create(
                        thread_id=thread.id,
                        role="user",
                        content=user_message
                    )
                    
                    # Process the message with retry
                    run = process_message_with_retry(project_client, thread.id, agent.id)
                    
                    if run and run.status == "completed":
                        print(f"✅ 查詢處理完成")
                        
                        # Display the conversation
                        display_messages(project_client, thread.id)
                    else:
                        print("❌ 查詢處理失敗，請重試")
                    
                    # Ask if user wants to continue
                    continue_choice = input("\n是否繼續查詢？(y/n): ").strip().lower()
                    if continue_choice not in ['y', 'yes', '是', '']:
                        print("\n👋 謝謝使用，再見！")
                        break
                        
                except KeyboardInterrupt:
                    print("\n\n👋 程式被中斷，再見！")
                    break
                except Exception as e:
                    print(f"❌ 處理過程中發生錯誤: {str(e)}")
                    continue

        except Exception as e:
            print(f"❌ 初始化失敗: {str(e)}")
            return
        
        finally:
            # <cleanup>
            # Clean up resources
            try:
                if 'agent' in locals():
                    project_client.agents.delete_agent(agent.id)
                    print(f"\n🧹 已清理代理資源")
            except Exception as e:
                print(f"⚠️  清理資源時發生錯誤: {str(e)}")
            # </cleanup>

if __name__ == "__main__":
    main()