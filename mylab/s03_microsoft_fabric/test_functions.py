#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to demonstrate the taxi query functions without requiring Azure connection.
This shows how the mock data functions work.
"""

from taxi_query_functions import (
    get_daily_trip_stats,
    get_monthly_statistics,
    get_vehicle_and_driver_count,
    get_highest_fares,
    get_top_pickup_areas,
    get_passenger_count_distribution
)
import json

def pretty_print_json(json_str: str) -> None:
    """Pretty print JSON string."""
    data = json.loads(json_str)
    print(json.dumps(data, indent=2, ensure_ascii=False))

def test_functions():
    """Test the taxi query functions."""
    
    print("="*60)
    print("🚕 計程車數據查詢函數測試")
    print("="*60)
    
    # Test daily stats
    print("\n1. 日常統計測試:")
    print("-" * 30)
    result = get_daily_trip_stats("2025-08-01")
    pretty_print_json(result)
    
    # Test monthly statistics
    print("\n2. 月度統計測試:")
    print("-" * 30)
    result = get_monthly_statistics(2024)
    data = json.loads(result)
    print(f"2024年統計摘要:")
    print(f"  - 分析月份數: {len(data['monthly_statistics'])}")
    print(f"  - 第一個月: {data['monthly_statistics'][0]['month']}")
    print(f"  - 第一個月行程數: {data['monthly_statistics'][0]['trip_count']}")
    
    # Test vehicle count
    print("\n3. 車輛與駕駛統計:")
    print("-" * 30)
    result = get_vehicle_and_driver_count()
    pretty_print_json(result)
    
    # Test highest fares
    print("\n4. 最高車資測試:")
    print("-" * 30)
    result = get_highest_fares("2025-01-01", 5)
    data = json.loads(result)
    print(f"找到 {len(data['top_fares'])} 筆高車資記錄")
    if data['top_fares']:
        print(f"最高車資: ${data['top_fares'][0]['fare_amount']}")
    
    # Test pickup areas
    print("\n5. 熱門上車地點:")
    print("-" * 30)
    result = get_top_pickup_areas(30)
    data = json.loads(result)
    print(f"分析了 {data['total_rides']} 趟行程")
    print("前3名熱門地點:")
    for area in data['top_areas'][:3]:
        print(f"  {area['rank']}. {area['pickup_location']} - {area['percentage']}%")
    
    # Test passenger distribution
    print("\n6. 乘客數分布:")
    print("-" * 30)
    result = get_passenger_count_distribution()
    data = json.loads(result)
    print(f"分析總行程數: {data['total_rides_analyzed']}")
    print("乘客數分布:")
    for dist in data['distribution'][:3]:
        print(f"  {dist['passenger_count']} 人: {dist['percentage']}%")
    
    print("\n" + "="*60)
    print("✅ 所有測試完成！函數運行正常。")
    print("="*60)

if __name__ == "__main__":
    test_functions()