from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship, declarative_base
from .base import Base  # Import Base from the local base module

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # Allow table to be extended if it exists

    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    dob = Column(Date, nullable=True)
    phone_number = Column(String(20), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    address = Column(Text, nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default='patient')  # 'patient', 'doctor', 'admin'
    specialty = Column(String(100), nullable=True)  # For doctors
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Define relationships with explicit back_populates
    patient_appointments = relationship("Appointment", 
                                      foreign_keys="Appointment.patient_id", 
                                      back_populates="patient")
    doctor_appointments = relationship("Appointment", 
                                      foreign_keys="Appointment.doctor_id", 
                                      back_populates="doctor")
    patient_prescriptions = relationship("Prescription", 
                                        foreign_keys="Prescription.patient_id", 
                                        back_populates="patient")
    doctor_prescriptions = relationship("Prescription", 
                                       foreign_keys="Prescription.doctor_id", 
                                       back_populates="doctor")
    reminders = relationship("Reminder", back_populates="patient")
    call_logs = relationship("CallLog", back_populates="patient")

    # Relationships for a user as a patient
    patient_appointments = relationship("Appointment", foreign_keys='Appointment.patient_id', back_populates="patient")
    patient_prescriptions = relationship("Prescription", foreign_keys='Prescription.patient_id', back_populates="patient")
    reminders = relationship("Reminder", back_populates="patient")
    call_logs = relationship("CallLog", back_populates="patient")

    # Relationships for a user as a doctor
    doctor_appointments = relationship("Appointment", foreign_keys='Appointment.doctor_id', back_populates="doctor")
    doctor_prescriptions = relationship("Prescription", foreign_keys='Prescription.doctor_id', back_populates="doctor")

class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = {'extend_existing': True}  # Allow table to be extended if it exists

    appointment_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Define relationships with explicit back_populates
    patient = relationship("User", foreign_keys=[patient_id], back_populates="patient_appointments")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_appointments")

class Prescription(Base):
    __tablename__ = "prescriptions"
    __table_args__ = {'extend_existing': True}  # Allow table to be extended if it exists

    prescription_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    medication_name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=True)
    frequency = Column(String(100), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Define relationships with explicit back_populates
    patient = relationship("User", foreign_keys=[patient_id], back_populates="patient_prescriptions")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_prescriptions")

class Reminder(Base):
    __tablename__ = "reminders"
    __table_args__ = {'extend_existing': True}  # Allow table to be extended if it exists

    reminder_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    type = Column(String(50), nullable=False)  # 'appointment', 'medication', etc.
    reference_id = Column(Integer, nullable=True)  # ID of the appointment or prescription
    reminder_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), nullable=True)  # 'pending', 'sent', 'cancelled'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Define relationship with explicit back_populates
    patient = relationship("User", back_populates="reminders")

class CallLog(Base):
    __tablename__ = "call_logs"
    __table_args__ = {'extend_existing': True}  # Allow table to be extended if it exists

    call_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    call_type = Column(String(50), nullable=True)  # 'incoming', 'outgoing', 'missed'
    call_time = Column(DateTime(timezone=True), nullable=False)
    call_status = Column(String(50), nullable=True)  # 'completed', 'failed', 'no-answer'
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Define relationship with explicit back_populates
    patient = relationship("User", back_populates="call_logs")
