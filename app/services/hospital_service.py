from sqlalchemy.orm import Session
from app.database.models import Department, Doctor, HospitalKnowledgeBase, HospitalLocation

class HospitalService:
    @staticmethod
    def get_departments(db: Session):
        return db.query(Department).filter_by(is_active=True).all()

    @staticmethod
    def get_doctors_by_department(db: Session, dept_id: int):
        return db.query(Doctor).filter_by(department_id=dept_id).all()

    @staticmethod
    def search_knowledge_base(db: Session, query_text: str):
        kb_items = db.query(HospitalKnowledgeBase).all()
        for item in kb_items:
            if item.key_phrase_ml in query_text or (item.category and item.category.lower() in query_text.lower()):
                return item
        return None

    @staticmethod
    def get_location_directions(db: Session, query_text: str):
        locations = db.query(HospitalLocation).all()
        for loc in locations:
            if loc.name_ml in query_text or loc.category.lower() in query_text.lower():
                return loc
        return None
