"""
Unit Tests for Square Root Operation

Tests the square root calculation logic in isolation.
"""
import pytest
from app.models.calculation import SquareRoot
import uuid


class TestSquareRootOperation:
    """Test the SquareRoot calculation class"""
    
    def test_sqrt_perfect_square(self):
        """Test square root of perfect square: √16 = 4"""
        calc = SquareRoot(
            user_id=uuid.uuid4(),
            inputs=[16]
        )
        assert calc.get_result() == 4.0
    
    def test_sqrt_another_perfect_square(self):
        """Test square root of another perfect square: √25 = 5"""
        calc = SquareRoot(
            user_id=uuid.uuid4(),
            inputs=[25]
        )
        assert calc.get_result() == 5.0
    
    def test_sqrt_non_perfect_square(self):
        """Test square root of non-perfect square: √2 ≈ 1.414"""
        calc = SquareRoot(
            user_id=uuid.uuid4(),
            inputs=[2]
        )
        result = calc.get_result()
        assert abs(result - 1.41421356) < 0.00001  # Close enough
    
    def test_sqrt_of_zero(self):
        """Test square root of zero: √0 = 0"""
        calc = SquareRoot(
            user_id=uuid.uuid4(),
            inputs=[0]
        )
        assert calc.get_result() == 0.0
    
    def test_sqrt_of_one(self):
        """Test square root of one: √1 = 1"""
        calc = SquareRoot(
            user_id=uuid.uuid4(),
            inputs=[1]
        )
        assert calc.get_result() == 1.0
    
    def test_sqrt_large_number(self):
        """Test square root of larger number: √100 = 10"""
        calc = SquareRoot(
            user_id=uuid.uuid4(),
            inputs=[100]
        )
        assert calc.get_result() == 10.0
    
    def test_sqrt_decimal(self):
        """Test square root of decimal: √6.25 = 2.5"""
        calc = SquareRoot(
            user_id=uuid.uuid4(),
            inputs=[6.25]
        )
        assert calc.get_result() == 2.5
    
    def test_sqrt_negative_number_raises_error(self):
        """Test that square root of negative number raises error"""
        calc = SquareRoot(
            user_id=uuid.uuid4(),
            inputs=[-4]
        )
        with pytest.raises(ValueError, match="negative number"):
            calc.get_result()
    
    def test_sqrt_requires_exactly_one_input(self):
        """Test that square root requires exactly 1 input"""
        calc = SquareRoot(
            user_id=uuid.uuid4(),
            inputs=[4, 9]  # Too many inputs
        )
        with pytest.raises(ValueError, match="exactly one number"):
            calc.get_result()
    
    def test_sqrt_requires_at_least_one_input(self):
        """Test that square root requires at least 1 input"""
        calc = SquareRoot(
            user_id=uuid.uuid4(),
            inputs=[]  # No inputs
        )
        with pytest.raises(ValueError, match="exactly one number"):
            calc.get_result()
    
    def test_sqrt_inputs_must_be_list(self):
        """Test that inputs must be a list"""
        calc = SquareRoot(
            user_id=uuid.uuid4(),
            inputs="not a list"
        )
        with pytest.raises(ValueError, match="must be a list"):
            calc.get_result()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])