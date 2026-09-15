from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.database import get_db
from app.api.voice_api import process_voice_input, VoiceProcessRequest

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp Bot Integration"])

class WhatsAppMsgRequest(BaseModel):
    phone: str = "9876543210"
    message_text: str

@router.post("/send")
async def handle_whatsapp_message(req: WhatsAppMsgRequest, db: Session = Depends(get_db)):
    voice_req = VoiceProcessRequest(
        session_id=f"wa_{req.phone}",
        caller_phone=req.phone,
        user_speech_text=req.message_text
    )
    res = await process_voice_input(voice_req, db)
    return {
        "reply_text_ml": res["bot_response_ml"],
        "intent": res["intent"],
        "status": "SENT"
    }
