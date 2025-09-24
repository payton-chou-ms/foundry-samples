# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Enhanced interactive demo showcasing comprehensive Azure Logic Apps features with chat UI.
    This demo demonstrates:
    1. Multiple Logic App integrations
    2. Interactive chat interface
    3. Advanced function calling capabilities
    4. Real-time conversation handling
    5. Comprehensive error handling and logging
    
PREREQUISITES:
    1) Create multiple Logic Apps for different scenarios (email, notifications, data processing, etc.)
    2) Configure HTTP request triggers for each Logic App
    3) Set up Azure AI Foundry project with proper permissions
    
USAGE:
    python interactive_logic_apps_demo.py
    
    Set environment variables:
    - PROJECT_ENDPOINT: Azure AI Foundry project endpoint
    - MODEL_DEPLOYMENT_NAME: AI model deployment name
    - AZURE_SUBSCRIPTION_ID: Azure subscription ID
    - AZURE_RESOURCE_GROUP: Resource group containing Logic Apps
    - Multiple Logic App configurations (see .env.example)
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime
from typing import Set, Dict, Any, List, Optional
from dotenv import load_dotenv

from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential

# Import our custom modules
from user_functions import user_functions
from user_logic_apps import AzureLogicAppTool, create_send_email_function

# Load environment variables
load_dotenv()


