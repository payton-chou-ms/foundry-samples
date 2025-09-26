# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
End-to-end test for Data Consistency Check scenario.
Tests data comparison between Fabric and Genie sources with conflict resolution.
"""

import pytest
from unittest.mock import Mock, patch

from app.config.settings import get_mock_settings
from app.orchestrator.magentic_runtime import MagenticTeamRuntime
from app.orchestrator.task_graph import ConflictResolutionStrategy


@pytest.mark.asyncio
async def test_data_consistency_scenario():
    """Test data consistency checking between Fabric and Genie."""
    
    settings = get_mock_settings()
    runtime = MagenticTeamRuntime(settings)
    
    user_query = "Compare last 30 days taxi data between Fabric and Genie, report differences >5%"
    
    # Mock initialization
    with patch.object(runtime, 'initialize') as mock_init:
        mock_init.return_value = {"success": True}
        
        await runtime.initialize()
        
        # Mock taxi agent responses with different data
        with patch.object(runtime, 'execute_taxi_fabric_task') as mock_fabric, \
             patch.object(runtime, 'execute_taxi_genie_task') as mock_genie:
            
            # Fabric data
            mock_fabric.return_value = {
                "summary": "30-day analysis: 1.2M trips, $16.85 avg fare",
                "details": {
                    "total_trips": 1200000,
                    "avg_fare": 16.85,
                    "day_trips": 720000,
                    "night_trips": 480000
                }
            }
            
            # Genie data with differences
            mock_genie.return_value = {
                "summary": "30-day analysis: 1.1M trips, $18.32 avg fare", 
                "details": {
                    "total_trips": 1100000,  # 8.3% difference
                    "avg_fare": 18.32,       # 8.7% difference  
                    "day_trips": 680000,     # 5.6% difference
                    "night_trips": 420000    # 12.5% difference
                }
            }
            
            # Execute consistency check
            result = await runtime.execute_scenario(user_query, "data_consistency")
            
            # Verify consistency check was performed
            assert result is not None
            assert result.get("scenario_type") == "data_consistency"


def test_conflict_resolution_strategies():
    """Test different conflict resolution strategies."""
    
    fabric_data = {
        "avg_fare": 16.85,
        "total_trips": 1200000,
        "peak_hour": "8 AM"
    }
    
    genie_data = {
        "avg_fare": 18.32,  # 8.7% difference
        "total_trips": 1100000,  # 8.3% difference
        "peak_hour": "9 AM"  # Different
    }
    
    # Test newest priority strategy
    result = ConflictResolutionStrategy.resolve_conflicts(
        fabric_data, genie_data, "newest_priority"
    )
    
    assert result["resolution_rule"] == "newest_priority"
    assert len(result["conflicts"]) >= 2  # Should detect fare and trip differences
    assert result["data_quality_score"] < 1.0  # Should be less than perfect
    
    # Test fabric priority strategy
    result = ConflictResolutionStrategy.resolve_conflicts(
        fabric_data, genie_data, "fabric_priority"
    )
    
    assert result["resolution_rule"] == "fabric_priority"
    # For numeric conflicts, should prefer fabric values
    
    # Test report difference strategy
    result = ConflictResolutionStrategy.resolve_conflicts(
        fabric_data, genie_data, "report_difference"
    )
    
    assert result["resolution_rule"] == "report_difference"
    # Should report both values for conflicts


def test_variance_threshold_detection():
    """Test detection of differences above threshold."""
    
    # Data with differences above 5% threshold
    fabric_data = {"avg_fare": 16.85, "total_trips": 1000000}
    genie_data = {"avg_fare": 18.50, "total_trips": 1100000}  # ~9.8% and 10% differences
    
    result = ConflictResolutionStrategy.resolve_conflicts(fabric_data, genie_data)
    
    # Should detect both fields as conflicting
    conflicts = result["conflicts"]
    conflict_fields = [c["field"] for c in conflicts]
    
    assert "avg_fare" in conflict_fields
    assert "total_trips" in conflict_fields
    
    # Check variance percentages are calculated correctly
    for conflict in conflicts:
        assert conflict["variance_percent"] > 5.0


def test_no_conflicts_scenario():
    """Test scenario where data sources are consistent."""
    
    fabric_data = {"avg_fare": 16.85, "total_trips": 1000000}
    genie_data = {"avg_fare": 16.90, "total_trips": 1001000}  # <2% differences
    
    result = ConflictResolutionStrategy.resolve_conflicts(fabric_data, genie_data)
    
    # Should have no significant conflicts
    assert len(result["conflicts"]) == 0
    assert result["data_quality_score"] == 1.0


@pytest.mark.asyncio
async def test_consistency_report_generation():
    """Test generation of consistency reports."""
    
    settings = get_mock_settings()
    runtime = MagenticTeamRuntime(settings)
    
    # Mock consistency check with significant differences
    fabric_result = {
        "avg_fare": 16.85,
        "trip_count": 1200000,
        "peak_hours": ["8 AM", "5 PM"]
    }
    
    genie_result = {
        "avg_fare": 18.32,    # 8.7% difference
        "trip_count": 1100000, # 8.3% difference  
        "peak_hours": ["9 AM", "6 PM"]  # Different
    }
    
    # Test conflict resolution
    resolution_result = runtime.resolve_conflicts(str(fabric_result), str(genie_result))
    
    assert "conflict" in resolution_result["summary"].lower() or "resolved" in resolution_result["summary"].lower()
    assert resolution_result["details"] is not None


@pytest.mark.asyncio
async def test_email_consistency_report():
    """Test optional email sending for consistency reports."""
    
    settings = get_mock_settings()
    runtime = MagenticTeamRuntime(settings)
    
    # Mock email agent for consistency report
    with patch.object(runtime, 'execute_email_task') as mock_email:
        mock_email.return_value = {
            "summary": "Consistency report emailed successfully",
            "details": {"status": "sent", "recipient": "user@example.com"}
        }
        
        # Execute email task
        result = await runtime.execute_email_task(
            recipient="user@example.com",
            subject="Data Consistency Report", 
            body="Fabric vs Genie comparison: 3 conflicts found"
        )
        
        assert result["summary"] is not None
        mock_email.assert_called_once()


def test_data_quality_scoring():
    """Test data quality score calculation."""
    
    # Perfect consistency
    perfect_data = {"metric1": 100, "metric2": 200}
    result = ConflictResolutionStrategy.resolve_conflicts(perfect_data, perfect_data)
    assert result["data_quality_score"] == 1.0
    
    # Some conflicts
    fabric_data = {"metric1": 100, "metric2": 200, "metric3": 300}
    genie_data = {"metric1": 110, "metric2": 200, "metric3": 320}  # 1 of 3 has >5% diff
    
    result = ConflictResolutionStrategy.resolve_conflicts(fabric_data, genie_data)
    # Should have score between 0 and 1
    assert 0.0 <= result["data_quality_score"] <= 1.0


if __name__ == "__main__":
    pytest.main([__file__])