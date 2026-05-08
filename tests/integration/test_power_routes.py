"""
Integration Tests for Power Operation API Routes

Tests power calculation endpoints with real database interactions.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.calculation import Calculation


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_power.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user_data():
    """Reusable test user data"""
    return {
        "first_name": "Power",
        "last_name": "Test",
        "email": "power@example.com",
        "username": "poweruser",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!"
    }


@pytest.fixture
def authenticated_user(test_user_data):
    """Create user and return authentication token"""
    # Register user
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 201
    
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
        "user_data": test_user_data
    }


class TestPowerCalculationAPI:
    """Test power operation through API endpoints"""
    
    def test_create_power_calculation_basic(self, authenticated_user):
        """Test creating a basic power calculation: 2^3 = 8"""
        calc_data = {
            "type": "power",
            "inputs": [2, 3]
        }
        
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["type"] == "power"
        assert data["inputs"] == [2, 3]
        assert data["result"] == 8.0
        assert "id" in data
        assert "created_at" in data
    
    def test_create_power_calculation_zero_exponent(self, authenticated_user):
        """Test power calculation with zero exponent: 5^0 = 1"""
        calc_data = {
            "type": "power",
            "inputs": [5, 0]
        }
        
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 1.0
    
    def test_create_power_calculation_negative_exponent(self, authenticated_user):
        """Test power calculation with negative exponent: 2^-2 = 0.25"""
        calc_data = {
            "type": "power",
            "inputs": [2, -2]
        }
        
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 0.25
    
    def test_create_power_calculation_fractional_exponent(self, authenticated_user):
        """Test power calculation with fractional exponent: 4^0.5 = 2"""
        calc_data = {
            "type": "power",
            "inputs": [4, 0.5]
        }
        
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 2.0
    
    def test_create_power_calculation_large_numbers(self, authenticated_user):
        """Test power calculation with larger numbers: 10^3 = 1000"""
        calc_data = {
            "type": "power",
            "inputs": [10, 3]
        }
        
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 1000.0
    
    def test_power_requires_exactly_two_inputs(self, authenticated_user):
        """Test that power operation requires exactly 2 inputs"""
        calc_data = {
            "type": "power",
            "inputs": [2, 3, 4]  # Too many inputs
        }
        
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422
        assert "exactly two numbers" in response.json()["detail"][0]["msg"].lower()
    
    def test_power_requires_minimum_inputs(self, authenticated_user):
        """Test that power operation rejects single input"""
        calc_data = {
            "type": "power",
            "inputs": [2]  # Only one input
        }
        
        response = client.post(
            "/calculations",
            json=calc_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422
        assert "exactly two numbers" in response.json()["detail"][0]["msg"].lower()
    
    def test_power_calculation_unauthenticated(self):
        """Test that power calculation requires authentication"""
        calc_data = {
            "type": "power",
            "inputs": [2, 3]
        }
        
        response = client.post("/calculations", json=calc_data)
        assert response.status_code == 401
    
    def test_power_calculation_persists_in_database(self, authenticated_user):
        """Test that power calculation is saved to database"""
        calc_data = {
            "type": "power",
            "inputs": [3, 4]
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
        assert data["type"] == "power"
        assert data["inputs"] == [3, 4]
        assert data["result"] == 81.0
    
    def test_power_calculation_appears_in_history(self, authenticated_user):
        """Test that power calculation appears in user's calculation history"""
        calc_data = {
            "type": "power",
            "inputs": [2, 8]
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
        
        # Find our power calculation
        power_calcs = [c for c in calculations if c["type"] == "power"]
        assert len(power_calcs) >= 1
        assert any(c["inputs"] == [2, 8] and c["result"] == 256.0 for c in power_calcs)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])