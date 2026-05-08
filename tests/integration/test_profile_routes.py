"""
Integration Tests for Profile Management API Routes

Tests profile endpoints using shared database fixtures from conftest.py.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.fixture
def test_user_data():
    """Reusable test user data"""
    return {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!"
    }


@pytest.fixture
def authenticated_user(db_session, test_user_data):
    """Create user and return authentication token"""
    from app.models.user import User
    
    # Register user using User.register (same pattern as original tests)
    user = User.register(db_session, test_user_data)
    db_session.commit()
    
    # Login to get token
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
        "original_data": test_user_data,
        "user": user
    }


class TestGetProfile:
    """Test GET /api/profile endpoint"""
    
    def test_get_profile_success(self, db_session, authenticated_user):
        """Test retrieving user profile"""
        response = client.get("/api/profile", headers=authenticated_user["headers"])
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all expected fields are present
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "is_active" in data
        assert "is_verified" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        # Verify data matches registration
        assert data["username"] == authenticated_user["original_data"]["username"]
        assert data["email"] == authenticated_user["original_data"]["email"]
        assert data["first_name"] == authenticated_user["original_data"]["first_name"]
    
    def test_get_profile_unauthenticated(self, db_session):
        """Test profile access without authentication"""
        response = client.get("/api/profile")
        assert response.status_code == 401
    
    def test_get_profile_invalid_token(self, db_session):
        """Test profile access with invalid token"""
        headers = {"Authorization": "Bearer invalid_token_12345"}
        response = client.get("/api/profile", headers=headers)
        assert response.status_code == 401


class TestUpdateProfile:
    """Test PUT /api/profile endpoint"""
    
    def test_update_first_name_only(self, db_session, authenticated_user):
        """Test partial update - first name only"""
        update_data = {"first_name": "Updated"}
        response = client.put(
            "/api/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == authenticated_user["original_data"]["last_name"]
    
    def test_update_multiple_fields(self, db_session, authenticated_user):
        """Test updating multiple fields at once"""
        update_data = {
            "first_name": "NewFirst",
            "last_name": "NewLast",
            "email": "newemail@example.com"
        }
        response = client.put(
            "/api/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "NewFirst"
        assert data["last_name"] == "NewLast"
        assert data["email"] == "newemail@example.com"
    
    def test_update_email_duplicate(self, db_session, authenticated_user):
        """Test updating to an email that already exists"""
        from app.models.user import User
        
        # Create second user
        second_user_data = {
            "first_name": "Second",
            "last_name": "User",
            "email": "second@example.com",
            "username": "seconduser",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!"
        }
        User.register(db_session, second_user_data)
        db_session.commit()
        
        # Try to update first user's email to second user's email
        update_data = {"email": "second@example.com"}
        response = client.put(
            "/api/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_update_username_duplicate(self, db_session, authenticated_user):
        """Test updating to a username that already exists"""
        from app.models.user import User
        
        # Create second user
        second_user_data = {
            "first_name": "Second",
            "last_name": "User",
            "email": "second@example.com",
            "username": "seconduser",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!"
        }
        User.register(db_session, second_user_data)
        db_session.commit()
        
        # Try to update first user's username to second user's username
        update_data = {"username": "seconduser"}
        response = client.put(
            "/api/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 400
        assert "already taken" in response.json()["detail"].lower()
    
    def test_update_profile_invalid_email(self, db_session, authenticated_user):
        """Test updating with invalid email format"""
        update_data = {"email": "not-a-valid-email"}
        response = client.put(
            "/api/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_update_profile_unauthenticated(self, db_session):
        """Test profile update without authentication"""
        update_data = {"first_name": "Hacker"}
        response = client.put("/api/profile", json=update_data)
        assert response.status_code == 401
    
    def test_update_same_email_allowed(self, db_session, authenticated_user):
        """Test that updating to same email doesn't fail"""
        # Get current email
        current_email = authenticated_user["original_data"]["email"]
        
        update_data = {"email": current_email}
        response = client.put(
            "/api/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        # Should succeed - user can "update" to their own email
        assert response.status_code == 200
    
    def test_update_profile_updated_at_timestamp(self, db_session, authenticated_user):
        """Test that updated_at timestamp changes after update"""
        # Get original timestamp
        response = client.get("/api/profile", headers=authenticated_user["headers"])
        original_updated_at = response.json()["updated_at"]
        
        # Update profile
        update_data = {"first_name": "Changed"}
        response = client.put(
            "/api/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        # Verify timestamp changed
        new_updated_at = response.json()["updated_at"]
        assert new_updated_at != original_updated_at


class TestUpdatePassword:
    """Test PUT /api/profile/password endpoint"""
    
    def test_password_change_success(self, db_session, authenticated_user):
        """Test successful password change"""
        password_data = {
            "current_password": "TestPass123!",
            "new_password": "NewPass456!",
            "confirm_new_password": "NewPass456!"
        }
        response = client.put(
            "/api/profile/password",
            json=password_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        assert "successfully" in response.json()["message"].lower()
    
    def test_password_change_wrong_current(self, db_session, authenticated_user):
        """Test password change with incorrect current password"""
        password_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewPass456!",
            "confirm_new_password": "NewPass456!"
        }
        response = client.put(
            "/api/profile/password",
            json=password_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 400
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_password_change_mismatch(self, db_session, authenticated_user):
        """Test password change with mismatched new passwords"""
        password_data = {
            "current_password": "TestPass123!",
            "new_password": "NewPass456!",
            "confirm_new_password": "DifferentPass789!"
        }
        response = client.put(
            "/api/profile/password",
            json=password_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_password_change_same_as_current(self, db_session, authenticated_user):
        """Test that new password cannot be same as current"""
        password_data = {
            "current_password": "TestPass123!",
            "new_password": "TestPass123!",
            "confirm_new_password": "TestPass123!"
        }
        response = client.put(
            "/api/profile/password",
            json=password_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_password_change_then_login(self, db_session, authenticated_user, test_user_data):
        """Test that new password works for login after change"""
        # Change password
        new_password = "BrandNewPass789!"
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": new_password,
            "confirm_new_password": new_password
        }
        response = client.put(
            "/api/profile/password",
            json=password_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        
        # Try logging in with old password - should fail
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        
        # Try logging in with new password - should succeed
        login_data["password"] = new_password
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_password_change_unauthenticated(self, db_session):
        """Test password change without authentication"""
        password_data = {
            "current_password": "TestPass123!",
            "new_password": "NewPass456!",
            "confirm_new_password": "NewPass456!"
        }
        response = client.put("/api/profile/password", json=password_data)
        assert response.status_code == 401


class TestProfileUpdatePersistence:
    """Test that profile updates persist correctly in database"""
    
    def test_profile_update_persists_after_relogin(self, db_session, authenticated_user, test_user_data):
        """Test that profile changes persist after logging out and back in"""
        # Update profile
        update_data = {"first_name": "Persistent", "last_name": "Update"}
        response = client.put(
            "/api/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        
        # Login again with new token
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = client.post("/auth/login", json=login_data)
        new_token = response.json()["access_token"]
        
        # Get profile with new token
        response = client.get("/api/profile", headers={"Authorization": f"Bearer {new_token}"})
        data = response.json()
        
        # Verify updates persisted
        assert data["first_name"] == "Persistent"
        assert data["last_name"] == "Update"
    
    def test_username_update_affects_login(self, db_session, authenticated_user, test_user_data):
        """Test that username change requires login with new username"""
        # Update username
        new_username = "newusername123"
        update_data = {"username": new_username}
        response = client.put(
            "/api/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        
        # Try login with old username - should fail
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        
        # Login with new username - should succeed
        login_data["username"] = new_username
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200


class TestConcurrentUserScenarios:
    """Test scenarios with multiple users"""
    
    def test_two_users_cannot_have_same_email(self, db_session, authenticated_user):
        """Test that two users cannot update to the same email"""
        from app.models.user import User
        
        # Create second user
        second_user_data = {
            "first_name": "Second",
            "last_name": "User",
            "email": "second@example.com",
            "username": "seconduser",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!"
        }
        second_user = User.register(db_session, second_user_data)
        db_session.commit()
        
        # Login as second user
        login_data = {
            "username": second_user_data["username"],
            "password": second_user_data["password"]
        }
        response = client.post("/auth/login", json=login_data)
        second_token = response.json()["access_token"]
        second_headers = {"Authorization": f"Bearer {second_token}"}
        
        # Try to update second user's email to first user's email
        update_data = {"email": authenticated_user["original_data"]["email"]}
        response = client.put("/api/profile", json=update_data, headers=second_headers)
        
        # Should fail
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])