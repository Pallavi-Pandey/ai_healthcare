import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
from models import User
from utils.auth import hash_password
import os

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def test_client():
    """Create test database and client for each test"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_admin_user():
    """Create a sample admin user for testing"""
    db = TestingSessionLocal()
    admin = User(
        first_name="Test",
        last_name="Admin",
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        role="admin",
        specialty="Administration"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    db.close()
    return admin

class TestMainApp:
    """Test cases for main FastAPI application"""
    
    def test_read_root(self, test_client):
        """Test root endpoint returns correct message"""
        response = test_client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Healthcare AI Backend is running"}
    
    def test_startup_event_creates_admin(self, test_client, monkeypatch, db_session):
        """Test that startup event creates default admin user"""
        from main import startup_event
        from models import User
        
        # Set environment variables for test
        test_email = "test_admin@example.com"
        test_password = "test_admin_pass"
        test_first_name = "Test"
        test_last_name = "Admin"
        
        # Clean up any existing test user
        existing_user = db_session.query(User).filter(User.email == test_email).first()
        if existing_user:
            db_session.delete(existing_user)
            db_session.commit()
        
        # Set environment variables
        monkeypatch.setenv("ADMIN_EMAIL", test_email)
        monkeypatch.setenv("ADMIN_PASSWORD", test_password)
        monkeypatch.setenv("ADMIN_FIRST_NAME", test_first_name)
        monkeypatch.setenv("ADMIN_LAST_NAME", test_last_name)
        
        # Call the startup event handler directly
        startup_event()
        
        # Verify admin user was created
        admin_user = db_session.query(User).filter(User.email == test_email).first()
        assert admin_user is not None, f"Admin user with email {test_email} was not created"
        assert admin_user.role == "admin", f"Expected role 'admin', got '{admin_user.role}'"
        assert admin_user.first_name == test_first_name, f"Expected first name '{test_first_name}', got '{admin_user.first_name}'"
    
    def test_app_title_and_tags(self, test_client):
        """Test FastAPI app configuration"""
        response = test_client.get("/openapi.json")
        assert response.status_code == 200
        openapi_data = response.json()
        assert openapi_data["info"]["title"] == "Healthcare AI Backend"
    
    def test_auth_routes_included(self, test_client):
        """Test that auth routes are properly included"""
        response = test_client.get("/openapi.json")
        assert response.status_code == 200
        openapi_data = response.json()
        paths = openapi_data["paths"]
        
        # Check auth endpoints exist
        assert "/auth/register" in paths
        assert "/auth/login" in paths
        assert "/auth/token" in paths
        assert "/auth/refresh" in paths
        assert "/auth/me" in paths

if __name__ == "__main__":
    pytest.main([__file__])
