import pytest
from datetime import datetime, date
import os
import sys

# Add the parent directory to the Python path to allow imports from the main application
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import User, Appointment, Prescription, Reminder, CallLog
from utils.auth import hash_password

class TestUserModel:
    """Test cases for User model"""
    
    def test_create_patient_user(self, db_session):
        """Test creating a patient user"""
        user = User(
            first_name="Alice",
            last_name="Johnson",
            email="alice@test.com",
            password_hash=hash_password("password123"),
            role="patient",
            dob=date(1990, 5, 15),
            phone_number="9876543210"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.user_id is not None
        assert user.first_name == "Alice"
        assert user.last_name == "Johnson"
        assert user.email == "alice@test.com"
        assert user.role == "patient"
        assert user.dob == date(1990, 5, 15)
        assert user.created_at is not None
    
    def test_create_doctor_user(self, db_session):
        """Test creating a doctor user"""
        doctor = User(
            first_name="Dr. Bob",
            last_name="Wilson",
            email="bob@test.com",
            password_hash=hash_password("doctor123"),
            role="doctor",
            specialty="Neurology"
        )
        
        db_session.add(doctor)
        db_session.commit()
        db_session.refresh(doctor)
        
        assert doctor.user_id is not None
        assert doctor.role == "doctor"
        assert doctor.specialty == "Neurology"
    
    def test_user_email_unique_constraint(self, db_session, sample_patient):
        """Test that email must be unique"""
        duplicate_user = User(
            first_name="Jane",
            last_name="Doe",
            email=sample_patient.email,  # Use the same email as sample_patient
            password_hash=hash_password("password123"),
            role="patient"
        )
        
        db_session.add(duplicate_user)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_user_relationships(self, db_session, sample_patient, sample_doctor):
        """Test user relationships are properly set up"""
        # Create an appointment
        appointment = Appointment(
            patient_id=sample_patient.user_id,
            doctor_id=sample_doctor.user_id,
            appointment_date=datetime.now(),
            status="scheduled"
        )
        db_session.add(appointment)
        db_session.commit()
        
        # Test relationships
        db_session.refresh(sample_patient)
        db_session.refresh(sample_doctor)
        
        assert len(sample_patient.patient_appointments) == 1
        assert len(sample_doctor.doctor_appointments) == 1
        assert sample_patient.patient_appointments[0].doctor == sample_doctor

class TestAppointmentModel:
    """Test cases for Appointment model"""
    
    def test_create_appointment(self, db_session, sample_patient, sample_doctor):
        """Test creating an appointment"""
        appointment_date = datetime(2024, 12, 25, 10, 30)
        appointment = Appointment(
            patient_id=sample_patient.user_id,
            doctor_id=sample_doctor.user_id,
            appointment_date=appointment_date,
            status="scheduled"
        )
        
        db_session.add(appointment)
        db_session.commit()
        db_session.refresh(appointment)
        
        assert appointment.appointment_id is not None
        assert appointment.patient_id == sample_patient.user_id
        assert appointment.doctor_id == sample_doctor.user_id
        assert appointment.appointment_date == appointment_date
        assert appointment.status == "scheduled"
        assert appointment.created_at is not None
    
    def test_appointment_relationships(self, db_session, sample_patient, sample_doctor):
        """Test appointment relationships with users"""
        appointment = Appointment(
            patient_id=sample_patient.user_id,
            doctor_id=sample_doctor.user_id,
            appointment_date=datetime.now(),
            status="completed"
        )
        
        db_session.add(appointment)
        db_session.commit()
        db_session.refresh(appointment)
        
        assert appointment.patient.email == sample_patient.email
        assert appointment.doctor.email == sample_doctor.email
        assert appointment.patient.role == "patient"
        assert appointment.doctor.role == "doctor"

class TestPrescriptionModel:
    """Test cases for Prescription model"""
    
    def test_create_prescription(self, db_session, sample_patient, sample_doctor):
        """Test creating a prescription"""
        prescription = Prescription(
            patient_id=sample_patient.user_id,
            doctor_id=sample_doctor.user_id,
            medication_name="Aspirin",
            dosage="100mg",
            frequency="Once daily",
            start_date=date.today()
        )
        
        db_session.add(prescription)
        db_session.commit()
        db_session.refresh(prescription)
        
        assert prescription.prescription_id is not None
        assert prescription.medication_name == "Aspirin"
        assert prescription.dosage == "100mg"
        assert prescription.frequency == "Once daily"
        assert prescription.start_date == date.today()
    
    def test_prescription_relationships(self, db_session, sample_patient, sample_doctor):
        """Test prescription relationships"""
        prescription = Prescription(
            patient_id=sample_patient.user_id,
            doctor_id=sample_doctor.user_id,
            medication_name="Lisinopril",
            dosage="10mg"
        )
        
        db_session.add(prescription)
        db_session.commit()
        db_session.refresh(prescription)
        
        assert prescription.patient == sample_patient
        assert prescription.doctor == sample_doctor

class TestReminderModel:
    """Test cases for Reminder model"""
    
    def test_create_reminder(self, db_session, sample_patient):
        """Test creating a reminder"""
        reminder_time = datetime(2024, 12, 25, 9, 0)
        reminder = Reminder(
            patient_id=sample_patient.user_id,
            type="medication",
            reference_id=1,
            reminder_time=reminder_time,
            status="pending"
        )
        
        db_session.add(reminder)
        db_session.commit()
        db_session.refresh(reminder)
        
        assert reminder.reminder_id is not None
        assert reminder.type == "medication"
        assert reminder.reference_id == 1
        assert reminder.reminder_time == reminder_time
        assert reminder.status == "pending"
    
    def test_reminder_patient_relationship(self, db_session, sample_patient):
        """Test reminder relationship with patient"""
        reminder = Reminder(
            patient_id=sample_patient.user_id,
            type="appointment",
            reminder_time=datetime.now(),
            status="sent"
        )
        
        db_session.add(reminder)
        db_session.commit()
        db_session.refresh(reminder)
        
        assert reminder.patient == sample_patient
        assert reminder in sample_patient.reminders

class TestCallLogModel:
    """Test cases for CallLog model"""
    
    def test_create_call_log(self, db_session, sample_patient):
        """Test creating a call log"""
        call_time = datetime.now()
        call_log = CallLog(
            patient_id=sample_patient.user_id,
            call_type="consultation",
            call_time=call_time,
            call_status="completed",
            notes="Patient discussed symptoms and medication concerns."
        )
        
        db_session.add(call_log)
        db_session.commit()
        db_session.refresh(call_log)
        
        assert call_log.call_id is not None
        assert call_log.call_type == "consultation"
        assert call_log.call_time == call_time
        assert call_log.call_status == "completed"
        assert call_log.notes is not None
    
    def test_call_log_patient_relationship(self, db_session, sample_patient):
        """Test call log relationship with patient"""
        call_log = CallLog(
            patient_id=sample_patient.user_id,
            call_type="emergency",
            call_time=datetime.now(),
            call_status="answered"
        )
        
        db_session.add(call_log)
        db_session.commit()
        db_session.refresh(call_log)
        
        assert call_log.patient == sample_patient
        assert call_log in sample_patient.call_logs

class TestModelIntegration:
    """Test cases for model integration and complex relationships"""
    
    def test_patient_full_workflow(self, db_session, sample_patient, sample_doctor):
        """Test complete patient workflow with all models"""
        # Create appointment
        appointment = Appointment(
            patient_id=sample_patient.user_id,
            doctor_id=sample_doctor.user_id,
            appointment_date=datetime.now(),
            status="completed"
        )
        db_session.add(appointment)
        
        # Create prescription
        prescription = Prescription(
            patient_id=sample_patient.user_id,
            doctor_id=sample_doctor.user_id,
            medication_name="Metformin",
            dosage="500mg"
        )
        db_session.add(prescription)
        
        # Create reminder
        reminder = Reminder(
            patient_id=sample_patient.user_id,
            type="medication",
            reference_id=prescription.prescription_id,
            reminder_time=datetime.now(),
            status="pending"
        )
        db_session.add(reminder)
        
        # Create call log
        call_log = CallLog(
            patient_id=sample_patient.user_id,
            call_type="follow-up",
            call_time=datetime.now(),
            call_status="completed"
        )
        db_session.add(call_log)
        
        db_session.commit()
        db_session.refresh(sample_patient)
        
        # Verify all relationships
        assert len(sample_patient.patient_appointments) == 1
        assert len(sample_patient.patient_prescriptions) == 1
        assert len(sample_patient.reminders) == 1
        assert len(sample_patient.call_logs) == 1
    
    def test_doctor_patient_relationships(self, db_session, sample_doctor):
        """Test doctor managing multiple patients"""
        # Create multiple patients
        patient1 = User(
            first_name="Patient",
            last_name="One",
            email="patient1@test.com",
            password_hash=hash_password("pass123"),
            role="patient"
        )
        patient2 = User(
            first_name="Patient",
            last_name="Two",
            email="patient2@test.com",
            password_hash=hash_password("pass123"),
            role="patient"
        )
        
        db_session.add_all([patient1, patient2])
        db_session.commit()
        
        # Create appointments with both patients
        appointment1 = Appointment(
            patient_id=patient1.user_id,
            doctor_id=sample_doctor.user_id,
            appointment_date=datetime.now(),
            status="scheduled"
        )
        appointment2 = Appointment(
            patient_id=patient2.user_id,
            doctor_id=sample_doctor.user_id,
            appointment_date=datetime.now(),
            status="completed"
        )
        
        db_session.add_all([appointment1, appointment2])
        db_session.commit()
        db_session.refresh(sample_doctor)
        
        # Verify doctor has appointments with both patients
        assert len(sample_doctor.doctor_appointments) == 2
        patient_ids = [apt.patient_id for apt in sample_doctor.doctor_appointments]
        assert patient1.user_id in patient_ids
        assert patient2.user_id in patient_ids

if __name__ == "__main__":
    pytest.main([__file__])
