# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Simple demo script to showcase the enhanced Logic Apps features without requiring Azure setup.
    This demonstrates the core functionality and UI design of the interactive system.
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List

from user_functions import user_functions


class MockLogicAppsDemo:
    """Mock version of the Logic Apps demo for demonstration purposes."""
    
    def __init__(self):
        """Initialize mock demo."""
        self.conversation_history: List[Dict[str, Any]] = []
        self.available_functions = user_functions
        
    def _print_welcome_message(self):
        """Display welcome message and available features."""
        print("\n" + "="*60)
        print("🚀 Azure Logic Apps 互動式演示 (模擬模式)")
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
        
        print("\n💡 範例指令:")
        examples = [
            "「現在幾點？」",
            "「計算 45 + 55」",
            "「將 25 度 C 轉換為華氏」",
            "「查詢紐約的天氣」",
            "「取得用戶 ID 1 的資訊」",
            "「合併字典 {'name': 'Alice'} 和 {'age': 30}」"
        ]
        
        for example in examples:
            print(f"   • {example}")
        
        print("\n📝 輸入 'quit' 或 'exit' 結束對話")
        print("="*60 + "\n")
    
    def _process_user_input(self, user_input: str) -> str:
        """Process user input and simulate AI response with function calls."""
        
        # Simple keyword-based function matching for demo
        response = ""
        
        if "時間" in user_input or "幾點" in user_input:
            from user_functions import fetch_current_datetime
            result = fetch_current_datetime()
            result_data = json.loads(result)
            response = f"📅 當前時間：{result_data['current_time']}"
            
        elif "計算" in user_input or "加" in user_input or "+" in user_input:
            # Extract numbers for demonstration
            if "45" in user_input and "55" in user_input:
                from user_functions import calculate_sum
                result = calculate_sum(45, 55)
                result_data = json.loads(result)
                response = f"🧮 計算結果：45 + 55 = {result_data['result']}"
            else:
                response = "🧮 請提供要計算的兩個數字，例如：「計算 45 + 55」"
                
        elif "溫度" in user_input or "轉換" in user_input:
            if "25" in user_input:
                from user_functions import convert_temperature
                result = convert_temperature(25.0)
                result_data = json.loads(result)
                response = f"🌡️ 溫度轉換：25°C = {result_data['fahrenheit']}°F"
            else:
                response = "🌡️ 請提供要轉換的攝氏溫度，例如：「將 25 度 C 轉換為華氏」"
                
        elif "天氣" in user_input:
            from user_functions import fetch_weather
            location = "紐約" if "紐約" in user_input else "New York"
            result = fetch_weather("New York")
            result_data = json.loads(result)
            response = f"🌤️ {location}天氣：{result_data['weather']}"
            
        elif "用戶" in user_input or "使用者" in user_input:
            if "1" in user_input:
                from user_functions import get_user_info
                result = get_user_info(1)
                result_data = json.loads(result)
                user_info = result_data['user_info']
                response = f"👤 用戶資訊：姓名: {user_info['name']}, 電郵: {user_info['email']}"
            else:
                response = "👤 請指定用戶 ID，例如：「取得用戶 ID 1 的資訊」"
                
        elif "合併" in user_input or "字典" in user_input:
            from user_functions import merge_dicts
            dict1 = {"name": "Alice"}
            dict2 = {"age": 30}
            result = merge_dicts(dict1, dict2)
            result_data = json.loads(result)
            response = f"📝 合併結果：{result_data['merged_dict']}"
            
        elif "切換" in user_input or "布林" in user_input:
            from user_functions import toggle_flag
            result = toggle_flag(True)
            result_data = json.loads(result)
            response = f"🔄 切換結果：True → {result_data['toggled_flag']}"
            
        elif "郵件" in user_input or "email" in user_input.lower():
            response = "📧 模擬發送郵件功能（在實際環境中會透過 Logic Apps 發送）\n✅ 郵件發送成功！"
            
        else:
            response = """
❓ 我可以幫您執行以下操作：
• 🕒 查詢時間：「現在幾點？」
• 🧮 數學計算：「計算 45 + 55」
• 🌡️ 溫度轉換：「將 25 度 C 轉換為華氏」
• 🌤️ 天氣查詢：「查詢紐約的天氣」
• 👤 用戶查詢：「取得用戶 ID 1 的資訊」
• 📝 字典合併：「合併字典」
• 🔄 值切換：「切換布林值」
• 📧 發送郵件：「發送郵件」

請嘗試上述任何一種操作！
            """.strip()
        
        return response
    
    def start_demo(self):
        """Start the interactive demo."""
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
                response = self._process_user_input(user_input)
                
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
            self._print_summary()
    
    def _print_summary(self):
        """Print conversation summary."""
        if self.conversation_history:
            print(f"\n📊 對話摘要：")
            print(f"• 總對話次數：{len(self.conversation_history)}")
            total_time = sum(item['processing_time'] for item in self.conversation_history)
            print(f"• 總處理時間：{total_time:.2f} 秒")
            avg_time = total_time / len(self.conversation_history)
            print(f"• 平均回應時間：{avg_time:.2f} 秒")
            print("\n💾 在實際環境中，對話歷史會保存到檔案中。")
    
    def run_automated_demo(self):
        """Run automated demo scenarios."""
        print("\n🎬 執行自動化演示場景...")
        
        demo_scenarios = [
            "現在幾點？",
            "計算 45 + 55",
            "將 25 度 C 轉換為華氏",
            "查詢紐約的天氣",
            "取得用戶 ID 1 的資訊",
            "合併字典",
            "切換布林值 True",
            "發送郵件測試"
        ]
        
        for i, scenario in enumerate(demo_scenarios, 1):
            print(f"\n📋 場景 {i}: {scenario}")
            print("🤖 處理中...")
            
            start_time = time.time()
            response = self._process_user_input(scenario)
            processing_time = time.time() - start_time
            
            print(f"🤖 回應: {response}")
            print(f"⏱️  處理時間: {processing_time:.2f} 秒")
            
            # Save to history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": scenario,
                "assistant_response": response,
                "processing_time": processing_time
            })
            
            time.sleep(0.5)  # Brief pause between scenarios
        
        self._print_summary()


def main():
    """Main function to run the demo."""
    print("🔧 Azure Logic Apps 演示系統 - 模擬模式")
    print("此演示不需要 Azure 連線，展示系統功能和介面設計。\n")
    
    try:
        demo = MockLogicAppsDemo()
        
        # Ask user which mode to run
        print("請選擇演示模式：")
        print("1. 互動式對話模式")
        print("2. 自動化演示場景")
        
        choice = input("\n請輸入選擇 (1 或 2): ").strip()
        
        if choice == "2":
            demo.run_automated_demo()
        else:
            demo.start_demo()
            
    except KeyboardInterrupt:
        print("\n👋 程式被中斷，正在退出...")
    except Exception as e:
        print(f"❌ 程式執行錯誤: {str(e)}")


if __name__ == "__main__":
    main()