import pytest
import os
import sys
import os
from fastapi.testclient import TestClient

# Add the parent directory to the Python path to allow imports from the main application
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.main import app
from app.database.base import get_db
from app.utils.auth import create_access_token, ADMIN_TOKEN

# Override the database dependency for testing
@pytest.fixture(scope="function")
def test_client(db_session):
    """Create a test client with overridden database session"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    
    # Clear the dependency overrides after the test
    app.dependency_overrides.clear()

class TestUserRegistration:
    """Test cases for user registration endpoint"""
    
    def test_register_patient_success(self, test_client):
        """Test successful patient registration"""
        user_data = {
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": "alice@test.com",
            "password": "secure123",
            "role": "patient"
        }
        
        response = test_client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == "alice@test.com"
        assert data["first_name"] == "Alice"
        assert data["role"] == "patient"
        assert "user_id" in data
        assert "password" not in data  # Password should not be returned
    
    def test_register_doctor_with_admin_token(self, test_client):
        """Test doctor registration with valid admin token"""
        user_data = {
            "first_name": "Dr. Bob",
            "last_name": "Wilson",
            "email": "bob@test.com",
            "password": "doctor123",
            "role": "doctor",
            "specialty": "Neurology"
        }
        
        headers = {"X-Admin-Token": ADMIN_TOKEN}
        response = test_client.post("/auth/register", json=user_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["role"] == "doctor"
        assert data["specialty"] == "Neurology"
    
    def test_register_doctor_without_admin_token(self, test_client):
        """Test doctor registration fails without admin token"""
        user_data = {
            "first_name": "Dr. Charlie",
            "last_name": "Brown",
            "email": "charlie@test.com",
            "password": "doctor123",
            "role": "doctor"
        }
        
        response = test_client.post("/auth/register", json=user_data)
        assert response.status_code == 403
        assert "Admin token required" in response.json()["detail"]
    
    def test_register_duplicate_email(self, test_client, sample_patient):
        """Test registration fails with duplicate email"""
        user_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "patient@example.com",  # Same as sample_patient
            "password": "password123",
            "role": "patient"
        }
        
        response = test_client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "User with this email already exists" in response.json()["detail"]
    
    def test_register_invalid_email(self, test_client):
        """Test registration fails with invalid email format"""
        user_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "invalid-email",
            "password": "password123",
            "role": "patient"
        }
        
        response = test_client.post("/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error

class TestUserLogin:
    """Test cases for user login endpoint"""
    
    def test_login_patient_success(self, test_client, sample_patient):
        """Test successful patient login"""
        login_data = {
            "email": "patient@example.com",
            "password": "testpass123",
            "role": "patient"
        }
        
        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_doctor_success(self, test_client, sample_doctor):
        """Test successful doctor login"""
        login_data = {
            "email": "doctor@example.com",
            "password": "testpass123",
            "role": "doctor"
        }
        
        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_login_wrong_password(self, test_client, sample_patient):
        """Test login fails with wrong password"""
        login_data = {
            "email": "patient@example.com",
            "password": "wrongpassword",
            "role": "patient"
        }
        
        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_wrong_role(self, test_client, sample_patient):
        """Test login fails with wrong role"""
        login_data = {
            "email": "patient@example.com",
            "password": "testpass123",
            "role": "doctor"  # Wrong role
        }
        
        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Invalid credentials or role" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, test_client):
        """Test login fails for nonexistent user"""
        login_data = {
            "email": "nonexistent@test.com",
            "password": "password123",
            "role": "patient"
        }
        
        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 401

class TestTokenOperations:
    """Test cases for token-related operations"""
    
    def test_oauth2_token_endpoint(self, test_client, sample_patient):
        """Test OAuth2 token endpoint"""
        form_data = {
            "username": "patient@example.com",
            "password": "testpass123"
        }
        
        response = test_client.post("/auth/token", data=form_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_success(self, test_client, sample_patient):
        """Test successful token refresh"""
        # First login to get tokens
        login_data = {
            "email": "patient@example.com",
            "password": "testpass123",
            "role": "patient"
        }
        
        login_response = test_client.post("/auth/login", json=login_data)
        tokens = login_response.json()
        
        # Use refresh token
        refresh_data = {"refresh_token": tokens["refresh_token"]}
        response = test_client.post("/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_refresh_token_invalid(self, test_client):
        """Test refresh with invalid token"""
        refresh_data = {"refresh_token": "invalid_token"}
        response = test_client.post("/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401
    
    def test_get_current_user_info(self, test_client, sample_patient):
        """Test getting current user info with valid token"""
        # Login to get token
        login_data = {
            "email": "patient@example.com",
            "password": "testpass123",
            "role": "patient"
        }
        
        login_response = test_client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Get user info
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "patient"
        assert "user_id" in data
    
    def test_get_current_user_invalid_token(self, test_client):
        """Test getting user info with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = test_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_get_current_user_no_token(self, test_client):
        """Test getting user info without token"""
        response = test_client.get("/auth/me")
        assert response.status_code == 401

if __name__ == "__main__":
    pytest.main([__file__])
