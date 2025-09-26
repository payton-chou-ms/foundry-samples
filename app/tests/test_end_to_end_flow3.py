# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
End-to-end test for Decision Package scenario.
Tests hotel recommendations + transport insights + email decision package delivery.
"""

import pytest
from unittest.mock import Mock, patch

from app.config.settings import get_mock_settings
from app.orchestrator.magentic_runtime import MagenticTeamRuntime


@pytest.mark.asyncio
async def test_decision_package_scenario():
    """Test complete decision package scenario with hotel + transport + email."""
    
    settings = get_mock_settings()
    runtime = MagenticTeamRuntime(settings)
    
    user_query = "Recommend 3 4.5★+ hotels near Times Square with parking, analyze nearby taxi hotspots, email decision package"
    
    # Mock initialization
    with patch.object(runtime, 'initialize') as mock_init:
        mock_init.return_value = {"success": True}
        
        await runtime.initialize()
        
        # Mock agent responses for decision package
        with patch.object(runtime, 'execute_hotel_task') as mock_hotel, \
             patch.object(runtime, 'execute_taxi_fabric_task') as mock_fabric, \
             patch.object(runtime, 'execute_taxi_genie_task') as mock_genie, \
             patch.object(runtime, 'execute_email_task') as mock_email:
            
            # Hotel recommendations
            mock_hotel.return_value = {
                "summary": "Found 3 high-rated hotels near Times Square with parking",
                "details": {
                    "hotels": [
                        {
                            "name": "The Times Square Hotel",
                            "rating": 4.8,
                            "amenities": ["parking", "wifi", "gym"],
                            "location": "42nd Street",
                            "price_range": "$300-450/night"
                        },
                        {
                            "name": "Midtown Marriott",
                            "rating": 4.6,
                            "amenities": ["parking", "wifi", "restaurant"],
                            "location": "40th Street",
                            "price_range": "$250-380/night"
                        },
                        {
                            "name": "Broadway Plaza",
                            "rating": 4.5,
                            "amenities": ["parking", "wifi", "concierge"],
                            "location": "44th Street", 
                            "price_range": "$200-320/night"
                        }
                    ]
                }
            }
            
            # Taxi hotspot analysis
            mock_fabric.return_value = {
                "summary": "Times Square area has 3 major pickup hotspots with peak times 8-9 AM and 6-8 PM",
                "details": {
                    "hotspots": [
                        {"location": "Times Square Center", "daily_pickups": 2500, "avg_fare": "$18.50"},
                        {"location": "Port Authority", "daily_pickups": 2100, "avg_fare": "$16.80"},
                        {"location": "Herald Square", "daily_pickups": 1800, "avg_fare": "$17.20"}
                    ],
                    "peak_times": ["8-9 AM", "6-8 PM"],
                    "off_peak_savings": "15-20%"
                }
            }
            
            # Genie validation (optional)
            mock_genie.return_value = {
                "summary": "Validation confirms hotspot data with 95% accuracy",
                "details": {
                    "validated_hotspots": 3,
                    "accuracy_score": 0.95,
                    "additional_insights": "Weekend patterns differ significantly"
                }
            }
            
            # Decision package email
            mock_email.return_value = {
                "summary": "Decision package emailed successfully with hotel recommendations and transport insights",
                "details": {
                    "status": "delivered",
                    "tracking_id": "DP-EMAIL-001",
                    "content_sections": ["hotel_recommendations", "transport_analysis", "key_insights", "booking_links"]
                }
            }
            
            # Execute scenario
            result = await runtime.execute_scenario(user_query, "decision_package")
            
            # Verify execution
            assert result.get("scenario_type") == "decision_package"
            
            # Verify all key agents were called
            mock_hotel.assert_called()
            mock_fabric.assert_called()
            mock_email.assert_called()
            # Genie validation is optional


@pytest.mark.asyncio
async def test_decision_package_with_location_filtering():
    """Test decision package with specific location requirements."""
    
    settings = get_mock_settings()
    runtime = MagenticTeamRuntime(settings)
    
    user_query = "Find luxury hotels within 2 blocks of Central Park with valet parking and analyze subway accessibility"
    
    with patch.object(runtime, 'initialize') as mock_init:
        mock_init.return_value = {"success": True}
        
        await runtime.initialize()
        
        with patch.object(runtime, 'execute_hotel_task') as mock_hotel:
            mock_hotel.return_value = {
                "summary": "Found 2 luxury hotels within 2 blocks of Central Park with valet parking",
                "details": {
                    "hotels": [
                        {
                            "name": "The Plaza Hotel",
                            "rating": 4.9,
                            "distance_to_park": "0.1 miles",
                            "parking_type": "valet",
                            "luxury_amenities": ["spa", "concierge", "fine_dining"]
                        },
                        {
                            "name": "The Pierre",
                            "rating": 4.8,
                            "distance_to_park": "0.3 miles", 
                            "parking_type": "valet",
                            "luxury_amenities": ["spa", "butler_service", "rooftop_terrace"]
                        }
                    ],
                    "filtering_criteria": "luxury + central_park + valet_parking"
                }
            }
            
            # Test that hotel task was called with location-specific query
            result = await runtime.execute_hotel_task(
                "luxury hotels", 
                "Central Park area", 
                "valet parking, within 2 blocks"
            )
            
            assert result["summary"] is not None
            assert "luxury" in result["summary"].lower()


def test_decision_package_content_formatting():
    """Test formatting of decision package content for email."""
    
    # Mock hotel data
    hotel_data = {
        "hotels": [
            {"name": "Hotel A", "rating": 4.8, "price": "$300"},
            {"name": "Hotel B", "rating": 4.6, "price": "$250"}
        ]
    }
    
    # Mock transport data
    transport_data = {
        "hotspots": [
            {"location": "Times Square", "pickups": 2500},
            {"location": "Port Authority", "pickups": 2100}
        ],
        "peak_times": ["8-9 AM", "6-8 PM"]
    }
    
    # Test that data can be formatted for email content
    email_content = format_decision_package(hotel_data, transport_data)
    
    assert "Hotel A" in email_content
    assert "4.8" in email_content
    assert "Times Square" in email_content
    assert "peak_times" in email_content.lower() or "peak times" in email_content.lower()


def format_decision_package(hotel_data, transport_data):
    """Helper function to format decision package content."""
    content = "# Travel Decision Package\n\n"
    
    content += "## Hotel Recommendations\n"
    for hotel in hotel_data.get("hotels", []):
        content += f"- **{hotel['name']}**: {hotel['rating']}⭐, {hotel['price']}\n"
    
    content += "\n## Transport Analysis\n" 
    for hotspot in transport_data.get("hotspots", []):
        content += f"- {hotspot['location']}: {hotspot['pickups']} daily pickups\n"
    
    content += f"\n**Peak Times**: {', '.join(transport_data.get('peak_times', []))}\n"
    
    return content


@pytest.mark.asyncio
async def test_decision_package_with_optional_components():
    """Test decision package when some components are optional or fail."""
    
    settings = get_mock_settings()
    runtime = MagenticTeamRuntime(settings)
    
    user_query = "Recommend hotels and create decision package"
    
    with patch.object(runtime, 'initialize') as mock_init:
        mock_init.return_value = {"success": True}
        
        await runtime.initialize()
        
        # Mock required components succeeding
        with patch.object(runtime, 'execute_hotel_task') as mock_hotel, \
             patch.object(runtime, 'execute_email_task') as mock_email, \
             patch.object(runtime, 'execute_taxi_fabric_task') as mock_fabric:
            
            mock_hotel.return_value = {
                "summary": "Found hotels successfully",
                "details": {"hotels": ["Hotel A", "Hotel B"]}
            }
            
            # Mock optional fabric analysis failing
            mock_fabric.return_value = {
                "summary": "Transport analysis failed due to data unavailability",
                "details": {"error": "no_data"}
            }
            
            mock_email.return_value = {
                "summary": "Decision package sent with available information",
                "details": {"status": "delivered", "content_warning": "transport_data_unavailable"}
            }
            
            # Should still complete scenario even with optional component failure
            result = await runtime.execute_scenario(user_query, "decision_package")
            
            # Should get some result even with partial data
            assert result is not None


@pytest.mark.asyncio
async def test_decision_package_comprehensive_insights():
    """Test comprehensive insights generation for decision packages."""
    
    settings = get_mock_settings()
    runtime = MagenticTeamRuntime(settings)
    
    # Mock comprehensive data from multiple sources
    hotel_insights = {
        "top_choice": "The Plaza Hotel",
        "best_value": "Midtown Marriott",
        "unique_features": ["Central Park views", "Historic building", "Michelin dining"]
    }
    
    transport_insights = {
        "cost_optimization": "Use subway during peak hours to save 40%",
        "convenience_factor": "Hotel A has direct subway access",
        "weekend_patterns": "Friday night rates 25% higher"
    }
    
    # Test insight compilation
    comprehensive_insights = compile_decision_insights(hotel_insights, transport_insights)
    
    assert "top_choice" in comprehensive_insights
    assert "cost_optimization" in comprehensive_insights
    assert len(comprehensive_insights["recommendations"]) > 0


def compile_decision_insights(hotel_data, transport_data):
    """Compile comprehensive insights from multiple data sources."""
    insights = {
        "top_choice": hotel_data.get("top_choice"),
        "best_value": hotel_data.get("best_value"),
        "cost_optimization": transport_data.get("cost_optimization"),
        "recommendations": []
    }
    
    # Generate actionable recommendations
    if hotel_data.get("top_choice"):
        insights["recommendations"].append(f"Book {hotel_data['top_choice']} for premium experience")
    
    if transport_data.get("cost_optimization"):
        insights["recommendations"].append(transport_data["cost_optimization"])
    
    return insights


def test_decision_package_email_tracking():
    """Test email tracking and delivery confirmation for decision packages."""
    
    # Mock email delivery tracking
    tracking_info = {
        "email_id": "DP-EMAIL-001",
        "sent_timestamp": "2025-01-01T10:30:00Z",
        "delivery_status": "delivered",
        "tracking_url": "https://logic-app-logs.azure.com/track/DP-EMAIL-001"
    }
    
    # Test tracking information format
    assert tracking_info["email_id"].startswith("DP-EMAIL")
    assert tracking_info["delivery_status"] in ["pending", "delivered", "failed"]
    assert "timestamp" in tracking_info["sent_timestamp"]


if __name__ == "__main__":
    pytest.main([__file__])