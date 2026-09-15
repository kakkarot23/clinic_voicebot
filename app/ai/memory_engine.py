from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.database.models import Patient, Appointment, LabOrder, BillingRecord

class MemoryEngine:
    _short_term_memory: Dict[str, List[dict]] = {}

    @classmethod
    def add_short_term_turn(cls, session_id: str, sender: str, text: str, intent: str = None, entities: dict = None):
        if session_id not in cls._short_term_memory:
            cls._short_term_memory[session_id] = []
        cls._short_term_memory[session_id].append({
            "sender": sender,
            "text": text,
            "intent": intent,
            "entities": entities or {}
        })

    @classmethod
    def get_short_term_history(cls, session_id: str, max_turns: int = 5) -> List[dict]:
        return cls._short_term_memory.get(session_id, [])[-max_turns:]

    @classmethod
    def get_long_term_patient_memory(cls, db: Session, phone: str) -> dict:
        patient = db.query(Patient).filter(Patient.phone == phone).first()
        if not patient:
            return {"recognized": False}
            
        recent_appointment = db.query(Appointment).filter_by(patient_id=patient.id).order_by(Appointment.created_at.desc()).first()
        recent_lab = db.query(LabOrder).filter_by(patient_id=patient.id).order_by(LabOrder.created_at.desc()).first()
        recent_bill = db.query(BillingRecord).filter_by(patient_id=patient.id).order_by(BillingRecord.created_at.desc()).first()

        return {
            "recognized": True,
            "patient_code": patient.patient_code,
            "name": patient.name,
            "phone": patient.phone,
            "insurance": patient.insurance_info,
            "recent_appointment": recent_appointment.appointment_number if recent_appointment else None,
            "recent_lab_order": recent_lab.order_number if recent_lab else None,
            "recent_bill_status": recent_bill.status if recent_bill else None
        }
