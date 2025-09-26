# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
End-to-end test for Travel Query + Notification scenario.
Tests the complete workflow: hotel search + taxi analysis + email notification.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from app.config.settings import get_mock_settings
from app.orchestrator.magentic_runtime import MagenticTeamRuntime


@pytest.mark.asyncio
async def test_travel_query_scenario_full_flow():
    """Test complete travel query scenario with all agents."""
    
    # Use mock settings for testing
    settings = get_mock_settings()
    runtime = MagenticTeamRuntime(settings)
    
    # Test query
    user_query = "Find NYC hotels with parking, analyze day/night taxi costs, and email me the summary"
    
    # Mock the initialize method to avoid external dependencies
    with patch.object(runtime, 'initialize') as mock_init:
        mock_init.return_value = {"success": True, "agents_status": {}}
        
        # Initialize runtime  
        result = await runtime.initialize()
        assert result["success"] is True
        
        # Mock individual agent responses
        with patch.object(runtime, 'execute_hotel_task') as mock_hotel, \
             patch.object(runtime, 'execute_taxi_fabric_task') as mock_fabric, \
             patch.object(runtime, 'execute_taxi_genie_task') as mock_genie, \
             patch.object(runtime, 'execute_email_task') as mock_email:
            
            mock_hotel.return_value = {
                "summary": "Found 3 hotels with parking: Grand Central (4.8⭐), Brooklyn Heights (4.5⭐), Queens Plaza (4.3⭐)",
                "details": {"hotels": ["Grand Central Hotel", "Brooklyn Heights Inn", "Queens Plaza Hotel"]}
            }
            
            mock_fabric.return_value = {
                "summary": "Day trips: 743K ($16.85 avg), Night trips: 504K ($21.40 avg). Night fares 27% higher.",
                "details": {"day_fare": 16.85, "night_fare": 21.40, "difference": 0.27}
            }
            
            mock_genie.return_value = {
                "summary": "Analysis confirmed: avg fare $18.32, peak hours 8-9 AM and 5-7 PM",
                "details": {"avg_fare": 18.32, "peak_hours": ["8-9 AM", "5-7 PM"]}
            }
            
            mock_email.return_value = {
                "summary": "Email sent successfully to user@example.com",
                "details": {"status": "delivered", "tracking_id": "LA-EMAIL-001"}
            }
            
            # Execute scenario
            scenario_result = await runtime.execute_scenario(user_query, "travel_query")
            
            # Verify execution
            assert scenario_result.get("scenario_type") == "travel_query"
            
            # Verify all agents were called
            mock_hotel.assert_called()
            mock_fabric.assert_called()
            mock_genie.assert_called() 
            mock_email.assert_called()


@pytest.mark.asyncio  
async def test_travel_query_scenario_partial_failure():
    """Test scenario handling when one agent fails."""
    
    settings = get_mock_settings()
    runtime = MagenticTeamRuntime(settings)
    
    user_query = "Find hotels and analyze taxi costs"
    
    # Mock initialization
    with patch.object(runtime, 'initialize') as mock_init:
        mock_init.return_value = {"success": True}
        
        await runtime.initialize()
        
        # Mock one agent failure
        with patch.object(runtime, 'execute_hotel_task') as mock_hotel, \
             patch.object(runtime, 'execute_taxi_fabric_task') as mock_fabric:
            
            mock_hotel.return_value = {
                "summary": "Found 2 hotels with parking",
                "details": {"hotels": ["Hotel A", "Hotel B"]}
            }
            
            # Simulate fabric agent failure
            mock_fabric.return_value = {
                "summary": "Taxi analysis failed: Connection timeout",
                "details": {"error": "timeout"}
            }
            
            # Scenario should handle partial failure gracefully
            result = await runtime.execute_scenario(user_query, "travel_query")
            
            # Should still return some results even with partial failure
            assert result is not None


@pytest.mark.asyncio
async def test_travel_query_with_data_fusion():
    """Test data fusion when both taxi agents provide conflicting data."""
    
    settings = get_mock_settings()
    runtime = MagenticTeamRuntime(settings)
    
    # Mock conflicting taxi data
    fabric_data = {"avg_fare": 16.85, "trip_count": 100000}
    genie_data = {"avg_fare": 18.32, "trip_count": 95000}
    
    # Test conflict resolution
    result = runtime.resolve_conflicts(str(fabric_data), str(genie_data))
    
    assert result["summary"] is not None
    assert "conflict" in result["summary"] or "Resolved" in result["summary"]
    assert result["details"] is not None


def test_scenario_type_detection():
    """Test automatic scenario type detection from user queries."""
    
    settings = get_mock_settings()
    runtime = MagenticTeamRuntime(settings)
    
    # Test travel query detection
    travel_query = "Find hotels and analyze taxi costs and email summary"
    scenario_type = runtime._detect_scenario_type(travel_query)
    assert scenario_type == "travel_query"
    
    # Test consistency check detection  
    consistency_query = "Compare fabric and genie data for consistency check"
    scenario_type = runtime._detect_scenario_type(consistency_query)
    assert scenario_type == "data_consistency"
    
    # Test decision package detection
    decision_query = "Recommend hotels with comprehensive insights and decision package"
    scenario_type = runtime._detect_scenario_type(decision_query)
    assert scenario_type == "decision_package"


def test_agent_status_monitoring():
    """Test agent status and health monitoring."""
    
    settings = get_mock_settings()
    runtime = MagenticTeamRuntime(settings)
    
    # Get team status
    status = runtime.get_team_status()
    
    assert "hotel_agent" in status
    assert "taxi_fabric_agent" in status
    assert "taxi_genie_agent" in status
    assert "email_agent" in status
    assert "orchestration_ready" in status
    assert "runtime_active" in status


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__])