#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Demo script to showcase the interactive menu system without requiring Azure connection.
This demonstrates the user interface and query selection functionality.
"""

import json
import random

# Replicate the PREDEFINED_QUERIES from the main script
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

# Simple mock functions for demo
def get_daily_trip_stats(date: str) -> str:
    total_trips = random.randint(50000, 80000)
    total_revenue = random.randint(200000, 400000)
    avg_fare = total_revenue / total_trips
    result = {
        "date": date,
        "total_trips": total_trips,
        "total_revenue": round(total_revenue, 2),
        "average_fare": round(avg_fare, 2)
    }
    return json.dumps(result)

def get_monthly_statistics(year: int) -> str:
    monthly_stats = []
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for i, month in enumerate(months, 1):
        trip_count = random.randint(400000, 600000)
        total_fare = random.randint(1500000, 2500000)
        monthly_stats.append({
            "month": month,
            "month_number": i,
            "trip_count": trip_count,
            "total_fare": round(total_fare, 2),
            "average_fare": round(total_fare / trip_count, 2)
        })
    
    result = {
        "year": year,
        "monthly_statistics": monthly_stats
    }
    return json.dumps(result)

def demo_interactive_menu():
    """Demo the interactive menu system."""
    print("🎯 計程車數據分析助手 - 互動式選單展示")
    print("="*60)
    print("注意：這是展示模式，不需要 Azure 連接")
    print("="*60)
    
    # Show the menu
    display_menu()
    
    # Demo some query selections
    print("\n📋 範例查詢展示:")
    print("-" * 40)
    
    # Demo query 1.1
    query_1_1 = get_query_by_selection("1.1")
    if query_1_1:
        print(f"選擇 1.1: {query_1_1}")
        print("執行結果:")
        result = get_daily_trip_stats("2025-08-01")
        import json
        data = json.loads(result)
        print(f"  📊 總行程數: {data['total_trips']:,}")
        print(f"  💰 總收入: ${data['total_revenue']:,.2f}")
        print(f"  📈 平均車資: ${data['average_fare']:.2f}")
    
    print("\n" + "-" * 40)
    
    # Demo query 1.2
    query_1_2 = get_query_by_selection("1.2")
    if query_1_2:
        print(f"選擇 1.2: {query_1_2}")
        print("執行結果:")
        result = get_monthly_statistics(2024)
        import json
        data = json.loads(result)
        print(f"  📅 分析年份: {data['year']}")
        print(f"  📊 月份數: {len(data['monthly_statistics'])}")
        print("  前三個月統計:")
        for i, month_data in enumerate(data['monthly_statistics'][:3]):
            print(f"    {i+1}. {month_data['month']}: {month_data['trip_count']:,} 趟行程, ${month_data['total_fare']:,.2f}")
    
    print("\n" + "="*60)
    print("✅ 互動式選單展示完成！")
    print("要使用完整功能，請設定環境變數並執行 sample_agents_fabric.py")
    print("="*60)

def demo_all_query_categories():
    """Demo all query categories and their examples."""
    print("\n🗂️  所有查詢類別展示:")
    print("="*60)
    
    for category_id, category in PREDEFINED_QUERIES.items():
        print(f"\n{category_id}. {category['title']}")
        print("-" * len(category['title']))
        for i, query in enumerate(category['queries'], 1):
            print(f"  {category_id}.{i} {query}")
    
    print("\n" + "="*60)
    print("📊 統計:")
    total_queries = sum(len(cat['queries']) for cat in PREDEFINED_QUERIES.values())
    print(f"  總類別數: {len(PREDEFINED_QUERIES)}")
    print(f"  總查詢數: {total_queries}")
    print("="*60)

if __name__ == "__main__":
    demo_interactive_menu()
    demo_all_query_categories()