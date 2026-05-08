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
        
        # Wait for success message
        success_msg = page.locator('#successMsg')
        expect(success_msg).to_be_visible(timeout=5000)
        expect(success_msg).to_contain_text("8")
        
        # Verify calculation appears in history
        page.wait_for_timeout(1000)
        history_table = page.locator('#calculationsTable')
        expect(history_table).to_contain_text("power")
        expect(history_table).to_contain_text("8")
    
    def test_power_calculation_zero_exponent(self, page: Page, test_user, register_and_login):
        """
        Test Flow: Calculate 5^0 = 1
        """
        page.select_option('#calcType', 'power')
        page.fill('#calcInputs', '5, 0')
        page.click('button[type="submit"]')
        
        success_msg = page.locator('#successMsg')
        expect(success_msg).to_be_visible(timeout=5000)
        expect(success_msg).to_contain_text("1")
    
    def test_power_calculation_negative_exponent(self, page: Page, test_user, register_and_login):
        """
        Test Flow: Calculate 2^-2 = 0.25
        """
        page.select_option('#calcType', 'power')
        page.fill('#calcInputs', '2, -2')
        page.click('button[type="submit"]')
        
        success_msg = page.locator('#successMsg')
        expect(success_msg).to_be_visible(timeout=5000)
        expect(success_msg).to_contain_text("0.25")
    
    def test_power_calculation_fractional_exponent(self, page: Page, test_user, register_and_login):
        """
        Test Flow: Calculate 4^0.5 = 2 (square root)
        """
        page.select_option('#calcType', 'power')
        page.fill('#calcInputs', '4, 0.5')
        page.click('button[type="submit"]')
        
        success_msg = page.locator('#successMsg')
        expect(success_msg).to_be_visible(timeout=5000)
        expect(success_msg).to_contain_text("2")
    
    def test_power_calculation_large_numbers(self, page: Page, test_user, register_and_login):
        """
        Test Flow: Calculate 10^3 = 1000
        """
        page.select_option('#calcType', 'power')
        page.fill('#calcInputs', '10, 3')
        page.click('button[type="submit"]')
        
        success_msg = page.locator('#successMsg')
        expect(success_msg).to_be_visible(timeout=5000)
        expect(success_msg).to_contain_text("1000")
    
    def test_power_calculation_appears_in_history(self, page: Page, test_user, register_and_login):
        """
        Test Flow: Create calculation → Verify it appears in table
        """
        page.select_option('#calcType', 'power')
        page.fill('#calcInputs', '3, 3')
        page.click('button[type="submit"]')
        
        # Wait for success
        page.wait_for_timeout(2000)
        
        # Check history table
        table = page.locator('#calculationsTable')
        expect(table).to_contain_text("27")
        expect(table).to_contain_text("3, 3")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])