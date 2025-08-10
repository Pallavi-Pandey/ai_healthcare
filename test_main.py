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
    
    def test_startup_event_creates_admin(self, test_client):
        """Test that startup event creates default admin user"""
        # Set environment variables for test
        os.environ["ADMIN_EMAIL"] = "test_admin@example.com"
        os.environ["ADMIN_PASSWORD"] = "test_admin_pass"
        os.environ["ADMIN_FIRST_NAME"] = "Test"
        os.environ["ADMIN_LAST_NAME"] = "Admin"
        
        # Trigger startup event by making a request
        response = test_client.get("/")
        assert response.status_code == 200
        
        # Verify admin user was created
        db = TestingSessionLocal()
        admin_user = db.query(User).filter(User.email == "test_admin@example.com").first()
        assert admin_user is not None
        assert admin_user.role == "admin"
        assert admin_user.first_name == "Test"
        db.close()
    
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
