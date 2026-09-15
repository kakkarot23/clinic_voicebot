from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
import asyncio

from app.database.database import get_db
from app.database.models import CallLog, CallTranscript, Patient, Doctor, Department, Appointment, Complaint
from app.ai.nlp_engine import MalayalamNLPEngine
from app.ai.intent_classifier import IntentClassifier
from app.ai.safety_layer import SafetyLayer
from app.ai.conversation_manager import ConversationManager
from app.ai.responses_ml import HospitalResponses
from app.voice.tts_handler import TTSHandler
from app.services.appointment_service import AppointmentService
from app.services.patient_service import PatientService
from app.services.emergency_service import EmergencyService
from app.services.billing_service import BillingService
from app.services.lab_service import LabService
from app.services.hospital_service import HospitalService
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/api/voice", tags=["Voice Engine"])

class VoiceProcessRequest(BaseModel):
    session_id: Optional[str] = None
    caller_phone: str = "9876543210"
    user_speech_text: str
    language: Optional[str] = None # "ml" or "en"

@router.post("/process")
async def process_voice_input(req: VoiceProcessRequest, db: Session = Depends(get_db)):
    session = ConversationManager.get_or_create_session(req.session_id, req.caller_phone)
    raw_text = req.user_speech_text
    
    # Language Detection
    lang = req.language or MalayalamNLPEngine.detect_language(raw_text)

    # 1. Safety Check
    safety_res = SafetyLayer.check_safety(raw_text)
    if safety_res["is_emergency"]:
        bot_response = safety_res["response_ml"] if lang == "ml" else "This may be a medical emergency! Please stay on the line while we immediately transfer your call to our Emergency Care & Trauma Desk."
        session.add_transcript("USER", raw_text)
        session.add_transcript("SYSTEM", bot_response)
        
        # Log Emergency Call
        EmergencyService.handle_emergency_trigger(db, req.caller_phone, safety_res["trigger"])
        
        return {
            "session_id": session.session_id,
            "language": lang,
            "intent": "EMERGENCY_ESCALATION",
            "is_emergency": True,
            "bot_response": bot_response,
            "bot_response_ml": bot_response,
            "transferred_to": "EMERGENCY_DESK_108",
            "caller_phone": req.caller_phone
        }

    # 2. Text Normalization & Entity Extraction
    normalized_text = MalayalamNLPEngine.normalize_text(raw_text)
    entities = MalayalamNLPEngine.extract_entities(raw_text)
    
    if entities["doctor_name"]:
        session.selected_doctor = entities["doctor_name"]
    if entities["department_code"]:
        session.selected_department = entities["department_code"]
    if entities["time_slot"]:
        session.selected_time = entities["time_slot"]

    # 3. Intent Classification
    intent = IntentClassifier.classify(raw_text)
    session.current_intent = intent
    
    bot_response = ""
    transferred = False
    transfer_dept = None
    call_summary = ""

    # 4. Intent Execution Logic
    if intent == "GREETING":
        bot_response = HospitalResponses.GREETING_ML if lang == "ml" else HospitalResponses.GREETING_EN

    elif intent == "BOOK_APPOINTMENT":
        if not session.selected_doctor and not session.selected_department:
            bot_response = HospitalResponses.ASK_DOCTOR_OR_DEPT_ML if lang == "ml" else HospitalResponses.ASK_DOCTOR_OR_DEPT_EN
            session.pending_slot = "NEEDS_DOCTOR"
        elif session.selected_doctor and not session.selected_time:
            if lang == "ml":
                bot_response = f"{session.selected_doctor} ഡോക്ടർ കാണുന്ന സമയങ്ങൾ: രാവിലെ 10:00, 10:30, 11:30. നിങ്ങൾക്ക് ഏത് സമയമാണ് സൗകര്യം?"
            else:
                bot_response = f"{session.selected_doctor} is available tomorrow at 10:00 AM, 10:30 AM, and 11:30 AM. Which time slot do you prefer?"
            session.pending_slot = "NEEDS_TIME"
        elif session.selected_doctor and session.selected_time:
            patient = PatientService.get_by_phone(db, req.caller_phone)
            if not patient:
                patient = PatientService.create_patient(db, name="Caller (New Patient)", phone=req.caller_phone)
            
            doc = db.query(Doctor).filter(Doctor.name_en.ilike(f"%{session.selected_doctor}%") | Doctor.name_ml.ilike(f"%{session.selected_doctor}%")).first()
            doc_id = doc.id if doc else 2
            
            app_rec = AppointmentService.book_appointment(
                db, patient_id=patient.id, doctor_id=doc_id, date_str="2026-09-16", time_slot=session.selected_time
            )
            
            if lang == "ml":
                bot_response = HospitalResponses.BOOKING_CONFIRMED_ML.format(
                    app_num=app_rec.appointment_number, phone=req.caller_phone
                )
            else:
                bot_response = HospitalResponses.BOOKING_CONFIRMED_EN.format(
                    app_num=app_rec.appointment_number, phone=req.caller_phone
                )
            NotificationService.send_appointment_sms(req.caller_phone, doc.name_en if doc else session.selected_doctor, "16 Sept 2026", session.selected_time, app_rec.appointment_number)
            call_summary = f"Appointment Booked: {doc.name_en if doc else session.selected_doctor}, 16 Sept, {session.selected_time} - Confirmed"

    elif intent == "DOCTOR_AVAILABILITY":
        docs = db.query(Doctor).all()
        doc_list_ml = ", ".join([d.name_ml for d in docs[:3]])
        doc_list_en = ", ".join([d.name_en for d in docs[:3]])
        if lang == "ml":
            bot_response = f"ഞങ്ങളുടെ ആശുപത്രിയിൽ {doc_list_ml} തുടങ്ങി മികച്ച സ്പെഷ്യലിസ്റ്റ് ഡോക്ടർമാർ ലഭ്യമാണ്. നിങ്ങൾക്ക് ഏത് വിഭാഗമാണ് വേണ്ടത്?"
        else:
            bot_response = f"Our hospital features specialist consultants including {doc_list_en}. Which department are you looking for?"

    elif intent == "DEPARTMENT_INFO":
        if lang == "ml":
            bot_response = "ഞങ്ങളുടെ ആശുപത്രിയിൽ എമർജൻസി, കാർഡിയോളജി, ന്യൂറോളജി, ഓർത്തോപീഡിക്സ്, ഗൈനക്കോളജി, പീഡിയാട്രിക്സ്, ജനറൽ മെഡിസിൻ, ലാബ്, ഫാർമസി തുടങ്ങി എല്ലാ പ്രധാന വിഭാഗങ്ങളും ലഭ്യമാണ്."
        else:
            bot_response = "Our hospital departments include Emergency, Cardiology, Neurology, Orthopedics, Gynecology, Pediatrics, General Medicine, Radiology, Laboratory, and Pharmacy."

    elif intent == "LAB_REPORT_STATUS":
        lab_order = LabService.get_lab_status(db, req.caller_phone)
        if lab_order and lab_order.report_ready:
            if lang == "ml":
                bot_response = f"നിങ്ങളുടെ {lab_order.test_name_ml} റിപ്പോർട്ട് റെഡിയായിട്ടുണ്ട്. ഡൗൺലോഡ് ചെയ്യാനുള്ള ലിങ്ക് നിങ്ങളുടെ രജിസ്റ്റർ ചെയ്ത മൊബൈൽ നമ്പറിലേക്ക് SMS അയച്ചിട്ടുണ്ട്."
            else:
                bot_response = f"Your lab report for {lab_order.test_name_en} is ready. A secure download link has been sent to your registered mobile number."
        else:
            if lang == "ml":
                bot_response = "നിങ്ങളുടെ ലാബ് പരിശോധനാ ഫലം പ്രോസസ്സ് ചെയ്ത് കൊണ്ടിരിക്കുകയാണ്. ഉടൻ തന്നെ ലഭ്യമാകും."
            else:
                bot_response = "Your lab order is currently under review by our pathologists. It will be ready shortly."

    elif intent == "BILLING_ENQUIRY":
        bill = BillingService.get_patient_bill(db, req.caller_phone)
        if bill:
            if lang == "ml":
                bot_response = f"നിങ്ങളുടെ നിലവിലെ ബിൽ തുക {bill.total_amount} രൂപയാണ്. സ്റ്റാറ്റസ്: {bill.status}. ഓൺലൈനായി അടയ്ക്കാനുള്ള ലിങ്ക് അയച്ചിട്ടുണ്ട്."
            else:
                bot_response = f"Your current outstanding bill is ₹{bill.total_amount}. Payment Status: {bill.status}. An online payment link has been sent to your phone."
        else:
            if lang == "ml":
                bot_response = "നിങ്ങൾക്ക് നിലവിൽ കുടിശ്ശിക ബില്ലുകൾ ഒന്നും ലഭ്യമല്ല."
            else:
                bot_response = "You have no outstanding bills pending at this time."

    elif intent == "LOCATION_NAVIGATION" or intent == "PARKING_INFO":
        kb = HospitalService.search_knowledge_base(db, raw_text)
        if kb:
            bot_response = kb.answer_ml if lang == "ml" else kb.answer_en
        else:
            if lang == "ml":
                bot_response = "കേരള മെഡിക്കൽ സെന്റർ കൊച്ചി ബൈപാസ് റോഡിൽ വൈറ്റിലയിലാണ് സ്ഥിതി ചെയ്യുന്നത്. ബേസ്മെന്റ് 2-ൽ സൗജന്യ പാർക്കിംഗ് ലഭ്യമാണ്."
            else:
                bot_response = "Kerala Medical Center is located on Bypass Road, Vyttila, Kochi. Free parking is available in Basement Level 2."

    elif intent == "HUMAN_AGENT_TRANSFER":
        bot_response = HospitalResponses.HUMAN_TRANSFER_ML if lang == "ml" else HospitalResponses.HUMAN_TRANSFER_EN
        transferred = True
        transfer_dept = "FRONT_DESK"

    elif intent == "COMPLAINT_FEEDBACK":
        c_code = f"CMP-{uuid.uuid4().hex[:6].upper()}"
        new_c = Complaint(
            ticket_code=c_code,
            caller_phone=req.caller_phone,
            department="FRONT_OFFICE",
            category="GENERAL",
            description=raw_text
        )
        db.add(new_c)
        db.commit()
        if lang == "ml":
            bot_response = f"നിങ്ങളുടെ പരാതി വിജയകരമായി രജിസ്റ്റർ ചെയ്തു. ടിക്കറ്റ് നമ്പർ: {c_code}. ഫ്രണ്ട് ഓഫീസ് ടീം ഉടൻ പരിശോധിച്ച് നടപടി സ്വീകരിക്കും."
        else:
            bot_response = f"Your feedback/complaint has been registered under Ticket ID: {c_code}. Our front office manager will address it promptly."

    else:
        bot_response = HospitalResponses.UNKNOWN_RETRY_ML if lang == "ml" else HospitalResponses.UNKNOWN_RETRY_EN

    session.add_transcript("USER", raw_text)
    session.add_transcript("SYSTEM", bot_response)

    call_id = f"CALL-{session.session_id[:8]}"
    log_rec = db.query(CallLog).filter_by(call_id=call_id).first()
    if not log_rec:
        log_rec = CallLog(
            call_id=call_id,
            caller_phone=req.caller_phone,
            language=lang,
            primary_intent=intent,
            call_summary_ml=call_summary or f"Call Intent: {intent}",
            transferred_to_human=transferred,
            transfer_department=transfer_dept
        )
        db.add(log_rec)
        db.commit()

    return {
        "session_id": session.session_id,
        "language": lang,
        "intent": intent,
        "entities": entities,
        "bot_response": bot_response,
        "bot_response_ml": bot_response,
        "transferred_to_human": transferred,
        "caller_phone": req.caller_phone,
        "context": {
            "doctor": session.selected_doctor,
            "department": session.selected_department,
            "time": session.selected_time
        }
    }

@router.get("/tts")
async def get_tts_audio(text: str, lang: str = "ml"):
    """
    Returns live MP3 audio stream for given text (Malayalam or English)
    """
    audio_bytes = await TTSHandler.generate_malayalam_audio(text)
    return Response(content=audio_bytes, media_type="audio/mpeg")
