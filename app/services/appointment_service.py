from sqlalchemy.orm import Session
from app.database.models import Appointment, Doctor, Department, Patient, DoctorSchedule
from datetime import datetime, timedelta
import random

class AppointmentService:
    @staticmethod
    def get_available_doctors(db: Session, dept_code: str = None, doc_name: str = None):
        query = db.query(Doctor)
        if dept_code:
            dept = db.query(Department).filter_by(code=dept_code).first()
            if dept:
                query = query.filter(Doctor.department_id == dept.id)
        if doc_name:
            query = query.filter(Doctor.name_en.ilike(f"%{doc_name}%") | Doctor.name_ml.ilike(f"%{doc_name}%"))
        return query.all()

    @staticmethod
    def get_doctor_slots(db: Session, doctor_id: int, date_str: str = None):
        if not date_str:
            date_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
        doc = db.query(Doctor).filter_by(id=doctor_id).first()
        if not doc:
            return []
            
        # Default slots if not specified
        return ["09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "12:00 PM"]

    @staticmethod
    def book_appointment(db: Session, patient_id: int, doctor_id: int, date_str: str, time_slot: str, notes: str = None):
        doc = db.query(Doctor).filter_by(id=doctor_id).first()
        if not doc:
            raise ValueError("Doctor not found")
            
        app_num = f"APT-{datetime.now().strftime('%Y%m%d')}-{random.randint(100, 999)}"
        new_app = Appointment(
            appointment_number=app_num,
            patient_id=patient_id,
            doctor_id=doctor_id,
            department_id=doc.department_id,
            date=date_str,
            time_slot=time_slot,
            status="CONFIRMED",
            notes=notes
        )
        db.add(new_app)
        db.commit()
        db.refresh(new_app)
        return new_app
