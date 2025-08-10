import pytest
from datetime import date, datetime
from pydantic import ValidationError
from typing import Dict, Any

from schemas import (
    UserCreate, UserRead, UserBase,
    AppointmentCreate, AppointmentRead,
    PrescriptionCreate, PrescriptionRead,
    ReminderCreate, ReminderRead,
    CallLogCreate, CallLogRead,
    LoginRequest, Token, RefreshRequest, UserInfo
)

class TestUserSchemas:
    """Test cases for User-related Pydantic schemas"""
    
    def test_user_base_valid_data(self):
        """Test UserBase with valid data"""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "1234567890",
            "address": "123 Main St",
            "specialty": "Cardiology"
        }
        
        user = UserBase(**user_data)
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.email == "john.doe@example.com"
        assert user.phone_number == "1234567890"
        assert user.specialty == "Cardiology"
    
    def test_user_base_optional_fields(self):
        """Test UserBase with only required fields"""
        user_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com"
        }
        
        user = UserBase(**user_data)
        assert user.first_name == "Jane"
        assert user.dob is None
        assert user.phone_number is None
        assert user.address is None
        assert user.specialty is None
    
    def test_user_base_invalid_email(self):
        """Test UserBase with invalid email format"""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)
    
    def test_user_create_schema(self):
        """Test UserCreate schema"""
        user_data = {
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": "alice@example.com",
            "password": "secure_password123",
            "role": "doctor",
            "specialty": "Neurology"
        }
        
        user = UserCreate(**user_data)
        assert user.password == "secure_password123"
        assert user.role == "doctor"
        assert user.specialty == "Neurology"
    
    def test_user_create_default_role(self):
        """Test UserCreate with default role"""
        user_data = {
            "first_name": "Bob",
            "last_name": "Wilson",
            "email": "bob@example.com",
            "password": "password123"
        }
        
        user = UserCreate(**user_data)
        assert user.role == "patient"  # Default role
    
    def test_user_read_schema(self):
        """Test UserRead schema"""
        user_data = {
            "user_id": 123,
            "first_name": "Charlie",
            "last_name": "Brown",
            "email": "charlie@example.com",
            "role": "admin",
            "created_at": datetime.now(),
            "dob": date(1985, 3, 15)
        }
        
        user = UserRead(**user_data)
        assert user.user_id == 123
        assert user.role == "admin"
        assert isinstance(user.created_at, datetime)
        assert user.dob == date(1985, 3, 15)

class TestAppointmentSchemas:
    """Test cases for Appointment-related schemas"""
    
    def test_appointment_base_schema(self):
        """Test AppointmentBase schema"""
        appointment_data = {
            "patient_id": 1,
            "doctor_id": 2,
            "appointment_date": datetime(2024, 12, 25, 10, 30),
            "status": "scheduled"
        }
        
        appointment = AppointmentBase(**appointment_data)
        assert appointment.patient_id == 1
        assert appointment.doctor_id == 2
        assert appointment.appointment_date == datetime(2024, 12, 25, 10, 30)
        assert appointment.status == "scheduled"
    
    def test_appointment_base_optional_status(self):
        """Test AppointmentBase with optional status"""
        appointment_data = {
            "patient_id": 1,
            "doctor_id": 2,
            "appointment_date": datetime.now()
        }
        
        appointment = AppointmentBase(**appointment_data)
        assert appointment.status is None
    
    def test_appointment_create_schema(self):
        """Test AppointmentCreate schema"""
        appointment_data = {
            "patient_id": 5,
            "doctor_id": 10,
            "appointment_date": datetime(2024, 11, 15, 14, 0),
            "status": "confirmed"
        }
        
        appointment = AppointmentCreate(**appointment_data)
        assert isinstance(appointment, AppointmentBase)
        assert appointment.patient_id == 5
    
    def test_appointment_read_schema(self):
        """Test AppointmentRead schema"""
        appointment_data = {
            "appointment_id": 100,
            "patient_id": 1,
            "doctor_id": 2,
            "appointment_date": datetime(2024, 12, 25, 10, 30),
            "status": "completed",
            "created_at": datetime.now()
        }
        
        appointment = AppointmentRead(**appointment_data)
        assert appointment.appointment_id == 100
        assert appointment.status == "completed"
        assert isinstance(appointment.created_at, datetime)

