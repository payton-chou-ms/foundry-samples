# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
import datetime
from typing import Any, Callable, Set, Dict, List, Optional
from datetime import datetime, timedelta
import random

# Microsoft Fabric lakehouse 中計程車行程數據的模擬查詢函數
# 在實際實作中，這些函數會連接到您的 Fabric lakehouse 並執行 SQL 查詢

def mock_execute_query(query: str) -> Dict[str, Any]:
    """
    模擬對計程車行程數據執行 SQL 查詢的函數。
    在實際實作中，這會連接到 Microsoft Fabric lakehouse。
    """
    print(f"正在執行查詢: {query[:100]}...")
    # 返回示範用的模擬數據
    return {"result": "模擬查詢結果", "query": query}

# 基本查詢和聚合函數

def get_daily_trip_stats(date: str) -> str:
    """
    取得特定日期的總行程數和營收。
    
    :param date: YYYY-MM-DD 格式的日期
    :return: 包含行程統計的 JSON 字串
    """
    query = f"""
    SELECT 
        COUNT(*) as total_trips,
        SUM(fare_amount) as total_revenue,
        AVG(fare_amount) as avg_fare
    FROM taxi_trips 
    WHERE DATE(pickup_datetime) = '{date}'
    """
    
    # 模擬數據產生
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
    """
    Get monthly trip count and fare statistics for a given year.
    
    :param year: Year to analyze (e.g., 2024)
    :return: JSON string with monthly statistics
    """
    query = f"""
    SELECT 
        MONTH(pickup_datetime) as month,
        COUNT(*) as trip_count,
        SUM(fare_amount) as total_fare
    FROM taxi_trips 
    WHERE YEAR(pickup_datetime) = {year}
    GROUP BY MONTH(pickup_datetime)
    ORDER BY month
    """
    
    # Mock data generation
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

def get_vehicle_and_driver_count() -> str:
    """
    Get count of unique vehicles (medallions) and active drivers.
    
    :return: JSON string with vehicle and driver counts
    """
    query = """
    SELECT 
        COUNT(DISTINCT medallion) as unique_vehicles,
        COUNT(DISTINCT hack_license) as active_drivers
    FROM taxi_trips 
    WHERE pickup_datetime >= DATEADD(month, -1, GETDATE())
    """
    
    # Mock data
    result = {
        "unique_vehicles": random.randint(12000, 15000),
        "active_drivers": random.randint(30000, 40000),
        "period": "Last 30 days"
    }
    
    return json.dumps(result)

# 歷史趨勢函數

def get_monthly_revenue_trends() -> str:
    """
    Get monthly revenue trends with month-over-month and year-over-year comparisons.
    
    :return: JSON string with trend analysis
    """
    query = """
    SELECT 
        YEAR(pickup_datetime) as year,
        MONTH(pickup_datetime) as month,
        SUM(fare_amount) as total_revenue,
        AVG(fare_amount) as avg_fare
    FROM taxi_trips 
    WHERE pickup_datetime >= DATEADD(year, -1, GETDATE())
    GROUP BY YEAR(pickup_datetime), MONTH(pickup_datetime)
    ORDER BY year, month
    """
    
    # Mock trend data
    trends = []
    base_revenue = 2000000
    
    for month in range(1, 13):
        current_revenue = base_revenue + random.randint(-200000, 300000)
        mom_change = random.uniform(-5.0, 8.0)  # Month over month %
        yoy_change = random.uniform(-2.0, 12.0)  # Year over year %
        
        trends.append({
            "month": month,
            "total_revenue": round(current_revenue, 2),
            "avg_fare": round(random.uniform(12.0, 18.0), 2),
            "mom_change_percent": round(mom_change, 2),
            "yoy_change_percent": round(yoy_change, 2)
        })
    
    result = {
        "period": "Past 12 months",
        "trends": trends
    }
    
    return json.dumps(result)

