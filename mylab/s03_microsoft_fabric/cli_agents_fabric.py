# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
說明:
    此範例展示如何使用具有持續對話功能的代理程式來分析 Microsoft Fabric lakehouse 
    中的計程車行程數據。代理程式可以處理各種類型的查詢，包括基本統計、趨勢分析、
    異常檢測和地理分析。

必要條件:
    1) 設定包含計程車行程數據的 Microsoft Fabric lakehouse
    2) 配置具有適當模型部署的 Azure AI Foundry 專案
    
使用方法:
    python sample_agents_fabric.py
 
    執行範例前:
 
    pip install azure-ai-projects azure-identity python-dotenv

    使用您自己的值設定這些環境變數:
    1) PROJECT_ENDPOINT - 專案端點，可在您的 Azure AI Foundry 專案概觀頁面中找到
    2) MODEL_DEPLOYMENT_NAME - AI 模型的部署名稱，可在您的 Azure AI Foundry 專案
       「模型 + 端點」分頁的「名稱」欄位下找到
"""

# <imports>
import os
import time
from typing import Set
from dotenv import load_dotenv

from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential

# 載入環境變數
load_dotenv()

# 匯入計程車查詢函數
from taxi_query_functions import taxi_query_functions
# </imports>

# <sample_questions>
# 從 sample.txt 提取的範例問題，用於定義代理程式個性和能力
SAMPLE_QUESTIONS = [
    "比較國定假日與一般平日的計程車總行程數。此外，分析假日與平日之間的平均行程距離和平均車資是否有顯著差異。提供關於人們在假日是否行駛更長距離或支付更高車資的洞察。",
    "計算車資金額大於 70 的行程數量。同時，計算這些高車資行程相對於所有行程的百分比。",
    "比較日間（7:00–19:00）與夜間（19:00–7:00）的行程數量和平均車資金額。此外，顯示日間和夜間行程的行程距離是否有差異。",
    "識別擁有最高行程數的上車郵遞區號。提供按行程量排名的前 5 個上車郵遞區號。",
    "確定資料集中最常見的乘客數量值（眾數）。提供所有行程中乘客數量的分佈。"
]
# </sample_questions>

def display_menu():
    """顯示查詢選擇的互動選單。"""
    print("\n" + "="*80)
    print("🚕 計程車數據分析助手 - Microsoft Fabric Agent")
    print("="*80)
    print("\n請選擇查詢類型：")
    
    print("\n範例問題 (基於 sample.txt)：")
    for i, query in enumerate(SAMPLE_QUESTIONS, 1):
        # Truncate long queries for menu display
        display_query = query[:100] + "..." if len(query) > 100 else query
        print(f"   {i}. {display_query}")
    
    print("\n0. 退出程式")
    print("9. 自定義查詢（直接輸入您的問題）")
    print("\n" + "="*80)

def get_query_by_selection(selection: str) -> str:
    """透過選擇編號取得範例查詢。"""
    try:
        query_num = int(selection)
        if 1 <= query_num <= len(SAMPLE_QUESTIONS):
            return SAMPLE_QUESTIONS[query_num - 1]
    except ValueError:
        pass
    return None

def process_message_with_retry(project_client, thread_id: str, agent_id: str, max_retries: int = 3):
    """使用重試機制處理代理程式執行。"""
    for attempt in range(max_retries):
        try:
            # 建立並處理執行
            run = project_client.agents.runs.create_and_process(
                thread_id=thread_id, 
                agent_id=agent_id
            )
            
            # 如果仍在處理中，等待完成
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
            time.sleep(2)  # 重試前等待
    
    return None

def display_messages(project_client, thread_id: str):
    """以格式化的方式顯示對話訊息。"""
    try:
        messages = project_client.agents.messages.list(thread_id=thread_id)
        
        # 轉換為清單並反轉以按時間順序顯示
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
# 建立專案用戶端
project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.environ["PROJECT_ENDPOINT"],
)
# </client_initialization>

def main():
    """執行持續對話代理程式的主要函數。"""
    
    # 檢查必要的環境變數
    required_vars = ["PROJECT_ENDPOINT", "MODEL_DEPLOYMENT_NAME"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment.")
        return
    
    with project_client:
        try:
            # <agent_creation>
            # 使用計程車查詢函數建立功能工具
            functions = FunctionTool(functions=taxi_query_functions)
            toolset = ToolSet()
            toolset.add(functions)
            
            # 啟用自動函數呼叫
            project_client.agents.enable_auto_function_calls(toolset)

            agent = project_client.agents.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="TaxiDataAnalysisAgent",
                instructions="""您是專業的計程車數據分析助手，專門分析 Microsoft Fabric lakehouse 中的計程車行程數據。

