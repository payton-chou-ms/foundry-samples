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

# <sample_questions>
# Sample questions from sample.txt to define agent personality and capabilities
SAMPLE_QUESTIONS = [
    "Compare the total number of taxi trips on public holidays versus regular weekdays. In addition, analyze whether the average trip distance and average fare amount differ significantly between holidays and weekdays. Provide insights into whether people travel longer distances or pay higher fares during holidays.",
    "Count the number of trips with fare amounts greater than 70. Also, calculate the percentage of these high-fare trips relative to all trips.", 
    "Compare the number of trips and average fare amount between daytime (7:00–19:00) and nighttime (19:00–7:00). Additionally, show whether trip distances differ between daytime and nighttime trips.",
    "Identify the pickup zip code with the highest number of trips. Provide the top 5 pickup zip codes ranked by trip volume.",
    "Determine the most frequent passenger count value (mode) in the dataset. Provide the distribution of passenger counts across all trips."
]
# </sample_questions>

def display_menu():
    """Display the interactive menu for query selection."""
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
    """Get sample query by selection number."""
    try:
        query_num = int(selection)
        if 1 <= query_num <= len(SAMPLE_QUESTIONS):
            return SAMPLE_QUESTIONS[query_num - 1]
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
            
            # Enable automatic function calls
            project_client.agents.enable_auto_function_calls(toolset)

            agent = project_client.agents.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="TaxiDataAnalysisAgent",
                instructions="""You are a professional taxi data analysis assistant specializing in analyzing taxi trip data from Microsoft Fabric lakehouse.

Your expertise includes analyzing:
- Public holidays vs weekdays trip patterns and fare comparisons
- High-fare trip analysis (trips > $70) and their percentage distribution  
- Daytime (7:00-19:00) vs nighttime (19:00-7:00) trip and fare patterns
- Geographic analysis including top pickup locations and zip codes
- Passenger count distributions and modal analysis

You should:
1. Provide clear, structured responses with specific numbers and statistics
2. Use appropriate functions to retrieve real data from the lakehouse
3. Offer insights and trends based on the data analysis
4. Present information in Traditional Chinese while preserving technical terms and field names in English
5. Always maintain a professional and helpful tone

When users ask about taxi trip data, provide comprehensive analysis including relevant statistics, trends, and actionable insights.""",
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