def get_top_growth_areas(months: int = 6) -> str:
    """
    Get top 10 areas with highest ride growth in recent months.
    
    :param months: Number of months to analyze (default 6)
    :return: JSON string with top growth areas
    """
    query = f"""
    WITH current_period AS (
        SELECT pickup_location_id, COUNT(*) as current_rides
        FROM taxi_trips 
        WHERE pickup_datetime >= DATEADD(month, -{months}, GETDATE())
        GROUP BY pickup_location_id
    ),
    previous_period AS (
        SELECT pickup_location_id, COUNT(*) as previous_rides
        FROM taxi_trips 
        WHERE pickup_datetime >= DATEADD(month, -{months*2}, GETDATE())
        AND pickup_datetime < DATEADD(month, -{months}, GETDATE())
        GROUP BY pickup_location_id
    )
    SELECT TOP 10
        c.pickup_location_id,
        c.current_rides,
        p.previous_rides,
        ((c.current_rides - p.previous_rides) * 100.0 / p.previous_rides) as growth_percent
    FROM current_period c
    JOIN previous_period p ON c.pickup_location_id = p.pickup_location_id
    ORDER BY growth_percent DESC
    """
    
    # Mock growth data
    areas = ['Manhattan Financial District', 'Brooklyn Heights', 'Queens Astoria', 
             'Bronx Yankee Stadium', 'Manhattan Midtown', 'LGA Airport',
             'JFK Airport', 'Brooklyn DUMBO', 'Manhattan Chelsea', 'Queens Flushing']
    
    top_areas = []
    for i, area in enumerate(areas):
        growth = random.uniform(15.0, 45.0)
        current_rides = random.randint(5000, 25000)
        previous_rides = int(current_rides / (1 + growth/100))
        
        top_areas.append({
            "rank": i + 1,
            "area": area,
            "location_id": f"LOC_{i+100}",
            "current_rides": current_rides,
            "previous_rides": previous_rides,
            "growth_percent": round(growth, 2)
        })
    
    result = {
        "period_months": months,
        "top_growth_areas": top_areas
    }
    
    return json.dumps(result)

# 異常和極值函數

def get_highest_fares(start_date: str, limit: int = 10) -> str:
    """
    Get highest fare amounts since a given date with trip details.
    
    :param start_date: Start date in YYYY-MM-DD format
    :param limit: Number of top fares to return (default 10)
    :return: JSON string with highest fare trips
    """
    query = f"""
    SELECT TOP {limit}
        trip_id,
        pickup_datetime,
        dropoff_datetime,
        pickup_location,
        dropoff_location,
        fare_amount,
        trip_distance,
        passenger_count
    FROM taxi_trips 
    WHERE pickup_datetime >= '{start_date}'
    ORDER BY fare_amount DESC
    """
    
    # Mock high fare data
    high_fares = []
    locations = [
        ('JFK Airport', 'Manhattan Financial District'),
        ('Newark Airport', 'Brooklyn Heights'),
        ('LGA Airport', 'Queens Astoria'),
        ('Manhattan Midtown', 'Bronx Yankee Stadium'),
        ('Brooklyn DUMBO', 'Staten Island Ferry')
    ]
    
    for i in range(limit):
        pickup_loc, dropoff_loc = random.choice(locations)
        fare = random.uniform(150.0, 500.0)
        distance = random.uniform(25.0, 60.0)
        
        high_fares.append({
            "rank": i + 1,
            "trip_id": f"TRIP_{random.randint(100000, 999999)}",
            "pickup_datetime": f"2025-{random.randint(1,8):02d}-{random.randint(1,28):02d} {random.randint(0,23):02d}:{random.randint(0,59):02d}:00",
            "pickup_location": pickup_loc,
            "dropoff_location": dropoff_loc,
            "fare_amount": round(fare, 2),
            "trip_distance": round(distance, 2),
            "passenger_count": random.randint(1, 4)
        })
    
    result = {
        "since_date": start_date,
        "top_fares": high_fares
    }
    
    return json.dumps(result)

def get_anomalous_short_high_fare_trips(days: int = 90) -> str:
    """
    Find anomalous short trips with high fares (distance < 1km, fare > $50).
    
    :param days: Number of days to look back (default 90)
    :return: JSON string with anomalous trips
    """
    query = f"""
    SELECT 
        trip_id,
        pickup_datetime,
        pickup_location,
        dropoff_location,
        fare_amount,
        trip_distance,
        payment_type
    FROM taxi_trips 
    WHERE pickup_datetime >= DATEADD(day, -{days}, GETDATE())
    AND trip_distance < 1.0
    AND fare_amount > 50
    ORDER BY fare_amount DESC
    """
    
    # Mock anomalous trip data
    anomalous_trips = []
    num_trips = random.randint(15, 30)
    
    for i in range(num_trips):
        anomalous_trips.append({
            "trip_id": f"ANOM_{random.randint(100000, 999999)}",
            "pickup_datetime": f"2025-{random.randint(1,8):02d}-{random.randint(1,28):02d} {random.randint(0,23):02d}:{random.randint(0,59):02d}:00",
            "pickup_location": "Manhattan Midtown",
            "dropoff_location": "Manhattan Midtown",
            "fare_amount": round(random.uniform(51.0, 120.0), 2),
            "trip_distance": round(random.uniform(0.1, 0.9), 2),
            "payment_type": random.choice(["Credit", "Cash", "Dispute"])
        })
    
    result = {
        "criteria": "Distance < 1km AND Fare > $50",
        "period_days": days,
        "anomalous_trips": anomalous_trips,
        "total_found": len(anomalous_trips)
    }
    
    return json.dumps(result)

