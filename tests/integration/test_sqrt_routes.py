"""
Integration Tests for Square Root Operation API Routes

Tests square root calculation endpoints using shared database fixtures from conftest.py.
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
        "first_name": "Sqrt",
        "last_name": "Test",
        "email": f"sqrt_{unique_id}@example.com",
        "username": f"sqrtuser_{unique_id}",
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


class TestSquareRootCalculationAPI:
    """Test square root operation through API endpoints"""
    
    def test_create_sqrt_calculation_perfect_square(self, db_session, authenticated_user):
        """Test creating square root calculation: √16 = 4"""
        calc_data = {
            "type": "square_root",
            "inputs": [16]
        }
        
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["type"] == "square_root"
        assert data["inputs"] == [16]
        assert data["result"] == 4.0
        assert "id" in data
        assert "created_at" in data
    
    def test_create_sqrt_calculation_another_perfect_square(self, db_session, authenticated_user):
        """Test square root calculation: √25 = 5"""
        calc_data = {
            "type": "square_root",
            "inputs": [25]
        }
        
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 5.0
    
    def test_create_sqrt_calculation_non_perfect_square(self, db_session, authenticated_user):
        """Test square root calculation: √2 ≈ 1.414"""
        calc_data = {
            "type": "square_root",
            "inputs": [2]
        }
        
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 201
        data = response.json()
        result = data["result"]
        assert abs(result - 1.41421356) < 0.00001
    
    def test_create_sqrt_calculation_zero(self, db_session, authenticated_user):
        """Test square root of zero: √0 = 0"""
        calc_data = {
            "type": "square_root",
            "inputs": [0]
        }
        
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 0.0
    
    def test_create_sqrt_calculation_decimal(self, db_session, authenticated_user):
        """Test square root of decimal: √6.25 = 2.5"""
        calc_data = {
            "type": "square_root",
            "inputs": [6.25]
        }
        
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 2.5
    
    def test_sqrt_negative_number_error(self, db_session, authenticated_user):
        """Test that square root of negative number returns error"""
        calc_data = {
            "type": "square_root",
            "inputs": [-4]
        }
        
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 400
        assert "negative" in response.json()["detail"].lower()
    
    def test_sqrt_requires_exactly_one_input(self, db_session, authenticated_user):
        """Test that square root requires exactly 1 input"""
        calc_data = {
            "type": "square_root",
            "inputs": [4, 9]  # Too many inputs
        }
        
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422
        assert "exactly one number" in response.json()["detail"][0]["msg"].lower()
    
    def test_sqrt_requires_minimum_inputs(self, db_session, authenticated_user):
        """Test that square root rejects empty input"""
        calc_data = {
            "type": "square_root",
            "inputs": []  # No inputs
        }
        
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422
    
    def test_sqrt_calculation_unauthenticated(self, db_session):
        """Test that square root calculation requires authentication"""
        calc_data = {
            "type": "square_root",
            "inputs": [16]
        }
        
        response = client.post("/calculations", json=calc_data)
        assert response.status_code == 401
    
    def test_sqrt_calculation_persists_in_database(self, db_session, authenticated_user):
        """Test that square root calculation is saved to database"""
        calc_data = {
            "type": "square_root",
            "inputs": [49]
        }
        
        # Create calculation
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201
        calc_id = response.json()["id"]
        
        # Retrieve calculation
        response = client.get(
            f"/calculations/{calc_id}",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "square_root"
        assert data["inputs"] == [49]
        assert data["result"] == 7.0
    
    def test_sqrt_calculation_appears_in_history(self, db_session, authenticated_user):
        """Test that square root calculation appears in user's calculation history"""
        calc_data = {
            "type": "square_root",
            "inputs": [36]
        }
        
        # Create calculation
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201
        
        # Get all calculations
        response = client.get(
            "/calculations",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        calculations = response.json()
        
        # Find our sqrt calculation
        sqrt_calcs = [c for c in calculations if c["type"] == "square_root"]
        assert len(sqrt_calcs) >= 1
        assert any(c["inputs"] == [36] and c["result"] == 6.0 for c in sqrt_calcs)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])