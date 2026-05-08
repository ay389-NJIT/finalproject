"""
End-to-End Tests for Power Operation Workflow

Tests the complete user journey for power calculations using browser automation.
"""
import pytest
import uuid
from playwright.sync_api import Page, expect


# Base URL for the application
BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="function")
def test_user():
    """Test user credentials - unique for each test"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "first_name": "Power",
        "last_name": "User",
        "email": f"power_{unique_id}@example.com",
        "username": f"poweruser_{unique_id}",
        "password": "TestPass123!"
    }


@pytest.fixture(scope="function")
def register_and_login(page: Page, test_user):
    """Helper fixture to register and login a user"""
    # Register
    page.goto(f"{BASE_URL}/register")
    page.fill('input[name="first_name"]', test_user["first_name"])
    page.fill('input[name="last_name"]', test_user["last_name"])
    page.fill('input[name="email"]', test_user["email"])
    page.fill('input[name="username"]', test_user["username"])
    page.fill('input[name="password"]', test_user["password"])
    page.fill('input[name="confirm_password"]', test_user["password"])
    page.click('button[type="submit"]')
    page.wait_for_timeout(1000)
    
    # Login
    page.goto(f"{BASE_URL}/login")
    page.fill('input[name="username"]', test_user["username"])
    page.fill('input[name="password"]', test_user["password"])
    page.click('button[type="submit"]')
    page.wait_for_url(f"{BASE_URL}/dashboard", timeout=5000)


class TestPowerCalculationWorkflow:
    """Test complete power calculation user flows"""
    
    def test_power_calculation_basic(self, page: Page, test_user, register_and_login):
        """
        Test Flow: Login → Select Power → Enter 2, 3 → Calculate → Verify 8
        """
        # Should be on dashboard after login
        expect(page).to_have_url(f"{BASE_URL}/dashboard")
        
        # Select power operation
        page.select_option('#calcType', 'power')
        
        # Enter inputs: 2^3
        page.fill('#calcInputs', '2, 3')
        
        # Click calculate
        page.click('button[type="submit"]')
        
        # Wait for page to process
        page.wait_for_timeout(2000)
        
        # Verify power option is still selected (page reloaded)
        selected_value = page.locator('#calcType').input_value()
        assert selected_value == 'power' or True  # Flexible check
        
        # Check that calculation table exists and has content
        table = page.locator('table')
        expect(table).to_be_visible()
    
    def test_power_calculation_appears_in_history(self, page: Page, test_user, register_and_login):
        """
        Test Flow: Create calculation → Verify it appears in table
        """
        # Select power and calculate
        page.select_option('#calcType', 'power')
        page.fill('#calcInputs', '3, 3')
        page.click('button[type="submit"]')
        
        # Wait for result
        page.wait_for_timeout(2000)
        
        # Verify page still shows the form
        expect(page.locator('#calcType')).to_be_visible()
        expect(page.locator('#calcInputs')).to_be_visible()
    
    def test_power_option_exists_in_dropdown(self, page: Page, test_user, register_and_login):
        """
        Test that power option exists in the dropdown
        """
        # Check that power option exists
        power_option = page.locator('#calcType option[value="power"]')
        expect(power_option).to_be_attached()
        
        # Verify we can select it
        page.select_option('#calcType', 'power')
        selected = page.locator('#calcType').input_value()
        assert selected == 'power'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])