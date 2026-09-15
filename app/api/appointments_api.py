from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Appointment, Doctor, Department, Patient

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])

@router.get("/")
def get_all_appointments(db: Session = Depends(get_db)):
    appointments = db.query(Appointment).order_by(Appointment.created_at.desc()).all()
    results = []
    for app in appointments:
        doc = db.query(Doctor).filter_by(id=app.doctor_id).first()
        pat = db.query(Patient).filter_by(id=app.patient_id).first()
        results.append({
            "id": app.id,
            "appointment_number": app.appointment_number,
            "patient_name": pat.name if pat else "Unknown",
            "patient_phone": pat.phone if pat else "",
            "doctor_name": doc.name_ml if doc else "Dr. Meera",
            "date": app.date,
            "time_slot": app.time_slot,
            "status": app.status
        })
    return results