您的專業領域包括分析：
- 國定假日與平日的行程模式和費用比較
- 高費用行程分析（行程 > $70）及其百分比分佈  
- 日間（7:00-19:00）與夜間（19:00-7:00）行程和費用模式
- 地理分析，包括熱門上車地點和郵遞區號
- 乘客數量分佈和模態分析

您應該：
1. 提供清晰、結構化的回應，包含具體數字和統計資料
2. 使用適當的函數從 lakehouse 檢索真實數據
3. 基於數據分析提供洞察和趋势
4. 以繁體中文呈現資訊，同時保留技術術語和欄位名稱的英文
5. 始終保持專業和樂於助人的語調

當使用者詢問計程車行程數據時，提供包含相關統計、趨勢和可行洞察的全面分析。""",
                toolset=toolset,
            )
            print(f"✅ 成功建立代理，ID: {agent.id}")
            
            # 為持續對話建立線程
            thread = project_client.agents.threads.create()
            print(f"✅ 成功建立對話線程，ID: {thread.id}")
            
            print(f"\n🔑 **Agent Information:**")
            print(f"   Agent ID: {agent.id}")
            print(f"   Thread ID: {thread.id}")
            print(f"   Model: {os.environ['MODEL_DEPLOYMENT_NAME']}")
            print(f"   Status: Active (will be cleaned up on exit)")
            # </agent_creation>

            # <thread_management>
            # </thread_management>

            # 主要對話循環
            print("\n🎯 歡迎使用計程車數據分析助手！")
            print("您可以選擇預設查詢或輸入自定義問題。")
            
            while True:
                try:
                    display_menu()
                    user_choice = input("\n請選擇 (例如: 1, 2, 9 或 0): ").strip()
                    
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
                        sample_query = get_query_by_selection(user_choice)
                        if sample_query:
                            user_message = sample_query
                            print(f"\n📋 選擇的查詢: {sample_query[:100]}{'...' if len(sample_query) > 100 else ''}")
                        else:
                            print("❌ 無效的選擇，請重新選擇")
                            continue
                    
                    # 在線程中建立訊息
                    print("\n🔄 處理查詢中...")
                    message = project_client.agents.messages.create(
                        thread_id=thread.id,
                        role="user",
                        content=user_message
                    )
                    
                    # 使用重試機制處理訊息
                    run = process_message_with_retry(project_client, thread.id, agent.id)
                    
                    if run and run.status == "completed":
                        print(f"✅ 查詢處理完成")
                        
                        # 顯示對話
                        display_messages(project_client, thread.id)
                    else:
                        print("❌ 查詢處理失敗，請重試")
                    
                    # 詢問使用者是否要繼續
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
        
        # finally:
        #     # <cleanup>
        #     # 清理資源
        #     try:
        #         if 'agent' in locals():
        #             project_client.agents.delete_agent(agent.id)
        #             print(f"\n🧹 已清理代理資源")
        #     except Exception as e:
        #         print(f"⚠️  清理資源時發生錯誤: {str(e)}")
        #     # </cleanup>

if __name__ == "__main__":
    main()