class InteractiveLogicAppsDemo:
    """Enhanced interactive demo for Azure Logic Apps with chat interface."""
    
    def __init__(self):
        """Initialize the demo with Azure clients and Logic Apps."""
        self.project_client = None
        self.agent = None
        self.thread = None
        self.logic_app_tool = None
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Configuration from environment
        self.config = self._load_configuration()
        self._setup_clients()
        self._setup_logic_apps()
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load and validate configuration from environment variables."""
        required_vars = [
            "PROJECT_ENDPOINT",
            "MODEL_DEPLOYMENT_NAME", 
            "AZURE_SUBSCRIPTION_ID",
            "AZURE_RESOURCE_GROUP"
        ]
        
        config = {}
        missing_vars = []
        
        for var in required_vars:
            value = os.environ.get(var)
            if not value:
                missing_vars.append(var)
            else:
                config[var] = value
        
        if missing_vars:
            print(f"❌ 錯誤: 缺少必要的環境變數: {', '.join(missing_vars)}")
            print("請在 .env 檔案中設定這些變數")
            sys.exit(1)
            
        # Optional Logic App configurations
        logic_apps_config = {
            "email_app": {
                "name": os.environ.get("EMAIL_LOGIC_APP_NAME"),
                "trigger": os.environ.get("EMAIL_TRIGGER_NAME", "When_a_HTTP_request_is_received")
            },
            "notification_app": {
                "name": os.environ.get("NOTIFICATION_LOGIC_APP_NAME"),
                "trigger": os.environ.get("NOTIFICATION_TRIGGER_NAME", "When_a_HTTP_request_is_received")
            },
            "data_processing_app": {
                "name": os.environ.get("DATA_PROCESSING_LOGIC_APP_NAME"),
                "trigger": os.environ.get("DATA_PROCESSING_TRIGGER_NAME", "When_a_HTTP_request_is_received")
            }
        }
        
        config["logic_apps"] = logic_apps_config
        return config
    
    def _setup_clients(self):
        """Initialize Azure AI clients."""
        try:
            self.project_client = AIProjectClient(
                endpoint=self.config["PROJECT_ENDPOINT"],
                credential=DefaultAzureCredential(),
                api_version="latest",
            )
            print("✅ Azure AI 客戶端初始化成功")
        except Exception as e:
            print(f"❌ Azure AI 客戶端初始化失敗: {str(e)}")
            sys.exit(1)
    
    def _setup_logic_apps(self):
        """Setup Logic Apps tool and register available Logic Apps."""
        try:
            self.logic_app_tool = AzureLogicAppTool(
                subscription_id=self.config["AZURE_SUBSCRIPTION_ID"],
                resource_group=self.config["AZURE_RESOURCE_GROUP"]
            )
            
            registered_apps = []
            for app_key, app_config in self.config["logic_apps"].items():
                if app_config["name"]:
                    try:
                        self.logic_app_tool.register_logic_app(
                            app_config["name"],
                            app_config["trigger"]
                        )
                        registered_apps.append(f"{app_key}: {app_config['name']}")
                        print(f"✅ Logic App 註冊成功: {app_config['name']}")
                    except Exception as e:
                        print(f"⚠️  Logic App 註冊失敗 ({app_config['name']}): {str(e)}")
            
            if registered_apps:
                print(f"📱 已註冊的 Logic Apps: {', '.join(registered_apps)}")
            else:
                print("⚠️  沒有成功註冊任何 Logic Apps")
                
        except Exception as e:
            print(f"❌ Logic Apps 工具初始化失敗: {str(e)}")
            self.logic_app_tool = None
    
    def _create_enhanced_functions(self) -> Set:
        """Create enhanced function set including Logic Apps functions."""
        functions_set = user_functions.copy()
        
        # Add Logic Apps functions if available
        if self.logic_app_tool:
            for app_key, app_config in self.config["logic_apps"].items():
                if app_config["name"]:
                    # Create specialized function for each Logic App
                    func_name = f"invoke_{app_key}"
                    logic_app_func = self._create_logic_app_function(
                        app_config["name"], 
                        func_name
                    )
                    functions_set.add(logic_app_func)
        
        return functions_set
    
    def _create_logic_app_function(self, logic_app_name: str, function_name: str):
        """Create a specialized function for invoking a specific Logic App."""
        def logic_app_function(payload_json: str) -> str:
            f"""
            Invoke {logic_app_name} Logic App with custom payload.
            
            :param payload_json: JSON string containing the payload for the Logic App
            :return: Result of Logic App invocation
            """
            try:
                payload = json.loads(payload_json)
                result = self.logic_app_tool.invoke_logic_app(logic_app_name, payload)
                return json.dumps(result)
            except json.JSONDecodeError:
                return json.dumps({"error": "Invalid JSON payload"})
            except Exception as e:
                return json.dumps({"error": f"Logic App invocation failed: {str(e)}"})
        
        # Set function name for agent discovery
        logic_app_function.__name__ = function_name
        logic_app_function.__doc__ = f"Invoke {logic_app_name} Logic App with custom payload."
        
        return logic_app_function
    
    def _setup_agent(self):
        """Create the AI agent with comprehensive toolset."""
        try:
            # Create enhanced function set
            functions_to_use = self._create_enhanced_functions()
            
            # Setup agent tools
            functions = FunctionTool(functions=functions_to_use)
            toolset = ToolSet()
            toolset.add(functions)
            
            # Enable automatic function calls
            self.project_client.agents.enable_auto_function_calls(toolset)
            
            # Create agent with enhanced instructions
            agent_instructions = self._get_agent_instructions()
            
            self.agent = self.project_client.agents.create_agent(
                model=self.config["MODEL_DEPLOYMENT_NAME"],
                name="EnhancedLogicAppsAgent",
                instructions=agent_instructions,
                toolset=toolset,
            )
            
            print(f"🤖 智能代理創建成功 (ID: {self.agent.id})")
            
            # Create conversation thread
            self.thread = self.project_client.agents.threads.create()
            print(f"💬 對話線程創建成功 (ID: {self.thread.id})")
            
        except Exception as e:
            print(f"❌ 智能代理設定失敗: {str(e)}")
            sys.exit(1)
    
    def _get_agent_instructions(self) -> str:
        """Get comprehensive instructions for the agent."""
        return """
        您是一個專業的 Azure Logic Apps 助理，具備以下能力：

        核心功能：
        1. 📧 電子郵件發送和管理
        2. 📱 即時通知和提醒
        3. 📊 數據處理和分析
        4. 🕒 時間和日期操作
        5. 🌤️ 天氣資訊查詢
        6. 🧮 數學計算和轉換
        7. 👤 用戶資訊管理
        8. 📋 記錄處理和分析

        Logic Apps 整合：
        - 可以調用多個 Logic Apps 來執行複雜的業務流程
        - 支援自定義 payload 進行靈活的資料傳遞
        - 提供詳細的執行結果和錯誤處理

        互動原則：
        - 使用繁體中文回應
        - 提供清晰、詳細的說明
        - 主動建議相關功能
        - 確認重要操作後再執行
        - 提供友好的用戶體驗

        當用戶詢問功能時，請詳細說明可用的功能並提供具體的使用範例。
        """
    
    def _print_welcome_message(self):
        """Display welcome message and available features."""
        print("\n" + "="*60)
        print("🚀 Azure Logic Apps 互動式演示")
        print("="*60)
        print("歡迎使用增強版 Azure Logic Apps 演示系統！")
        print("\n📋 可用功能:")
        
        features = [
            "📧 發送電子郵件",
            "🕒 獲取當前時間",
            "🌤️ 查詢天氣資訊",  
            "🧮 數學計算",
            "🌡️ 溫度轉換",
            "🔄 布林值切換",
            "📝 字典合併",
            "👤 用戶資訊查詢",
            "📊 文字分析",
            "📋 記錄處理"
        ]
        
        for i, feature in enumerate(features, 1):
            print(f"   {i:2d}. {feature}")
        
        if self.logic_app_tool and any(app["name"] for app in self.config["logic_apps"].values()):
            print("\n🔗 已整合的 Logic Apps:")
            for app_key, app_config in self.config["logic_apps"].items():
                if app_config["name"]:
                    print(f"   • {app_key}: {app_config['name']}")
        
        print("\n💡 範例指令:")
        examples = [
            "「現在幾點？」",
            "「幫我發送郵件給 john@example.com，主題是會議提醒」",
            "「查詢台北的天氣」",
            "「計算 45 + 55」",
            "「將 25 度 C 轉換為華氏」",
            "「取得用戶 ID 1 的資訊」"
        ]
        
        for example in examples:
            print(f"   • {example}")
        
        print("\n📝 輸入 'quit' 或 'exit' 結束對話")
        print("="*60 + "\n")
    
    def _process_user_message(self, user_input: str) -> str:
        """Process user message and get agent response."""
        try:
            # Create message in thread
            message = self.project_client.agents.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=user_input,
            )
            
            # Process with agent
            run = self.project_client.agents.runs.create_and_process(
                thread_id=self.thread.id, 
                agent_id=self.agent.id
            )
            
            if run.status == "failed":
                return f"❌ 處理失敗: {run.last_error}"
            
            # Get latest messages
            messages = self.project_client.agents.messages.list(thread_id=self.thread.id)
            
            # Find the latest assistant message
            for message in messages:
                if message.role == "assistant":
                    if hasattr(message, 'content') and message.content:
                        for content_item in message.content:
                            if hasattr(content_item, 'text') and content_item.text:
                                return content_item.text.value
            
            return "❌ 無法獲取回應"
            
        except Exception as e:
            return f"❌ 處理錯誤: {str(e)}"
    
    def _save_conversation_history(self):
        """Save conversation history to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/logic_apps_conversation_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
            
            print(f"💾 對話歷史已保存到: {filename}")
            
        except Exception as e:
            print(f"⚠️  保存對話歷史失敗: {str(e)}")
    
    def start_interactive_chat(self):
        """Start the interactive chat interface."""
        self._setup_agent()
        self._print_welcome_message()
        
        try:
            while True:
                # Get user input
                user_input = input("👤 您: ").strip()
                
                # Check exit conditions
                if user_input.lower() in ['quit', 'exit', '退出', '結束']:
                    print("👋 感謝使用 Azure Logic Apps 演示！再見！")
                    break
                
                if not user_input:
                    continue
                
                # Record start time
                start_time = time.time()
                print("🤖 正在處理您的請求...")
                
                # Process message
                response = self._process_user_message(user_input)
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                # Display response
                print(f"\n🤖 助理: {response}")
                print(f"⏱️  處理時間: {processing_time:.2f} 秒\n")
                
                # Save to conversation history
                self.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "user_input": user_input,
                    "assistant_response": response,
                    "processing_time": processing_time
                })
                
        except KeyboardInterrupt:
            print("\n\n👋 收到中斷信號，正在結束對話...")
        
        except Exception as e:
            print(f"\n❌ 對話過程中發生錯誤: {str(e)}")
        
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Cleanup resources."""
        try:
            if self.conversation_history:
                self._save_conversation_history()
            
            if self.agent and self.project_client:
                self.project_client.agents.delete_agent(self.agent.id)
                print("🗑️  智能代理已清理")
                
        except Exception as e:
            print(f"⚠️  清理過程中發生錯誤: {str(e)}")
    
    def run_demo_scenarios(self):
        """Run automated demo scenarios to showcase features."""
        print("\n🎬 運行自動化演示場景...")
        self._setup_agent()
        
        demo_scenarios = [
            "現在幾點？請使用 '%Y-%m-%d %H:%M:%S' 格式顯示",
            "查詢紐約的天氣資訊",
            "計算 123 加 456 等於多少",
            "將 30 度攝氏轉換為華氏溫度",
            "切換布林值 True",
            "合併這兩個字典: {'name': 'Alice'} 和 {'age': 25}",
            "取得用戶 ID 2 的資訊",
            "在這些句子中找出最長的單詞: ['Hello world', 'Python programming', 'Azure Logic Apps']",
            "處理這些記錄: [{'a': 10, 'b': 20}, {'x': 5, 'y': 15}]"
        ]
        
        for i, scenario in enumerate(demo_scenarios, 1):
            print(f"\n📋 場景 {i}: {scenario}")
            print("🤖 處理中...")
            
            response = self._process_user_message(scenario)
            print(f"🤖 回應: {response}")
            
            time.sleep(1)  # Brief pause between scenarios
        
        self._cleanup()


def main():
    """Main function to run the interactive demo."""
    try:
        demo = InteractiveLogicAppsDemo()
        
        # Check command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == "--demo":
            demo.run_demo_scenarios()
        else:
            demo.start_interactive_chat()
            
    except KeyboardInterrupt:
        print("\n👋 程式被中斷，正在退出...")
    except Exception as e:
        print(f"❌ 程式執行錯誤: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()