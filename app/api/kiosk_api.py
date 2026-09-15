from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.database import get_db
from app.database.models import HospitalLocation, Department

router = APIRouter(prefix="/api/kiosk", tags=["Entrance Kiosk"])

class KioskQuery(BaseModel):
    query: str

@router.post("/search")
def kiosk_search(data: KioskQuery, db: Session = Depends(get_db)):
    q = data.query.lower()
    locations = db.query(HospitalLocation).all()
    for loc in locations:
        if loc.name_ml in q or loc.name_en.lower() in q or loc.category.lower() in q:
            return {
                "found": True,
                "name_ml": loc.name_ml,
                "name_en": loc.name_en,
                "floor": loc.floor,
                "block": loc.block,
                "directions_ml": loc.directions_ml,
                "voice_response": f"{loc.name_ml} {loc.floor}-ലാണ്. {loc.directions_ml}"
            }
    
    # Default search department
    depts = db.query(Department).all()
    for d in depts:
        if d.name_ml in q or d.code.lower() in q or d.name_en.lower() in q:
            return {
                "found": True,
                "name_ml": d.name_ml,
                "name_en": d.name_en,
                "floor": d.floor,
                "room": d.room_number,
                "directions_ml": f"{d.name_ml} {d.floor}-ൽ റൂം നമ്പർ {d.room_number}-ലാണ്. {d.description_ml}",
                "voice_response": f"{d.name_ml} {d.floor}-ൽ റൂം നമ്പർ {d.room_number}-ലാണ്."
            }

    return {
        "found": False,
        "voice_response": "ക്ഷമിക്കണം, നിർദ്ദിഷ്ട വിഭാഗം കണ്ടെത്തിയില്ല. ദയവായി മെയിൻ റിസപ്ഷൻ ഡെസ്കിൽ ബന്ധപ്പെടുക."
    }
