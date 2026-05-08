"""
End-to-End Tests for Statistics Feature Workflow

Tests the complete user journey for viewing calculation statistics.
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
        "first_name": "Stats",
        "last_name": "User",
        "email": f"stats_{unique_id}@example.com",
        "username": f"statsuser_{unique_id}",
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


class TestStatisticsWorkflow:
    """Test complete statistics feature user flows"""
    
    def test_statistics_section_exists(self, page: Page, test_user, register_and_login):
        """Test that statistics section is visible on dashboard"""
        # Should be on dashboard after login
        expect(page).to_have_url(f"{BASE_URL}/dashboard")
        
        # Check statistics section exists
        stats_section = page.locator('text=Your Statistics')
        expect(stats_section).to_be_visible()
        
        # Check individual stat elements exist
        expect(page.locator('#totalCalcs')).to_be_visible()
        expect(page.locator('#mostUsed')).to_be_visible()
        expect(page.locator('#avgOperands')).to_be_visible()
    
    def test_statistics_show_zero_for_new_user(self, page: Page, test_user, register_and_login):
        """Test that statistics show zero/empty for new users"""
        # Wait for page to load
        page.wait_for_timeout(1000)
        
        # Check that statistics show initial values
        total_calcs = page.locator('#totalCalcs')
        expect(total_calcs).to_be_visible()
        
        # Should show 0 or - for new user
        total_text = total_calcs.text_content()
        assert total_text in ['0', '-']
    
    def test_statistics_update_after_calculation(self, page: Page, test_user, register_and_login):
        """Test that statistics update after creating a calculation"""
        # Wait for page to fully load
        page.wait_for_timeout(1000)
        
        # Create a calculation
        page.select_option('#calcType', 'addition')
        page.fill('#calcInputs', '5, 3')
        page.click('button[type="submit"]')
        
        # Wait for calculation to complete and statistics to refresh
        page.wait_for_timeout(2000)
        
        # Check total calculations increased
        total_calcs = page.locator('#totalCalcs')
        expect(total_calcs).to_be_visible()
        
        # Should show at least 1 calculation
        total_text = total_calcs.text_content()
        assert total_text != '0' and total_text != '-'
    
    def test_statistics_operations_breakdown_visible(self, page: Page, test_user, register_and_login):
        """Test that operations breakdown section is visible"""
        # Check breakdown section exists
        breakdown = page.locator('#operationsBreakdown')
        expect(breakdown).to_be_visible()
    
    def test_statistics_most_used_operation(self, page: Page, test_user, register_and_login):
        """Test most used operation display"""
        # Check most used operation element exists
        most_used = page.locator('#mostUsed')
        expect(most_used).to_be_visible()
    
    def test_statistics_average_operands_display(self, page: Page, test_user, register_and_login):
        """Test average operands display"""
        # Check average operands element exists
        avg_operands = page.locator('#avgOperands')
        expect(avg_operands).to_be_visible()
    
    def test_statistics_multiple_calculations_breakdown(self, page: Page, test_user, register_and_login):
        """Test that breakdown shows multiple calculation types"""
        # Wait for page load
        page.wait_for_timeout(1000)
        
        # Create multiple calculations of different types
        calculations = [
            ('addition', '5, 3'),
            ('subtraction', '10, 4'),
            ('multiplication', '2, 3')
        ]
        
        for calc_type, inputs in calculations:
            page.select_option('#calcType', calc_type)
            page.fill('#calcInputs', inputs)
            page.click('button[type="submit"]')
            page.wait_for_timeout(1500)
        
        # Check that breakdown is not empty
        breakdown = page.locator('#operationsBreakdown')
        breakdown_text = breakdown.text_content()
        assert 'No calculations yet' not in breakdown_text
        
        # Check total is correct
        total_calcs = page.locator('#totalCalcs')
        total_text = total_calcs.text_content()
        assert int(total_text) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])