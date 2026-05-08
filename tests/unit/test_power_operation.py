"""
Unit Tests for Power Operation

Tests the power calculation logic in isolation.
"""
import pytest
from app.models.calculation import Power
import uuid


class TestPowerOperation:
    """Test the Power calculation class"""
    
    def test_power_basic(self):
        """Test basic exponentiation: 2^3 = 8"""
        calc = Power(
            user_id=uuid.uuid4(),
            inputs=[2, 3]
        )
        assert calc.get_result() == 8
    
    def test_power_zero_exponent(self):
        """Test anything to the power of 0 equals 1"""
        calc = Power(
            user_id=uuid.uuid4(),
            inputs=[5, 0]
        )
        assert calc.get_result() == 1
    
    def test_power_negative_exponent(self):
        """Test negative exponent: 2^(-2) = 0.25"""
        calc = Power(
            user_id=uuid.uuid4(),
            inputs=[2, -2]
        )
        assert calc.get_result() == 0.25
    
    def test_power_fractional_exponent(self):
        """Test fractional exponent (square root): 4^0.5 = 2"""
        calc = Power(
            user_id=uuid.uuid4(),
            inputs=[4, 0.5]
        )
        assert calc.get_result() == 2.0
    
    def test_power_large_numbers(self):
        """Test with larger numbers: 10^3 = 1000"""
        calc = Power(
            user_id=uuid.uuid4(),
            inputs=[10, 3]
        )
        assert calc.get_result() == 1000
    
    def test_power_requires_exactly_two_inputs(self):
        """Test that power operation requires exactly 2 inputs"""
        calc = Power(
            user_id=uuid.uuid4(),
            inputs=[2, 3, 4]  # Too many inputs
        )
        with pytest.raises(ValueError, match="exactly two numbers"):
            calc.get_result()
    
    def test_power_requires_at_least_two_inputs(self):
        """Test that power operation requires at least 2 inputs"""
        calc = Power(
            user_id=uuid.uuid4(),
            inputs=[2]  # Only one input
        )
        with pytest.raises(ValueError, match="exactly two numbers"):
            calc.get_result()
    
    def test_power_inputs_must_be_list(self):
        """Test that inputs must be a list"""
        calc = Power(
            user_id=uuid.uuid4(),
            inputs="not a list"
        )
        with pytest.raises(ValueError, match="must be a list"):
            calc.get_result()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])