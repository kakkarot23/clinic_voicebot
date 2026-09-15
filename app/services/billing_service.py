from sqlalchemy.orm import Session
from app.database.models import BillingRecord, Patient

class BillingService:
    @staticmethod
    def get_patient_bill(db: Session, phone_or_code: str):
        patient = db.query(Patient).filter((Patient.phone == phone_or_code) | (Patient.patient_code == phone_or_code.upper())).first()
        if not patient:
            return None
        bill = db.query(BillingRecord).filter_by(patient_id=patient.id).order_by(BillingRecord.created_at.desc()).first()
        return bill