# 地理分佈函數

def get_top_pickup_areas(days: int = 30) -> str:
    """
    Get top 10 pickup areas by ride volume with percentages.
    
    :param days: Number of days to analyze (default 30)
    :return: JSON string with top pickup areas
    """
    query = f"""
    SELECT TOP 10
        pickup_location,
        COUNT(*) as ride_count,
        (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM taxi_trips 
         WHERE pickup_datetime >= DATEADD(day, -{days}, GETDATE()))) as percentage
    FROM taxi_trips 
    WHERE pickup_datetime >= DATEADD(day, -{days}, GETDATE())
    GROUP BY pickup_location
    ORDER BY ride_count DESC
    """
    
    # Mock pickup area data
    areas = [
        'Manhattan Midtown', 'JFK Airport', 'LGA Airport', 'Manhattan Financial District',
        'Brooklyn Heights', 'Queens Astoria', 'Bronx Yankee Stadium', 'Manhattan Chelsea',
        'Brooklyn DUMBO', 'Staten Island Ferry'
    ]
    
    top_areas = []
    total_rides = random.randint(800000, 1200000)
    remaining_percentage = 100.0
    
    for i, area in enumerate(areas):
        if i == len(areas) - 1:  # Last area gets remaining percentage
            percentage = remaining_percentage
        else:
            percentage = random.uniform(5.0, 20.0)
            remaining_percentage -= percentage
        
        ride_count = int(total_rides * percentage / 100)
        
        top_areas.append({
            "rank": i + 1,
            "pickup_location": area,
            "ride_count": ride_count,
            "percentage": round(percentage, 2)
        })
    
    result = {
        "period_days": days,
        "total_rides": total_rides,
        "top_areas": top_areas
    }
    
    return json.dumps(result)

# 時間分析函數

def get_day_night_comparison(days: int = 60) -> str:
    """
    Compare day (7:00-19:00) vs night (19:00-7:00) ride patterns.
    
    :param days: Number of days to analyze (default 60)
    :return: JSON string with day/night comparison
    """
    query = f"""
    SELECT 
        CASE 
            WHEN DATEPART(hour, pickup_datetime) BETWEEN 7 AND 18 THEN 'Day'
            ELSE 'Night'
        END as time_period,
        COUNT(*) as ride_count,
        AVG(fare_amount) as avg_fare
    FROM taxi_trips 
    WHERE pickup_datetime >= DATEADD(day, -{days}, GETDATE())
    GROUP BY CASE 
                WHEN DATEPART(hour, pickup_datetime) BETWEEN 7 AND 18 THEN 'Day'
                ELSE 'Night'
             END
    """
    
    # Mock day/night data
    day_rides = random.randint(400000, 600000)
    night_rides = random.randint(300000, 500000)
    day_avg_fare = random.uniform(15.0, 20.0)
    night_avg_fare = random.uniform(18.0, 25.0)
    
    result = {
        "period_days": days,
        "day_period": "7:00-19:00",
        "night_period": "19:00-7:00",
        "day_stats": {
            "ride_count": day_rides,
            "avg_fare": round(day_avg_fare, 2),
            "percentage": round(day_rides / (day_rides + night_rides) * 100, 2)
        },
        "night_stats": {
            "ride_count": night_rides,
            "avg_fare": round(night_avg_fare, 2),
            "percentage": round(night_rides / (day_rides + night_rides) * 100, 2)
        },
        "fare_difference": round(night_avg_fare - day_avg_fare, 2)
    }
    
    return json.dumps(result)

