from sqlalchemy.orm import Session
from app.database.models import CallLog, Complaint
import uuid
from datetime import datetime

class EmergencyService:
    @staticmethod
    def handle_emergency_trigger(db: Session, phone: str, trigger_word: str):
        call_id = f"EMG-{str(uuid.uuid4())[:8]}"
        call_log = CallLog(
            call_id=call_id,
            caller_phone=phone,
            language="ml",
            primary_intent="EMERGENCY_ESCALATION",
            call_summary_ml=f"അടിയന്തര സാഹചര്യ കണ്ടെത്തൽ: '{trigger_word}'. എമർജൻസി ട്രോമ ഡെസ്കിലേക്ക് കണക്ട് ചെയ്തു.",
            transferred_to_human=True,
            transfer_department="EMERGENCY_TRAUMA"
        )
        db.add(call_log)
        db.commit()
        return {
            "status": "ESCALATED",
            "call_id": call_id,
            "message_ml": "ഇത് അടിയന്തര സാഹചര്യമാകാം. ഉടൻ എമർജൻസി കെയർ കൗണ്ടറുമായി ബന്ധിപ്പിക്കുന്നു. ദയവായി ലൈനിൽ തുടരുക.",
            "emergency_num": "+91 484 2999999 / 108"
        }
