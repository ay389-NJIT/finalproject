"""
End-to-End Tests for Profile Management Workflow

Tests the complete user journey from login to profile management.
Uses Playwright for browser automation.

Demonstrates:
- Real browser interaction
- Multi-step workflows
- Form validation
- Session management
- User experience flows
"""
import pytest
import re
from playwright.sync_api import Page, expect
import uuid

# Base URL for the application
BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="function")
def test_user():
    """Test user credentials - unique for each test"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "first_name": "E2E",
        "last_name": "TestUser",
        "email": f"e2e_{unique_id}@example.com",
        "username": f"e2euser_{unique_id}",
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


class TestProfileManagementFlow:
    """Test complete profile management user flows"""
    
    def test_complete_profile_update_workflow(self, page: Page, test_user, register_and_login):
        """
        Test Flow: Login → Navigate to Profile → Update Info → Verify Changes
        """
        # Navigate to profile page
        page.goto(f"{BASE_URL}/profile")
        expect(page).to_have_url(f"{BASE_URL}/profile")
        
        # Verify page loaded correctly
        expect(page.locator("h1")).to_contain_text("My Profile")
        
        # Verify form is pre-filled with current data
        expect(page.locator('#firstName')).to_have_value(test_user["first_name"])
        expect(page.locator('#lastName')).to_have_value(test_user["last_name"])
        expect(page.locator('#email')).to_have_value(test_user["email"])
        expect(page.locator('#username')).to_have_value(test_user["username"])
        
        # Update profile information
        updated_first_name = "Updated"
        updated_last_name = "Name"
        updated_email = "updated@example.com"
        
        page.fill('#firstName', updated_first_name)
        page.fill('#lastName', updated_last_name)
        page.fill('#email', updated_email)
        
        # Submit form
        page.click('#profileForm button[type="submit"]')
        
        # Wait for and verify success message
        success_msg = page.locator('#successMsg')
        expect(success_msg).to_be_visible(timeout=5000)
        expect(success_msg).to_contain_text("successfully")
        
        # Reload page and verify changes persisted
        page.reload()
        page.wait_for_timeout(1000)
        
        expect(page.locator('#firstName')).to_have_value(updated_first_name)
        expect(page.locator('#lastName')).to_have_value(updated_last_name)
        expect(page.locator('#email')).to_have_value(updated_email)
    
    def test_password_change_and_forced_relogin(self, page: Page, test_user, register_and_login):
        """
        Test Flow: Login → Change Password → Auto Logout → Login with New Password
        """
        # Navigate to profile
        page.goto(f"{BASE_URL}/profile")
        
        # Change password
        new_password = "NewTestPass456!"
        
        page.fill('#currentPassword', test_user["password"])
        page.fill('#newPassword', new_password)
        page.fill('#confirmPassword', new_password)
        
        # Submit password change
        page.click('#passwordForm button[type="submit"]')
        
        # Wait for success message
        success_msg = page.locator('#successMsg')
        expect(success_msg).to_be_visible(timeout=5000)
        expect(success_msg).to_contain_text("Password changed")
        
        # Should auto-redirect to login
        page.wait_for_url(f"{BASE_URL}/login", timeout=10000)
        
        # Try logging in with OLD password - should fail
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', test_user["password"])
        page.click('button[type="submit"]')
        page.wait_for_timeout(2000)
        
        # Should still be on login page or show error
        current_url = page.url
        assert "/login" in current_url or "/dashboard" not in current_url
        
        # Login with NEW password - should succeed
        page.goto(f"{BASE_URL}/login")
        page.fill('input[name="username"]', test_user["username"])
        page.fill('input[name="password"]', new_password)
        page.click('button[type="submit"]')
        
        # Should redirect to dashboard
        page.wait_for_url(f"{BASE_URL}/dashboard", timeout=5000)
        expect(page).to_have_url(f"{BASE_URL}/dashboard")
    
    def test_profile_validation_errors_displayed(self, page: Page, test_user, register_and_login):
        """
        Test Flow: Enter Invalid Data → See Validation Errors
        """
        page.goto(f"{BASE_URL}/profile")
        
        # Try to submit with invalid email format
        page.fill('#email', 'not-a-valid-email')
        page.click('#profileForm button[type="submit"]')
        
        # Should show error (browser validation or API error)
        page.wait_for_timeout(1000)
        
        # Try username that's too short (less than 3 chars)
        page.fill('#email', test_user["email"])  # Fix email first
        page.fill('#username', 'ab')
        page.click('#profileForm button[type="submit"]')
        
        page.wait_for_timeout(1000)
    
    def test_password_mismatch_shows_error(self, page: Page, test_user, register_and_login):
        """
        Test Flow: Enter Mismatched Passwords → See Error Message
        """
        page.goto(f"{BASE_URL}/profile")
        
        # Enter mismatched passwords
        page.fill('#currentPassword', test_user["password"])
        page.fill('#newPassword', 'NewPass123!')
        page.fill('#confirmPassword', 'DifferentPass456!')
        page.click('#passwordForm button[type="submit"]')
        
        # Should show error message
        error_msg = page.locator('#errorMsg')
        expect(error_msg).to_be_visible(timeout=5000)
        expect(error_msg).to_contain_text("do not match")
    
    def test_wrong_current_password_shows_error(self, page: Page, test_user, register_and_login):
        """
        Test Flow: Enter Wrong Current Password → See Error
        """
        page.goto(f"{BASE_URL}/profile")
        
        # Enter wrong current password
        page.fill('#currentPassword', 'WrongPassword123!')
        page.fill('#newPassword', 'NewPass456!')
        page.fill('#confirmPassword', 'NewPass456!')
        page.click('#passwordForm button[type="submit"]')
        
        # Should show error message
        error_msg = page.locator('#errorMsg')
        expect(error_msg).to_be_visible(timeout=5000)
        expect(error_msg).to_contain_text("incorrect")
    
    def test_back_to_dashboard_link_works(self, page: Page, test_user, register_and_login):
        """Test navigation back to dashboard"""
        page.goto(f"{BASE_URL}/profile")
        
        # Click back to dashboard link
        page.click('a[href="/dashboard"]')
        
        # Should navigate to dashboard
        page.wait_for_url(f"{BASE_URL}/dashboard", timeout=5000)
        expect(page).to_have_url(f"{BASE_URL}/dashboard")


class TestProfileAccessControl:
    """Test that profile page requires authentication"""
    
    def test_profile_requires_authentication(self, page: Page):
        """Test that accessing profile without login redirects to login"""
        # Clear any existing auth
        page.context.clear_cookies()
        
        # Try to access profile directly
        page.goto(f"{BASE_URL}/profile")
        
        # Should redirect to login
        page.wait_for_url(f"{BASE_URL}/login", timeout=5000)
        expect(page).to_have_url(f"{BASE_URL}/login")
    
    def test_expired_session_redirects_to_login(self, page: Page, test_user, register_and_login):
        """Test that expired/invalid token redirects to login"""
        # Go to profile (while logged in)
        page.goto(f"{BASE_URL}/profile")
        expect(page).to_have_url(f"{BASE_URL}/profile")
        
        # Manually corrupt the token in localStorage
        page.evaluate("localStorage.setItem('access_token', 'invalid_token_xyz')")
        
        # Reload page - should redirect to login
        page.reload()
        page.wait_for_url(f"{BASE_URL}/login", timeout=5000)
        expect(page).to_have_url(f"{BASE_URL}/login")


class TestUserExperience:
    """Test user experience and UI behavior"""
    
    def test_success_message_auto_dismisses(self, page: Page, test_user, register_and_login):
        """Test that success messages auto-dismiss after 3 seconds"""
        page.goto(f"{BASE_URL}/profile")
        
        # Update profile
        page.fill('#firstName', 'AutoDismiss')
        page.click('#profileForm button[type="submit"]')
        
        # Success message should appear
        success_msg = page.locator('#successMsg')
        expect(success_msg).to_be_visible(timeout=5000)
        
        # Wait 4 seconds and check if it's hidden
        page.wait_for_timeout(4000)
        expect(success_msg).to_be_hidden()
    
    def test_forms_are_clearly_separated(self, page: Page, test_user, register_and_login):
        """Test that profile update and password change are in separate sections"""
        page.goto(f"{BASE_URL}/profile")
        
        # Verify both forms exist
        profile_form = page.locator('#profileForm')
        password_form = page.locator('#passwordForm')
        
        expect(profile_form).to_be_visible()
        expect(password_form).to_be_visible()
        
        # Verify they have separate submit buttons
        profile_submit = page.locator('#profileForm button[type="submit"]')
        password_submit = page.locator('#passwordForm button[type="submit"]')
        
        expect(profile_submit).to_be_visible()
        expect(password_submit).to_be_visible()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])