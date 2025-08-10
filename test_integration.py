import pytest
from datetime import datetime, date
from fastapi.testclient import TestClient

from models import User, Appointment, Prescription, Reminder, CallLog

@pytest.mark.integration
class TestUserWorkflow:
    """Integration tests for complete user workflows"""
    
    def test_patient_registration_and_login_workflow(self, test_client):
        """Test complete patient registration and login workflow"""
        # Step 1: Register patient
        patient_data = {
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": "alice.integration@test.com",
            "password": "secure123",
            "role": "patient",
            "phone_number": "9876543210"
        }
        
        register_response = test_client.post("/auth/register", json=patient_data)
        assert register_response.status_code == 200
        
        user_data = register_response.json()
        assert user_data["email"] == "alice.integration@test.com"
        assert user_data["role"] == "patient"
        
        # Step 2: Login with registered credentials
        login_data = {
            "email": "alice.integration@test.com",
            "password": "secure123",
            "role": "patient"
        }
        
        login_response = test_client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        tokens = login_response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        
        # Step 3: Use access token to get user info
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        me_response = test_client.get("/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        user_info = me_response.json()
        assert user_info["role"] == "patient"
        assert user_info["user_id"] == user_data["user_id"]
    
    def test_doctor_registration_workflow(self, test_client):
        """Test doctor registration workflow with admin token"""
        from utils.auth import ADMIN_TOKEN
        
        # Register doctor with admin token
        doctor_data = {
            "first_name": "Dr. Bob",
            "last_name": "Wilson",
            "email": "bob.integration@test.com",
            "password": "doctor123",
            "role": "doctor",
            "specialty": "Neurology"
        }
        
        headers = {"X-Admin-Token": ADMIN_TOKEN}
        register_response = test_client.post("/auth/register", json=doctor_data, headers=headers)
        assert register_response.status_code == 200
        
        user_data = register_response.json()
        assert user_data["role"] == "doctor"
        assert user_data["specialty"] == "Neurology"
        
        # Login as doctor
        login_data = {
            "email": "bob.integration@test.com",
            "password": "doctor123",
            "role": "doctor"
        }
        
        login_response = test_client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200

@pytest.mark.integration
class TestHealthcareDataWorkflow:
    """Integration tests for healthcare data workflows"""
    
    def test_complete_patient_care_workflow(self, test_client, sample_users, auth_headers, db_session):
        """Test complete patient care workflow from appointment to prescription"""
        patient = sample_users['patient']
        doctor = sample_users['doctor']
        
        # Step 1: Create appointment
        appointment = Appointment(
            patient_id=patient.user_id,
            doctor_id=doctor.user_id,
            appointment_date=datetime(2024, 12, 25, 10, 30),
            status="scheduled"
        )
        db_session.add(appointment)
        db_session.commit()
        db_session.refresh(appointment)
        
        # Step 2: Complete appointment
        appointment.status = "completed"
        db_session.commit()
        
        # Step 3: Create prescription after appointment
        prescription = Prescription(
            patient_id=patient.user_id,
            doctor_id=doctor.user_id,
            medication_name="Lisinopril",
            dosage="10mg",
            frequency="Once daily",
            start_date=date.today()
        )
        db_session.add(prescription)
        db_session.commit()
        db_session.refresh(prescription)
        
        # Step 4: Create medication reminder
        reminder = Reminder(
            patient_id=patient.user_id,
            type="medication",
            reference_id=prescription.prescription_id,
            reminder_time=datetime(2024, 12, 26, 9, 0),
            status="pending"
        )
        db_session.add(reminder)
        db_session.commit()
        
        # Step 5: Log follow-up call
        call_log = CallLog(
            patient_id=patient.user_id,
            call_type="follow-up",
            call_time=datetime.now(),
            call_status="completed",
            notes="Patient reported improved symptoms after medication."
        )
        db_session.add(call_log)
        db_session.commit()
        
        # Verify complete workflow
        db_session.refresh(patient)
        assert len(patient.patient_appointments) >= 1
        assert len(patient.patient_prescriptions) >= 1
        assert len(patient.reminders) >= 1
        assert len(patient.call_logs) >= 1
        
        # Verify relationships
        assert patient.patient_appointments[0].doctor == doctor
        assert patient.patient_prescriptions[0].doctor == doctor
    
    def test_multi_patient_doctor_workflow(self, test_client, db_session):
        """Test doctor managing multiple patients workflow"""
        from utils.auth import hash_password
        
        # Create doctor
        doctor = User(
            first_name="Dr. Multi",
            last_name="Practice",
            email="multi@test.com",
            password_hash=hash_password("doctor123"),
            role="doctor",
            specialty="Family Medicine"
        )
        db_session.add(doctor)
        db_session.commit()
        db_session.refresh(doctor)
        
        # Create multiple patients
        patients = []
        for i in range(3):
            patient = User(
                first_name=f"Patient{i}",
                last_name="Test",
                email=f"patient{i}@test.com",
                password_hash=hash_password("patient123"),
                role="patient"
            )
            patients.append(patient)
            db_session.add(patient)
        
        db_session.commit()
        
        # Create appointments for each patient
        appointments = []
        for i, patient in enumerate(patients):
            db_session.refresh(patient)
            appointment = Appointment(
                patient_id=patient.user_id,
                doctor_id=doctor.user_id,
                appointment_date=datetime(2024, 12, 25 + i, 10, 0),
                status="scheduled"
            )
            appointments.append(appointment)
            db_session.add(appointment)
        
        db_session.commit()
        
        # Verify doctor has all appointments
        db_session.refresh(doctor)
        assert len(doctor.doctor_appointments) == 3
        
        # Create prescriptions for each patient
        for i, patient in enumerate(patients):
            prescription = Prescription(
                patient_id=patient.user_id,
                doctor_id=doctor.user_id,
                medication_name=f"Medication{i}",
                dosage="100mg"
            )
            db_session.add(prescription)
        
        db_session.commit()
        
        # Verify doctor has all prescriptions
        db_session.refresh(doctor)
        assert len(doctor.doctor_prescriptions) == 3

@pytest.mark.integration
class TestAuthenticationIntegration:
    """Integration tests for authentication workflows"""
    
    def test_token_refresh_workflow(self, test_client, sample_users):
        """Test complete token refresh workflow"""
        patient = sample_users['patient']
        
        # Step 1: Login to get initial tokens
        login_data = {
            "email": patient.email,
            "password": "patient123",
            "role": "patient"
        }
        
        login_response = test_client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        initial_tokens = login_response.json()
        
        # Step 2: Use access token to verify authentication
        headers = {"Authorization": f"Bearer {initial_tokens['access_token']}"}
        me_response = test_client.get("/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        # Step 3: Refresh tokens
        refresh_data = {"refresh_token": initial_tokens["refresh_token"]}
        refresh_response = test_client.post("/auth/refresh", json=refresh_data)
        assert refresh_response.status_code == 200
        
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        
        # Step 4: Use new access token
        new_headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
        new_me_response = test_client.get("/auth/me", headers=new_headers)
        assert new_me_response.status_code == 200
        
        # Verify user info is consistent
        old_user_info = me_response.json()
        new_user_info = new_me_response.json()
        assert old_user_info["user_id"] == new_user_info["user_id"]
        assert old_user_info["role"] == new_user_info["role"]
    
    def test_oauth2_token_workflow(self, test_client, sample_users):
        """Test OAuth2 token endpoint workflow"""
        patient = sample_users['patient']
        
        # Step 1: Get token using OAuth2 endpoint
        form_data = {
            "username": patient.email,
            "password": "patient123"
        }
        
        token_response = test_client.post("/auth/token", data=form_data)
        assert token_response.status_code == 200
        
        tokens = token_response.json()
        assert "access_token" in tokens
        assert tokens["token_type"] == "bearer"
        
        # Step 2: Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        me_response = test_client.get("/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        user_info = me_response.json()
        assert user_info["user_id"] == patient.user_id

@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Integration tests for error handling across the system"""
    
    def test_invalid_authentication_workflow(self, test_client):
        """Test various invalid authentication scenarios"""
        # Test 1: Invalid login credentials
        invalid_login = {
            "email": "nonexistent@test.com",
            "password": "wrongpassword",
            "role": "patient"
        }
        
        response = test_client.post("/auth/login", json=invalid_login)
        assert response.status_code == 401
        
        # Test 2: Invalid token usage
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = test_client.get("/auth/me", headers=invalid_headers)
        assert response.status_code == 401
        
        # Test 3: Missing authentication
        response = test_client.get("/auth/me")
        assert response.status_code == 401
    
    def test_validation_error_workflow(self, test_client):
        """Test validation error handling"""
        # Test 1: Invalid email format
        invalid_user = {
            "first_name": "Test",
            "last_name": "User",
            "email": "invalid-email",
            "password": "password123",
            "role": "patient"
        }
        
        response = test_client.post("/auth/register", json=invalid_user)
        assert response.status_code == 422
        
        # Test 2: Missing required fields
        incomplete_user = {
            "first_name": "Test",
            # Missing last_name, email, password
            "role": "patient"
        }
        
        response = test_client.post("/auth/register", json=incomplete_user)
        assert response.status_code == 422
    
    def test_permission_error_workflow(self, test_client):
        """Test permission-based error handling"""
        # Try to register doctor without admin token
        doctor_data = {
            "first_name": "Dr. Unauthorized",
            "last_name": "Test",
            "email": "unauthorized@test.com",
            "password": "doctor123",
            "role": "doctor"
        }
        
        response = test_client.post("/auth/register", json=doctor_data)
        assert response.status_code == 403
        assert "Admin token required" in response.json()["detail"]

@pytest.mark.integration
@pytest.mark.slow
class TestSystemPerformance:
    """Integration tests for system performance"""
    
    def test_concurrent_user_registration(self, test_client):
        """Test system handles concurrent user registrations"""
        import threading
        import time
        
        results = []
        
        def register_user(user_id):
            user_data = {
                "first_name": f"User{user_id}",
                "last_name": "Concurrent",
                "email": f"concurrent{user_id}@test.com",
                "password": "password123",
                "role": "patient"
            }
            
            response = test_client.post("/auth/register", json=user_data)
            results.append(response.status_code)
        
        # Create multiple threads for concurrent registration
        threads = []
        for i in range(10):
            thread = threading.Thread(target=register_user, args=(i,))
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Verify all registrations were successful
        assert all(status == 200 for status in results)
        assert len(results) == 10
        assert end_time - start_time < 10.0  # Should complete within 10 seconds

if __name__ == "__main__":
    pytest.main([__file__])
