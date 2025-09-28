#!/usr/bin/env python3
"""
展示新代理程式配置和 UI 功能的示範腳本，
無需 Azure 認證即可使用。
"""

import sys
import os

# 將當前目錄新增到路徑中供匯入使用
sys.path.insert(0, os.path.dirname(__file__))

def demo_sample_questions():
    """展示範例問題功能。"""
    print("🚕 Microsoft Fabric Taxi Data Analysis Agent - Demo")
    print("=" * 60)
    
    # 匯入範例問題
    try:
        from sample_agents_fabric import SAMPLE_QUESTIONS, get_query_by_selection, display_menu
        from taxi_query_functions import taxi_query_functions
        
        print(f"✅ 成功從 sample.txt 載入 {len(SAMPLE_QUESTIONS)} 個範例問題")
        print(f"✅ 成功載入 {len(taxi_query_functions)} 個計程車查詢函數")
        print()
        
        # 顯示範例問題
        print("📝 範例問題（用於代理程式個性定義）:")
        print("-" * 50)
        for i, question in enumerate(SAMPLE_QUESTIONS, 1):
            print(f"{i}. {question}")
            print()
        
        # 展示查詢選擇
        print("🎯 展示：查詢選擇函數")
        print("-" * 30)
        test_selection = "1"
        selected_query = get_query_by_selection(test_selection)
        print(f"輸入：'{test_selection}'")
        print(f"輸出：{selected_query[:60]}...")
        print()
        
        # 顯示選單格式
        print("📋 CLI 選單預覽：")
        print("-" * 20)
        display_menu()
        
        print("\n🔧 實作功能：")
        print("- ✅ 基於 sample.txt 問題的代理程式配置")
        print("- ✅ 簡化的 CLI 選單（1-5, 9, 0）")
        print("- ✅ 包含提示按鈕的 Chainlit UI")
        print("- ✅ 代理程式生命週期管理")
        print("- ✅ 在兩個介面中顯示代理程式 ID")
        
        print("\n🚀 使用方法：")
        print("CLI:     python sample_agents_fabric.py")
        print("Web UI:  chainlit run chainlit_app.py")
        
        print("\n✨ 展示成功完成！")
        
    except ImportError as e:
        print(f"❌ 匯入錯誤：{e}")
        print("確保所有檔案都在相同目錄中。")
        return False
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        return False
    
    return True

if __name__ == "__main__":
    demo_sample_questions()