from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.database import get_db
from app.database.models import Department, Doctor, HospitalKnowledgeBase

router = APIRouter(prefix="/api/admin", tags=["Admin Portal"])

class AddDoctorRequest(BaseModel):
    name_ml: str
    name_en: str
    department_id: int
    specialization_ml: str
    fee: float = 500.0
    room_number: str = "101"

@router.post("/doctors")
def create_doctor(req: AddDoctorRequest, db: Session = Depends(get_db)):
    doc = Doctor(
        name_ml=req.name_ml,
        name_en=req.name_en,
        department_id=req.department_id,
        specialization_ml=req.specialization_ml,
        consultation_fee=req.fee,
        room_number=req.room_number
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"status": "SUCCESS", "doctor_id": doc.id, "message": "Doctor added to hospital database"}
