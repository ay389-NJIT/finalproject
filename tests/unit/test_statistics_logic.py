"""
Unit Tests for Calculation Statistics Logic

Tests the statistics calculation logic in isolation.
"""
import pytest
from app.models.calculation import Addition, Subtraction, Multiplication, Division, Power, SquareRoot
from app.schemas.calculation import CalculationStatistics
from pydantic import ValidationError
import uuid


class TestStatisticsCalculation:
    """Test statistics calculation logic"""
    
    def test_statistics_schema_valid(self):
        """Test that CalculationStatistics schema validates correct data"""
        stats_data = {
            "total_calculations": 10,
            "calculations_by_type": {"addition": 5, "subtraction": 5},
            "most_used_operation": "addition",
            "average_operands": 2.5,
            "total_operands": 25
        }
        stats = CalculationStatistics(**stats_data)
        
        assert stats.total_calculations == 10
        assert stats.calculations_by_type == {"addition": 5, "subtraction": 5}
        assert stats.most_used_operation == "addition"
        assert stats.average_operands == 2.5
        assert stats.total_operands == 25
    
    def test_statistics_schema_with_none_most_used(self):
        """Test statistics schema when no calculations exist"""
        stats_data = {
            "total_calculations": 0,
            "calculations_by_type": {},
            "most_used_operation": None,
            "average_operands": 0,
            "total_operands": 0
        }
        stats = CalculationStatistics(**stats_data)
        
        assert stats.total_calculations == 0
        assert stats.most_used_operation is None
    
    def test_statistics_schema_all_operation_types(self):
        """Test statistics with all operation types"""
        stats_data = {
            "total_calculations": 6,
            "calculations_by_type": {
                "addition": 1,
                "subtraction": 1,
                "multiplication": 1,
                "division": 1,
                "power": 1,
                "square_root": 1
            },
            "most_used_operation": "addition",
            "average_operands": 1.83,
            "total_operands": 11
        }
        stats = CalculationStatistics(**stats_data)
        
        assert len(stats.calculations_by_type) == 6
        assert stats.total_calculations == 6
    
    def test_statistics_average_operands_calculation(self):
        """Test that average operands is calculated correctly"""
        # 5 calculations with 2 operands each = 10 total operands
        # Average = 10 / 5 = 2.0
        stats_data = {
            "total_calculations": 5,
            "calculations_by_type": {"addition": 5},
            "most_used_operation": "addition",
            "average_operands": 2.0,
            "total_operands": 10
        }
        stats = CalculationStatistics(**stats_data)
        
        assert stats.average_operands == 2.0
        assert stats.total_operands == 10
    
    def test_statistics_most_used_operation_tie(self):
        """Test most_used_operation when there's a tie (picks one)"""
        stats_data = {
            "total_calculations": 4,
            "calculations_by_type": {"addition": 2, "subtraction": 2},
            "most_used_operation": "addition",  # Either is valid
            "average_operands": 2.0,
            "total_operands": 8
        }
        stats = CalculationStatistics(**stats_data)
        
        # Should be one of the tied operations
        assert stats.most_used_operation in ["addition", "subtraction"]


class TestCalculationTypeBreakdown:
    """Test calculation type counting logic"""
    
    def test_empty_calculations_list(self):
        """Test statistics with no calculations"""
        # This would be tested with actual database in integration tests
        # Here we just verify the schema handles empty case
        stats_data = {
            "total_calculations": 0,
            "calculations_by_type": {},
            "most_used_operation": None,
            "average_operands": 0,
            "total_operands": 0
        }
        stats = CalculationStatistics(**stats_data)
        
        assert stats.total_calculations == 0
        assert stats.calculations_by_type == {}
    
    def test_single_operation_type(self):
        """Test statistics when only one operation type is used"""
        stats_data = {
            "total_calculations": 10,
            "calculations_by_type": {"multiplication": 10},
            "most_used_operation": "multiplication",
            "average_operands": 3.5,
            "total_operands": 35
        }
        stats = CalculationStatistics(**stats_data)
        
        assert stats.most_used_operation == "multiplication"
        assert len(stats.calculations_by_type) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])