def get_hourly_ride_patterns() -> str:
    """
    Get hourly ride distribution for weekdays vs weekends to identify peak hours.
    
    :return: JSON string with hourly patterns
    """
    query = """
    SELECT 
        DATEPART(hour, pickup_datetime) as hour,
        CASE 
            WHEN DATEPART(weekday, pickup_datetime) IN (1, 7) THEN 'Weekend'
            ELSE 'Weekday'
        END as day_type,
        COUNT(*) as ride_count
    FROM taxi_trips 
    WHERE pickup_datetime >= DATEADD(day, -30, GETDATE())
    GROUP BY DATEPART(hour, pickup_datetime),
             CASE 
                WHEN DATEPART(weekday, pickup_datetime) IN (1, 7) THEN 'Weekend'
                ELSE 'Weekday'
             END
    ORDER BY hour, day_type
    """
    
    # Mock hourly pattern data
    weekday_pattern = []
    weekend_pattern = []
    
    for hour in range(24):
        # Weekday pattern - peaks at rush hours
        if hour in [7, 8, 9, 17, 18, 19]:
            weekday_rides = random.randint(8000, 15000)
        elif hour in [10, 11, 12, 13, 14, 15, 16]:
            weekday_rides = random.randint(5000, 10000)
        else:
            weekday_rides = random.randint(1000, 5000)
        
        # Weekend pattern - peaks later in evening
        if hour in [12, 13, 14, 20, 21, 22]:
            weekend_rides = random.randint(6000, 12000)
        elif hour in [10, 11, 15, 16, 17, 18, 19]:
            weekend_rides = random.randint(4000, 8000)
        else:
            weekend_rides = random.randint(500, 4000)
        
        weekday_pattern.append({
            "hour": hour,
            "ride_count": weekday_rides
        })
        
        weekend_pattern.append({
            "hour": hour,
            "ride_count": weekend_rides
        })
    
    # Find peak hours
    weekday_peak = max(weekday_pattern, key=lambda x: x['ride_count'])
    weekend_peak = max(weekend_pattern, key=lambda x: x['ride_count'])
    
    result = {
        "period": "Last 30 days",
        "weekday_pattern": weekday_pattern,
        "weekend_pattern": weekend_pattern,
        "peak_hours": {
            "weekday": f"{weekday_peak['hour']}:00 ({weekday_peak['ride_count']} rides)",
            "weekend": f"{weekend_peak['hour']}:00 ({weekend_peak['ride_count']} rides)"
        }
    }
    
    return json.dumps(result)

# 乘客/司機行為函數

def get_passenger_count_distribution() -> str:
    """
    Get distribution of passenger counts by percentage.
    
    :return: JSON string with passenger count statistics
    """
    query = """
    SELECT 
        passenger_count,
        COUNT(*) as ride_count,
        (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM taxi_trips)) as percentage
    FROM taxi_trips 
    WHERE passenger_count > 0
    GROUP BY passenger_count
    ORDER BY percentage DESC
    """
    
    # Mock passenger count data (realistic distribution)
    passenger_data = [
        {"count": 1, "rides": random.randint(600000, 800000)},
        {"count": 2, "rides": random.randint(200000, 350000)},
        {"count": 3, "rides": random.randint(80000, 150000)},
        {"count": 4, "rides": random.randint(40000, 80000)},
        {"count": 5, "rides": random.randint(10000, 30000)},
        {"count": 6, "rides": random.randint(5000, 15000)}
    ]
    
    total_rides = sum(data["rides"] for data in passenger_data)
    
    distribution = []
    for data in passenger_data:
        percentage = (data["rides"] / total_rides) * 100
        distribution.append({
            "passenger_count": data["count"],
            "ride_count": data["rides"],
            "percentage": round(percentage, 2)
        })
    
    result = {
        "total_rides_analyzed": total_rides,
        "distribution": distribution
    }
    
    return json.dumps(result)

def get_highest_tip_rate_hours() -> str:
    """
    Get top 5 hours with highest tip rates (tip/fare ratio).
    
    :return: JSON string with highest tip rate hours
    """
    query = """
    SELECT TOP 5
        DATEPART(hour, pickup_datetime) as hour,
        AVG(tip_amount / fare_amount) as avg_tip_rate,
        COUNT(*) as total_trips
    FROM taxi_trips 
    WHERE fare_amount > 0 
    AND tip_amount > 0
    GROUP BY DATEPART(hour, pickup_datetime)
    ORDER BY avg_tip_rate DESC
    """
    
    # Mock tip rate data
    hours = list(range(24))
    random.shuffle(hours)
    
    top_tip_hours = []
    for i in range(5):
        hour = hours[i]
        tip_rate = random.uniform(0.15, 0.35)
        total_trips = random.randint(5000, 25000)
        
        top_tip_hours.append({
            "rank": i + 1,
            "hour": hour,
            "time_period": f"{hour:02d}:00-{(hour+1)%24:02d}:00",
            "avg_tip_rate": round(tip_rate, 3),
            "avg_tip_percentage": round(tip_rate * 100, 1),
            "total_trips": total_trips
        })
    
    # Sort by tip rate descending
    top_tip_hours.sort(key=lambda x: x['avg_tip_rate'], reverse=True)
    for i, hour_data in enumerate(top_tip_hours):
        hour_data['rank'] = i + 1
    
    result = {
        "metric": "Average tip rate (tip_amount / fare_amount)",
        "top_tip_hours": top_tip_hours
    }
    
    return json.dumps(result)

