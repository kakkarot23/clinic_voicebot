from sqlalchemy.orm import Session
from app.database.models import Patient
import random

class PatientService:
    @staticmethod
    def get_by_phone(db: Session, phone: str):
        return db.query(Patient).filter(Patient.phone.like(f"%{phone}%")).first()

    @staticmethod
    def get_by_code(db: Session, code: str):
        return db.query(Patient).filter(Patient.patient_code == code.upper()).first()

    @staticmethod
    def create_patient(db: Session, name: str, phone: str, gender: str = "Unspecified", dob: str = None, address: str = None):
        code = f"KMC-{random.randint(1000, 9999)}"
        patient = Patient(
            patient_code=code,
            name=name,
            phone=phone,
            gender=gender,
            dob=dob,
            address=address
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient
