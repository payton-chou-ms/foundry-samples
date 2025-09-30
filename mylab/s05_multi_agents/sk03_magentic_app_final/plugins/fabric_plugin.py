# Copyright (c) Microsoft. All rights reserved.

import json
import random
from semantic_kernel.functions import kernel_function


class FabricPlugin:
    """Microsoft Fabric 插件 - 處理商業智慧和計程車數據分析"""
    
    def __init__(self):
        self.fabric_connection = None
    
    def set_connection(self, fabric_connection):
        """設定 Microsoft Fabric 連接"""
        self.fabric_connection = fabric_connection
    
    @kernel_function
    def query_fabric(self, question: str, query_type: str = "general") -> str:
        """
        向 Microsoft Fabric lakehouse 查詢計程車數據並取得回應。
        這是一個模擬函數，在實際實作中會連接到真實的 Fabric lakehouse。
        
        Args:
            question: 要查詢的問題
            query_type: 查詢類型 (general, stats, trends, anomaly, geography)
            
        Returns:
            str: JSON 格式的回應，包含查詢結果
        """
        if not self.fabric_connection:
            return json.dumps({
                "error": "Microsoft Fabric connection not initialized",
                "details": "Please ensure FOUNDRY_FABRIC_CONNECTION_NAME is set correctly"
            })
        
        try:
            # 這裡模擬 Fabric lakehouse 查詢
            # 在實際實作中，這會執行 SQL 查詢到 Fabric lakehouse
            
            if "總行程數" in question or "trip count" in question.lower():
                # 模擬行程統計查詢
                holiday_trips = random.randint(45000, 55000)
                weekday_trips = random.randint(65000, 75000)
                return json.dumps({
                    "query": question,
                    "result": {
                        "holiday_trips": holiday_trips,
                        "weekday_trips": weekday_trips,
                        "difference": weekday_trips - holiday_trips,
                        "analysis": f"平日行程數 ({weekday_trips}) 比國定假日 ({holiday_trips}) 多 {weekday_trips - holiday_trips} 趟"
                    }
                })
            elif "車資" in question or "fare" in question.lower():
                # 模擬車資分析查詢
                avg_fare = round(random.uniform(12.5, 15.8), 2)
                high_fare_count = random.randint(8000, 12000)
                total_trips = random.randint(500000, 600000)
                percentage = round((high_fare_count / total_trips) * 100, 2)
                return json.dumps({
                    "query": question,
                    "result": {
                        "average_fare": avg_fare,
                        "high_fare_trips": high_fare_count,
                        "total_trips": total_trips,
                        "percentage": percentage,
                        "analysis": f"平均車資為 ${avg_fare}，高車資行程 (>$70) 佔 {percentage}%"
                    }
                })
            elif "日間" in question and "夜間" in question:
                # 模擬日夜對比查詢
                day_trips = random.randint(380000, 420000)
                night_trips = random.randint(180000, 220000)
                day_avg_fare = round(random.uniform(13.2, 15.5), 2)
                night_avg_fare = round(random.uniform(14.8, 17.2), 2)
                return json.dumps({
                    "query": question,
                    "result": {
                        "day_trips": day_trips,
                        "night_trips": night_trips,
                        "day_avg_fare": day_avg_fare,
                        "night_avg_fare": night_avg_fare,
                        "analysis": f"日間行程: {day_trips} 趟 (平均 ${day_avg_fare})，夜間行程: {night_trips} 趟 (平均 ${night_avg_fare})"
                    }
                })
            else:
                # 一般查詢回應
                return json.dumps({
                    "query": question,
                    "result": {
                        "message": "這是一個關於計程車數據的模擬分析結果",
                        "data_source": "Microsoft Fabric lakehouse (模擬)",
                        "note": "實際實作中會執行真實的 SQL 查詢"
                    }
                })

        except Exception as e:
            return json.dumps({
                "error": "查詢 Microsoft Fabric lakehouse 時發生錯誤",
                "details": str(e)
            })