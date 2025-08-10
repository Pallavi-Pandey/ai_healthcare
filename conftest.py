"""
Pytest configuration file with shared fixtures and test setup.
This file provides common fixtures used across all test modules.
"""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from main import app
from database import Base, get_db
from models import User
from utils.auth import hash_password

# Test database configuration
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_healthcare.db"

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine for the entire test session"""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine

@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """Create session factory for tests"""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db_session(test_engine, test_session_factory):
    """Create a fresh database session for each test"""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = test_session_factory()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def test_client(db_session):
    """Create FastAPI test client with test database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Clean up dependency override
    app.dependency_overrides.clear()

@pytest.fixture
def sample_users(db_session):
    """Create sample users for testing"""
    users = {
        'patient': User(
            first_name="John",
            last_name="Doe",
            email="patient@test.com",
            password_hash=hash_password("patient123"),
            role="patient",
            phone_number="1234567890"
        ),
        'doctor': User(
            first_name="Dr. Jane",
            last_name="Smith",
            email="doctor@test.com",
            password_hash=hash_password("doctor123"),
            role="doctor",
            specialty="Cardiology"
        ),
        'admin': User(
            first_name="Admin",
            last_name="User",
            email="admin@test.com",
            password_hash=hash_password("admin123"),
            role="admin",
            specialty="Administration"
        )
    }
    
    for user in users.values():
        db_session.add(user)
    
    db_session.commit()
    
    # Refresh to get IDs
    for user in users.values():
        db_session.refresh(user)
    
    return users

@pytest.fixture
def auth_headers(test_client, sample_users):
    """Create authentication headers for different user types"""
    headers = {}
    
    for role, user in sample_users.items():
        login_data = {
            "email": user.email,
            "password": f"{role}123",
            "role": role
        }
        
        response = test_client.post("/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers[role] = {"Authorization": f"Bearer {token}"}
    
    return headers

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables"""
    # Set test environment variables
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
    os.environ["ADMIN_TOKEN"] = "test-admin-token"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
    os.environ["REFRESH_TOKEN_EXPIRE_MINUTES"] = "43200"
    
    yield
    
    # Clean up environment variables if needed
    pass

@pytest.fixture
def sample_healthcare_data(db_session, sample_users):
    """Create sample healthcare data for testing"""
    from models import Appointment, Prescription, Reminder, CallLog
    from datetime import datetime, date
    
    patient = sample_users['patient']
    doctor = sample_users['doctor']
    
    # Create appointment
    appointment = Appointment(
        patient_id=patient.user_id,
        doctor_id=doctor.user_id,
        appointment_date=datetime(2024, 12, 25, 10, 30),
        status="scheduled"
    )
    db_session.add(appointment)
    
    # Create prescription
    prescription = Prescription(
        patient_id=patient.user_id,
        doctor_id=doctor.user_id,
        medication_name="Aspirin",
        dosage="100mg",
        frequency="Once daily",
        start_date=date.today()
    )
    db_session.add(prescription)
    
    # Create reminder
    reminder = Reminder(
        patient_id=patient.user_id,
        type="medication",
        reference_id=1,
        reminder_time=datetime(2024, 12, 25, 9, 0),
        status="pending"
    )
    db_session.add(reminder)
    
    # Create call log
    call_log = CallLog(
        patient_id=patient.user_id,
        call_type="consultation",
        call_time=datetime.now(),
        call_status="completed",
        notes="Patient consultation completed successfully."
    )
    db_session.add(call_log)
    
    db_session.commit()
    
    return {
        'appointment': appointment,
        'prescription': prescription,
        'reminder': reminder,
        'call_log': call_log
    }

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "auth: marks tests related to authentication"
    )
    config.addinivalue_line(
        "markers", "database: marks tests related to database operations"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on test file names
        if "test_auth" in item.nodeid:
            item.add_marker(pytest.mark.auth)
        if "test_database" in item.nodeid or "test_models" in item.nodeid:
            item.add_marker(pytest.mark.database)
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)
