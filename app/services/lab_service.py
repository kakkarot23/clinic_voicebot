from sqlalchemy.orm import Session
from app.database.models import LabOrder, LabReport, Patient

class LabService:
    @staticmethod
    def get_lab_status(db: Session, phone_or_code: str):
        patient = db.query(Patient).filter((Patient.phone == phone_or_code) | (Patient.patient_code == phone_or_code.upper())).first()
        if not patient:
            return None
        order = db.query(LabOrder).filter_by(patient_id=patient.id).order_by(LabOrder.created_at.desc()).first()
        return order