class TestPrescriptionSchemas:
    """Test cases for Prescription-related schemas"""
    
    def test_prescription_base_schema(self):
        """Test PrescriptionBase schema"""
        prescription_data = {
            "patient_id": 1,
            "doctor_id": 2,
            "medication_name": "Aspirin",
            "dosage": "100mg",
            "frequency": "Once daily",
            "start_date": date.today()
        }
        
        prescription = PrescriptionBase(**prescription_data)
        assert prescription.medication_name == "Aspirin"
        assert prescription.dosage == "100mg"
        assert prescription.frequency == "Once daily"
        assert prescription.start_date == date.today()
    
    def test_prescription_base_required_fields_only(self):
        """Test PrescriptionBase with only required fields"""
        prescription_data = {
            "patient_id": 1,
            "doctor_id": 2,
            "medication_name": "Lisinopril"
        }
        
        prescription = PrescriptionBase(**prescription_data)
        assert prescription.medication_name == "Lisinopril"
        assert prescription.dosage is None
        assert prescription.frequency is None
        assert prescription.start_date is None
    
    def test_prescription_read_schema(self):
        """Test PrescriptionRead schema"""
        prescription_data = {
            "prescription_id": 50,
            "patient_id": 1,
            "doctor_id": 2,
            "medication_name": "Metformin",
            "dosage": "500mg",
            "created_at": datetime.now()
        }
        
        prescription = PrescriptionRead(**prescription_data)
        assert prescription.prescription_id == 50
        assert prescription.medication_name == "Metformin"
        assert isinstance(prescription.created_at, datetime)

class TestReminderSchemas:
    """Test cases for Reminder-related schemas"""
    
    def test_reminder_base_schema(self):
        """Test ReminderBase schema"""
        reminder_data = {
            "patient_id": 1,
            "type": "medication",
            "reference_id": 123,
            "reminder_time": datetime(2024, 12, 25, 9, 0),
            "status": "pending"
        }
        
        reminder = ReminderBase(**reminder_data)
        assert reminder.type == "medication"
        assert reminder.reference_id == 123
        assert reminder.reminder_time == datetime(2024, 12, 25, 9, 0)
        assert reminder.status == "pending"
    
    def test_reminder_base_optional_fields(self):
        """Test ReminderBase with optional fields"""
        reminder_data = {
            "patient_id": 1,
            "type": "appointment",
            "reminder_time": datetime.now()
        }
        
        reminder = ReminderBase(**reminder_data)
        assert reminder.reference_id is None
        assert reminder.status is None
    
    def test_reminder_read_schema(self):
        """Test ReminderRead schema"""
        reminder_data = {
            "reminder_id": 25,
            "patient_id": 1,
            "type": "medication",
            "reminder_time": datetime.now(),
            "created_at": datetime.now()
        }
        
        reminder = ReminderRead(**reminder_data)
        assert reminder.reminder_id == 25
        assert isinstance(reminder.created_at, datetime)

class TestCallLogSchemas:
    """Test cases for CallLog-related schemas"""
    
    def test_call_log_base_schema(self):
        """Test CallLogBase schema"""
        call_data = {
            "patient_id": 1,
            "call_type": "consultation",
            "call_time": datetime.now(),
            "call_status": "completed",
            "notes": "Patient discussed symptoms and treatment options."
        }
        
        call_log = CallLogBase(**call_data)
        assert call_log.call_type == "consultation"
        assert call_log.call_status == "completed"
        assert "symptoms" in call_log.notes
    
    def test_call_log_base_optional_fields(self):
        """Test CallLogBase with optional fields"""
        call_data = {
            "patient_id": 1,
            "call_time": datetime.now()
        }
        
        call_log = CallLogBase(**call_data)
        assert call_log.call_type is None
        assert call_log.call_status is None
        assert call_log.notes is None
    
    def test_call_log_read_schema(self):
        """Test CallLogRead schema"""
        call_data = {
            "call_id": 75,
            "patient_id": 1,
            "call_time": datetime.now(),
            "call_type": "emergency",
            "call_status": "answered"
        }
        
        call_log = CallLogRead(**call_data)
        assert call_log.call_id == 75
        assert call_log.call_type == "emergency"

