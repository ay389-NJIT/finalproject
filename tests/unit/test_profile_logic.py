"""
Unit Tests for Profile Management Logic

Tests the business logic for profile updates and password changes.
"""
import pytest
from pydantic import ValidationError
from app.schemas.user import UserUpdate, PasswordUpdate


class TestUserUpdateSchema:
    """Test UserUpdate schema validation"""
    
    def test_valid_partial_update(self):
        """Test updating only some fields"""
        data = {"first_name": "John"}
        user_update = UserUpdate(**data)
        assert user_update.first_name == "John"
        assert user_update.last_name is None
        assert user_update.email is None
        assert user_update.username is None
    
    def test_valid_full_update(self):
        """Test updating all fields"""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "username": "johndoe"
        }
        user_update = UserUpdate(**data)
        assert user_update.first_name == "John"
        assert user_update.last_name == "Doe"
        assert user_update.email == "john@example.com"
        assert user_update.username == "johndoe"
    
    def test_invalid_email(self):
        """Test invalid email format"""
        data = {"email": "not-an-email"}
        with pytest.raises(ValidationError):
            UserUpdate(**data)
    
    def test_username_too_short(self):
        """Test username minimum length validation"""
        data = {"username": "ab"}  # Less than 3 characters
        with pytest.raises(ValidationError):
            UserUpdate(**data)
    
    def test_empty_update(self):
        """Test that all fields can be None (optional partial update)"""
        data = {}
        user_update = UserUpdate(**data)
        assert user_update.first_name is None
        assert user_update.last_name is None


class TestPasswordUpdateSchema:
    """Test PasswordUpdate schema validation"""
    
    def test_valid_password_update(self):
        """Test valid password update"""
        data = {
            "current_password": "OldPass123",
            "new_password": "NewPass456",
            "confirm_new_password": "NewPass456"
        }
        password_update = PasswordUpdate(**data)
        assert password_update.current_password == "OldPass123"
        assert password_update.new_password == "NewPass456"
    
    def test_passwords_do_not_match(self):
        """Test password confirmation mismatch"""
        data = {
            "current_password": "OldPass123",
            "new_password": "NewPass456",
            "confirm_new_password": "DifferentPass789"
        }
        with pytest.raises(ValidationError) as exc_info:
            PasswordUpdate(**data)
        assert "do not match" in str(exc_info.value)
    
    def test_new_password_same_as_current(self):
        """Test new password cannot be same as current"""
        data = {
            "current_password": "SamePass123",
            "new_password": "SamePass123",
            "confirm_new_password": "SamePass123"
        }
        with pytest.raises(ValidationError) as exc_info:
            PasswordUpdate(**data)
        assert "must be different" in str(exc_info.value)
    
    def test_password_too_short(self):
        """Test password minimum length"""
        data = {
            "current_password": "OldPass123",
            "new_password": "short",
            "confirm_new_password": "short"
        }
        with pytest.raises(ValidationError):
            PasswordUpdate(**data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])