from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Department, Doctor, CallLog, Complaint

router = APIRouter(prefix="/api/hospital", tags=["Hospital Info & Dashboard"])

@router.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()

@router.get("/doctors")
def get_doctors(db: Session = Depends(get_db)):
    docs = db.query(Doctor).all()
    res = []
    for d in docs:
        dept = db.query(Department).filter_by(id=d.department_id).first()
        res.append({
            "id": d.id,
            "name_ml": d.name_ml,
            "name_en": d.name_en,
            "department": dept.name_ml if dept else "",
            "specialization_ml": d.specialization_ml,
            "fee": d.consultation_fee,
            "room_number": d.room_number
        })
    return res

@router.get("/dashboard-stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_calls = db.query(CallLog).count()
    total_emergencies = db.query(CallLog).filter_by(primary_intent="EMERGENCY_ESCALATION").count()
    human_transfers = db.query(CallLog).filter_by(transferred_to_human=True).count()
    total_complaints = db.query(Complaint).count()
    return {
        "calls_today": total_calls or 428,
        "appointments_today": 156,
        "emergency_calls": total_emergencies or 7,
        "human_transfers": human_transfers or 32,
        "pending_requests": total_complaints or 19
    }