class TestAuthSchemas:
    """Test cases for Authentication-related schemas"""
    
    def test_login_request_schema(self):
        """Test LoginRequest schema"""
        login_data = {
            "email": "user@example.com",
            "password": "secure_password",
            "role": "patient"
        }
        
        login = LoginRequest(**login_data)
        assert login.email == "user@example.com"
        assert login.password == "secure_password"
        assert login.role == "patient"
    
    def test_login_request_invalid_email(self):
        """Test LoginRequest with invalid email"""
        login_data = {
            "email": "invalid-email",
            "password": "password",
            "role": "patient"
        }
        
        with pytest.raises(ValidationError):
            LoginRequest(**login_data)
    
    def test_token_schema(self):
        """Test Token schema"""
        token_data = {
            "access_token": "access_token_string",
            "refresh_token": "refresh_token_string"
        }
        
        token = Token(**token_data)
        assert token.access_token == "access_token_string"
        assert token.refresh_token == "refresh_token_string"
        assert token.token_type == "bearer"  # Default value
    
    def test_token_schema_custom_type(self):
        """Test Token schema with custom token type"""
        token_data = {
            "access_token": "access_token_string",
            "refresh_token": "refresh_token_string",
            "token_type": "custom"
        }
        
        token = Token(**token_data)
        assert token.token_type == "custom"
    
    def test_refresh_request_schema(self):
        """Test RefreshRequest schema"""
        refresh_data = {"refresh_token": "refresh_token_string"}
        
        refresh = RefreshRequest(**refresh_data)
        assert refresh.refresh_token == "refresh_token_string"
    
    def test_user_info_schema(self):
        """Test UserInfo schema"""
        user_info_data = {
            "role": "doctor",
            "user_id": 456
        }
        
        user_info = UserInfo(**user_info_data)
        assert user_info.role == "doctor"
        assert user_info.user_id == 456

class TestSchemaValidation:
    """Test cases for schema validation edge cases"""
    
    def test_missing_required_fields(self):
        """Test schemas with missing required fields"""
        # Missing required fields for UserBase
        with pytest.raises(ValidationError):
            UserBase(first_name="John")  # Missing last_name and email
        
        # Missing required fields for AppointmentBase
        with pytest.raises(ValidationError):
            AppointmentBase(patient_id=1)  # Missing doctor_id and appointment_date
    
    def test_invalid_data_types(self):
        """Test schemas with invalid data types"""
        # Invalid user_id type
        with pytest.raises(ValidationError):
            UserRead(
                user_id="not_an_integer",
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                role="patient",
                created_at=datetime.now()
            )
        
        # Invalid datetime type
        with pytest.raises(ValidationError):
            AppointmentBase(
                patient_id=1,
                doctor_id=2,
                appointment_date="not_a_datetime"
            )
    
    def test_email_validation_edge_cases(self):
        """Test email validation with various formats"""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "123@example.org"
        ]
        
        invalid_emails = [
            "plainaddress",
            "@missingdomain.com",
            "missing@.com",
            "spaces @example.com",
            "toolong" + "x" * 100 + "@example.com"
        ]
        
        for email in valid_emails:
            user = UserBase(
                first_name="Test",
                last_name="User",
                email=email
            )
            assert user.email == email
        
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                UserBase(
                    first_name="Test",
                    last_name="User",
                    email=email
                )
    
    def test_schema_serialization(self):
        """Test schema serialization to dict"""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password": "password123",
            "role": "patient"
        }
        
        user = UserCreate(**user_data)
        user_dict = user.model_dump()
        
        assert isinstance(user_dict, dict)
        assert user_dict["first_name"] == "John"
        assert user_dict["email"] == "john@example.com"
        assert user_dict["role"] == "patient"
    
    def test_schema_json_serialization(self):
        """Test schema JSON serialization"""
        appointment_data = {
            "patient_id": 1,
            "doctor_id": 2,
            "appointment_date": datetime(2024, 12, 25, 10, 30),
            "status": "scheduled"
        }
        
        appointment = AppointmentBase(**appointment_data)
        json_str = appointment.model_dump_json()
        
        assert isinstance(json_str, str)
        assert "patient_id" in json_str
        assert "2024-12-25T10:30:00" in json_str

if __name__ == "__main__":
    pytest.main([__file__])
