from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_code = Column(String(50), unique=True, index=True)
    name = Column(String(100), nullable=False)
    dob = Column(String(20))
    gender = Column(String(20))
    phone = Column(String(20), index=True)
    address = Column(Text)
    email = Column(String(100))
    emergency_contact = Column(String(50))
    insurance_info = Column(String(200))
    preferred_language = Column(String(10), default="ml")
    registered_at = Column(DateTime, default=datetime.utcnow)
    
    appointments = relationship("Appointment", back_populates="patient")
    lab_orders = relationship("LabOrder", back_populates="patient")
    billing_records = relationship("BillingRecord", back_populates="patient")

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name_ml = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, index=True)
    floor = Column(String(50))
    room_number = Column(String(50))
    description_ml = Column(Text)
    is_active = Column(Boolean, default=True)
    
    doctors = relationship("Doctor", back_populates="department")

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    name_ml = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    specialization_ml = Column(String(150))
    qualifications = Column(String(150))
    consultation_fee = Column(Float, default=500.0)
    follow_up_fee = Column(Float, default=300.0)
    room_number = Column(String(50))
    photo_url = Column(String(255))
    teleconsultation_available = Column(Boolean, default=True)
    
    department = relationship("Department", back_populates="doctors")
    schedules = relationship("DoctorSchedule", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")

class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    day_of_week = Column(String(20)) # "Monday", "Tuesday", etc. or "ചൊവ്വ", "വ്യാഴം"
    start_time = Column(String(20)) # e.g. "09:00 AM"
    end_time = Column(String(20)) # e.g. "01:00 PM"
    slot_duration_mins = Column(Integer, default=30)
    max_patients = Column(Integer, default=15)
    
    doctor = relationship("Doctor", back_populates="schedules")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_number = Column(String(50), unique=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    date = Column(String(20)) # YYYY-MM-DD
    time_slot = Column(String(20)) # e.g. "10:30 AM"
    status = Column(String(30), default="BOOKED") # BOOKED, CONFIRMED, CANCELLED, RESCHEDULED, COMPLETED
    consultation_type = Column(String(20), default="IN_PERSON") # IN_PERSON, VIDEO
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")

class LabOrder(Base):
    __tablename__ = "lab_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    test_name_ml = Column(String(150))
    test_name_en = Column(String(150))
    price = Column(Float)
    preparation_instructions_ml = Column(Text)
    fasting_required = Column(Boolean, default=False)
    lab_timings = Column(String(100), default="24x7 Emergency / 7:00 AM - 6:00 PM Routine")
    sample_collection_type = Column(String(50), default="LAB_VISIT") # LAB_VISIT, HOME_COLLECTION
    status = Column(String(50), default="PENDING") # PENDING, SAMPLE_COLLECTED, PROCESSING, READY
    report_ready = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="lab_orders")
    report = relationship("LabReport", back_populates="order", uselist=False)

class LabReport(Base):
    __tablename__ = "lab_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("lab_orders.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    report_summary_ml = Column(Text)
    pdf_url = Column(String(255))
    doctor_verified = Column(Boolean, default=True)
    ready_at = Column(DateTime, default=datetime.utcnow)
    
    order = relationship("LabOrder", back_populates="report")

class BillingRecord(Base):
    __tablename__ = "billing_records"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    consultation_fee = Column(Float, default=0.0)
    lab_charges = Column(Float, default=0.0)
    pharmacy_charges = Column(Float, default=0.0)
    room_charges = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    status = Column(String(20), default="PENDING") # PAID, PENDING, PARTIAL
    payment_link = Column(String(255))
    due_date = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="billing_records")

class AdmissionRecord(Base):
    __tablename__ = "admission_records"
    
    id = Column(Integer, primary_key=True, index=True)
    admission_number = Column(String(50), unique=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    room_type = Column(String(50)) # ICU, GENERAL_WARD, PRIVATE_ROOM, SUITE
    room_number = Column(String(20))
    admission_date = Column(String(20))
    discharge_date = Column(String(20), nullable=True)
    status = Column(String(30), default="ADMITTED") # ADMITTED, DISCHARGED, DISCHARGE_PENDING

class Complaint(Base):
    __tablename__ = "complaints"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_code = Column(String(50), unique=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    caller_phone = Column(String(20))
    department = Column(String(50))
    category = Column(String(50)) # Doctor, Staff, Billing, Reception, Cleanliness, Food, Parking, Waiting time
    priority = Column(String(20), default="NORMAL") # HIGH, NORMAL, LOW
    description = Column(Text)
    status = Column(String(20), default="OPEN") # OPEN, IN_PROGRESS, RESOLVED
    created_at = Column(DateTime, default=datetime.utcnow)

class CallLog(Base):
    __tablename__ = "call_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String(50), unique=True, index=True)
    caller_phone = Column(String(20))
    language = Column(String(20), default="ml")
    primary_intent = Column(String(50))
    call_summary_ml = Column(Text)
    audio_url = Column(String(255), nullable=True)
    transferred_to_human = Column(Boolean, default=False)
    transfer_department = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    duration_seconds = Column(Integer, default=0)

class CallTranscript(Base):
    __tablename__ = "call_transcripts"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String(50), ForeignKey("call_logs.call_id"))
    sender = Column(String(10)) # USER or BOT
    text = Column(Text)
    language = Column(String(10), default="ml")
    timestamp = Column(DateTime, default=datetime.utcnow)

class HospitalKnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50)) # FAQ, PARKING, TIMINGS, LOCATION, RADIOLOGY, LAB
    key_phrase_ml = Column(String(200))
    answer_ml = Column(Text)
    answer_en = Column(Text)

class HospitalLocation(Base):
    __tablename__ = "hospital_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name_ml = Column(String(100))
    name_en = Column(String(100))
    category = Column(String(50)) # Department, Lab, Billing, ICU, Pharmacy, Parking
    floor = Column(String(20))
    room_number = Column(String(50), nullable=True)
    block = Column(String(50))
    directions_ml = Column(Text)

class PharmacyItem(Base):
    __tablename__ = "pharmacy_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    generic_name = Column(String(100))
    stock_status = Column(String(50), default="AVAILABLE")
    requires_prescription = Column(Boolean, default=True)
    price = Column(Float, default=100.0)

