"""
Integration Tests for Statistics API Routes

Tests statistics endpoint using shared database fixtures from conftest.py.
Follows the same pattern as the original test files.
"""
import pytest
import uuid
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.fixture
def test_user_data():
    """Reusable test user data with unique email/username"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "first_name": "Stats",
        "last_name": "Test",
        "email": f"stats_{unique_id}@example.com",
        "username": f"statsuser_{unique_id}",
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
        "user_data": test_user_data,
        "user": user
    }


class TestStatisticsAPI:
    """Test statistics endpoint"""
    
    def test_get_statistics_no_calculations(self, db_session, authenticated_user):
        """Test statistics when user has no calculations"""
        response = client.get(
            "/api/stats",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_calculations"] == 0
        assert data["calculations_by_type"] == {}
        assert data["most_used_operation"] is None
        assert data["average_operands"] == 0
        assert data["total_operands"] == 0
    
    def test_get_statistics_with_single_calculation(self, db_session, authenticated_user):
        """Test statistics after creating one calculation"""
        # Create a calculation
        calc_data = {"type": "addition", "inputs": [5, 3]}
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201
        
        # Get statistics
        response = client.get(
            "/api/stats",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_calculations"] == 1
        assert data["calculations_by_type"]["addition"] == 1
        assert data["most_used_operation"] == "addition"
        assert data["total_operands"] == 2
        assert data["average_operands"] == 2.0
    
    def test_get_statistics_with_multiple_calculations(self, db_session, authenticated_user):
        """Test statistics with multiple calculations of different types"""
        # Create multiple calculations
        calculations = [
            {"type": "addition", "inputs": [1, 2]},
            {"type": "addition", "inputs": [3, 4]},
            {"type": "subtraction", "inputs": [10, 5]},
            {"type": "multiplication", "inputs": [2, 3]},
            {"type": "division", "inputs": [10, 2]},
        ]
        
        for calc_data in calculations:
            response = client.post(
                "/calculations",
                json=calc_data,
                headers=authenticated_user["headers"]
            )
            assert response.status_code == 201
        
        # Get statistics
        response = client.get(
            "/api/stats",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_calculations"] == 5
        assert data["calculations_by_type"]["addition"] == 2
        assert data["calculations_by_type"]["subtraction"] == 1
        assert data["calculations_by_type"]["multiplication"] == 1
        assert data["calculations_by_type"]["division"] == 1
        assert data["most_used_operation"] == "addition"
        assert data["total_operands"] == 10
        assert data["average_operands"] == 2.0
    
    def test_get_statistics_with_all_operation_types(self, db_session, authenticated_user):
        """Test statistics with all 6 operation types"""
        calculations = [
            {"type": "addition", "inputs": [1, 2]},
            {"type": "subtraction", "inputs": [5, 3]},
            {"type": "multiplication", "inputs": [2, 4]},
            {"type": "division", "inputs": [10, 2]},
            {"type": "power", "inputs": [2, 3]},
            {"type": "square_root", "inputs": [16]},
        ]
        
        for calc_data in calculations:
            response = client.post(
                "/calculations",
                json=calc_data,
                headers=authenticated_user["headers"]
            )
            assert response.status_code == 201
        
        # Get statistics
        response = client.get(
            "/api/stats",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_calculations"] == 6
        assert len(data["calculations_by_type"]) == 6
        assert "square_root" in data["calculations_by_type"]
        assert "power" in data["calculations_by_type"]
        # Total operands: 2+2+2+2+2+1 = 11
        assert data["total_operands"] == 11
    
    def test_get_statistics_variable_operands(self, db_session, authenticated_user):
        """Test statistics with calculations having different numbers of operands"""
        calculations = [
            {"type": "addition", "inputs": [1, 2, 3]},  # 3 operands
            {"type": "multiplication", "inputs": [2, 3, 4, 5]},  # 4 operands
            {"type": "square_root", "inputs": [9]},  # 1 operand
        ]
        
        for calc_data in calculations:
            response = client.post(
                "/calculations",
                json=calc_data,
                headers=authenticated_user["headers"]
            )
            assert response.status_code == 201
        
        # Get statistics
        response = client.get(
            "/api/stats",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_calculations"] == 3
        # Total operands: 3 + 4 + 1 = 8
        assert data["total_operands"] == 8
        # Average: 8 / 3 ≈ 2.67
        assert abs(data["average_operands"] - 2.67) < 0.01
    
    def test_statistics_unauthenticated(self, db_session):
        """Test that statistics endpoint requires authentication"""
        response = client.get("/api/stats")
        assert response.status_code == 401
    
    def test_statistics_isolated_per_user(self, db_session):
        """Test that statistics are isolated per user"""
        from app.models.user import User
        
        # Create first user with unique credentials
        unique_id1 = str(uuid.uuid4())[:8]
        user1_data = {
            "first_name": "User",
            "last_name": "One",
            "email": f"user1_{unique_id1}@example.com",
            "username": f"user1_{unique_id1}",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!"
        }
        user1 = User.register(db_session, user1_data)
        db_session.commit()
        
        # Login user 1
        response = client.post("/auth/login", json={
            "username": f"user1_{unique_id1}",
            "password": "TestPass123!"
        })
        user1_token = response.json()["access_token"]
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        
        # User 1 creates 3 calculations
        for _ in range(3):
            client.post(
                "/calculations",
                json={"type": "addition", "inputs": [1, 2]},
                headers=user1_headers
            )
        
        # Create second user with unique credentials
        unique_id2 = str(uuid.uuid4())[:8]
        user2_data = {
            "first_name": "User",
            "last_name": "Two",
            "email": f"user2_{unique_id2}@example.com",
            "username": f"user2_{unique_id2}",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!"
        }
        user2 = User.register(db_session, user2_data)
        db_session.commit()
        
        # Login user 2
        response = client.post("/auth/login", json={
            "username": f"user2_{unique_id2}",
            "password": "TestPass123!"
        })
        user2_token = response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # User 2 creates 1 calculation
        client.post(
            "/calculations",
            json={"type": "subtraction", "inputs": [5, 3]},
            headers=user2_headers
        )
        
        # Check User 1 stats
        response = client.get("/api/stats", headers=user1_headers)
        user1_stats = response.json()
        assert user1_stats["total_calculations"] == 3
        
        # Check User 2 stats
        response = client.get("/api/stats", headers=user2_headers)
        user2_stats = response.json()
        assert user2_stats["total_calculations"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])