# 欄位統計函數

def get_fare_statistics_by_month(start_month: str, end_month: str) -> str:
    """
    Get fare statistics (avg, min, max, P90, P99) for each month in a range.
    
    :param start_month: Start month in YYYY-MM format
    :param end_month: End month in YYYY-MM format
    :return: JSON string with fare statistics by month
    """
    query = f"""
    SELECT 
        YEAR(pickup_datetime) as year,
        MONTH(pickup_datetime) as month,
        AVG(fare_amount) as avg_fare,
        MIN(fare_amount) as min_fare,
        MAX(fare_amount) as max_fare,
        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY fare_amount) as p90_fare,
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY fare_amount) as p99_fare
    FROM taxi_trips 
    WHERE pickup_datetime >= '{start_month}-01'
    AND pickup_datetime < DATEADD(month, 1, '{end_month}-01')
    GROUP BY YEAR(pickup_datetime), MONTH(pickup_datetime)
    ORDER BY year, month
    """
    
    # Parse month range
    start_year, start_month_num = map(int, start_month.split('-'))
    end_year, end_month_num = map(int, end_month.split('-'))
    
    monthly_stats = []
    current_date = datetime(start_year, start_month_num, 1)
    end_date = datetime(end_year, end_month_num, 1)
    
    while current_date <= end_date:
        month_stats = {
            "year": current_date.year,
            "month": current_date.month,
            "month_name": current_date.strftime("%B"),
            "avg_fare": round(random.uniform(12.0, 18.0), 2),
            "min_fare": round(random.uniform(2.5, 5.0), 2),
            "max_fare": round(random.uniform(200.0, 500.0), 2),
            "p90_fare": round(random.uniform(25.0, 35.0), 2),
            "p99_fare": round(random.uniform(60.0, 90.0), 2)
        }
        monthly_stats.append(month_stats)
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    result = {
        "period": f"{start_month} to {end_month}",
        "monthly_statistics": monthly_stats
    }
    
    return json.dumps(result)

def get_payment_type_analysis() -> str:
    """
    Get analysis of payment types with percentages and average fares.
    
    :return: JSON string with payment type analysis
    """
    query = """
    SELECT 
        payment_type,
        COUNT(*) as transaction_count,
        (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM taxi_trips)) as percentage,
        AVG(fare_amount) as avg_fare
    FROM taxi_trips 
    GROUP BY payment_type
    ORDER BY transaction_count DESC
    """
    
    # Mock payment type data
    payment_types = [
        {"type": "Credit Card", "count": random.randint(500000, 700000), "avg_fare": random.uniform(16.0, 20.0)},
        {"type": "Cash", "count": random.randint(300000, 450000), "avg_fare": random.uniform(14.0, 18.0)},
        {"type": "No Charge", "count": random.randint(20000, 50000), "avg_fare": 0.0},
        {"type": "Dispute", "count": random.randint(5000, 15000), "avg_fare": random.uniform(12.0, 16.0)},
        {"type": "Unknown", "count": random.randint(3000, 10000), "avg_fare": random.uniform(13.0, 17.0)}
    ]
    
    total_transactions = sum(pt["count"] for pt in payment_types)
    
    payment_analysis = []
    for pt in payment_types:
        percentage = (pt["count"] / total_transactions) * 100
        payment_analysis.append({
            "payment_type": pt["type"],
            "transaction_count": pt["count"],
            "percentage": round(percentage, 2),
            "avg_fare": round(pt["avg_fare"], 2)
        })
    
    result = {
        "total_transactions": total_transactions,
        "payment_breakdown": payment_analysis
    }
    
    return json.dumps(result)

# 為代理程式建立函數集合的輔助函數
taxi_query_functions: Set[Callable[..., Any]] = {
    get_daily_trip_stats,
    get_monthly_statistics,
    get_vehicle_and_driver_count,
    get_monthly_revenue_trends,
    get_top_growth_areas,
    get_highest_fares,
    get_anomalous_short_high_fare_trips,
    get_top_pickup_areas,
    get_day_night_comparison,
    get_hourly_ride_patterns,
    get_passenger_count_distribution,
    get_highest_tip_rate_hours,
    get_fare_statistics_by_month,
    get_payment_type_analysis
}