import pytest
from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

# Add the parent directory to the Python path to allow imports from the main application
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base
from models import User, Appointment, Prescription, Reminder, CallLog
from utils.auth import hash_password

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./tests/test_models.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Create the database and tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for testing
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up the database after the test
        Base.metadata.drop_all(bind=engine)
        # Remove the test database file
        if os.path.exists("test_models.db"):
            os.remove("test_models.db")

@pytest.fixture(scope="function")
def sample_patient(db_session):
    """Create a sample patient user"""
    patient = User(
        email="patient@example.com",
        password_hash=hash_password("testpass123"),
        first_name="John",
        last_name="Doe",
        dob=date(1990, 1, 1),
        phone_number="+1234567890",
        address="123 Test St",
        role="patient"
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient

@pytest.fixture(scope="function")
def sample_doctor(db_session):
    """Create a sample doctor user"""
    doctor = User(
        email="doctor@example.com",
        password_hash=hash_password("testpass123"),
        first_name="Jane",
        last_name="Smith",
        dob=date(1980, 1, 1),
        phone_number="+1987654321",
        address="456 Doctor Ln",
        role="doctor",
        specialty="Cardiology"
    )
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)
    return doctor
