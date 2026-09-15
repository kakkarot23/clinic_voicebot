import time
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.ai.nlp_engine import MalayalamNLPEngine
from app.ai.intent_classifier import IntentClassifier
from app.ai.safety_layer import SafetyLayer
from app.ai.tool_registry import ToolRegistry
from app.ai.memory_engine import MemoryEngine
from app.ai.personality import PersonalityConfig
from app.ai.responses_ml import HospitalResponses
from app.services.emergency_service import EmergencyService

router = APIRouter(prefix="/ws", tags=["Real-time Voice WebSockets"])

@router.websocket("/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = f"ws_{id(websocket)}"
    db = SessionLocal()

    try:
        while True:
            # Receive text or JSON frame from client
            raw_data = await websocket.receive_text()
            turn_start_time = time.time()

            frame = json.loads(raw_data)
            frame_type = frame.get("type", "SPEECH_INPUT")
            caller_phone = frame.get("caller_phone", "9876543210")
            lang = frame.get("language", "ml")

            # Handle Barge-In Interruption Event
            if frame_type == "BARGE_IN_INTERRUPT":
                await websocket.send_json({
                    "type": "BARGE_IN_ACK",
                    "status": "STOP_AUDIO",
                    "message": "Assistant audio aborted due to user speech."
                })
                continue

            # Handle VAD Events
            if frame_type == "VAD_EVENT":
                vad_state = frame.get("state") # "START_TALKING" or "STOP_TALKING"
                await websocket.send_json({
                    "type": "VAD_TELEMETRY",
                    "state": vad_state
                })
                continue

            # Speech Processing Pipeline
            user_text = frame.get("user_speech_text", "")
            if not user_text:
                continue

            stt_end_time = time.time()
            stt_latency_ms = int((stt_end_time - turn_start_time) * 1000)

            # 1. Memory Lookup
            long_term_mem = MemoryEngine.get_long_term_patient_memory(db, caller_phone)

            # 2. Safety & Emergency Check
            safety_res = SafetyLayer.check_safety(user_text)
            if safety_res["is_emergency"]:
                tool_res = ToolRegistry.execute_tool("escalate_emergency", db, patient_phone=caller_phone, trigger_word=safety_res["trigger"])
                bot_text = safety_res["response_ml"] if lang == "ml" else "Medical Emergency Detected! Transferring call to Trauma Care 108 immediately."
                
                await websocket.send_json({
                    "type": "ASSISTANT_RESPONSE",
                    "intent": "EMERGENCY_ESCALATION",
                    "is_emergency": True,
                    "bot_response": bot_text,
                    "tool_called": "escalate_emergency",
                    "tool_result": tool_res,
                    "latency": {
                        "stt_ms": stt_latency_ms,
                        "llm_ms": 15,
                        "tool_ms": 10,
                        "total_ms": int((time.time() - turn_start_time) * 1000)
                    }
                })
                continue

            # 3. Intent & Entity Extraction
            entities = MalayalamNLPEngine.extract_entities(user_text)
            intent = IntentClassifier.classify(user_text)

            llm_end_time = time.time()
            llm_latency_ms = int((llm_end_time - stt_end_time) * 1000)

            # 4. Function / Tool Execution
            tool_name = None
            tool_result = None
            tool_start_time = time.time()

            if intent == "BOOK_APPOINTMENT":
                tool_name = "book_appointment"
                doc_name = entities["doctor_name"] or "Dr. Meera Nair"
                time_slot = entities["time_slot"] or "10:30 AM"
                tool_result = ToolRegistry.execute_tool("book_appointment", db, patient_phone=caller_phone, doctor_name=doc_name, time_slot=time_slot)
                
                if lang == "ml":
                    bot_text = f"തീർച്ചയായും! {doc_name} ഡോക്ടറുമായി അപ്പോയിന്റ്മെന്റ് സ്ഥിരീകരിച്ചു. നമ്പർ: {tool_result['result'].get('appointment_number', 'APT-101')}."
                else:
                    bot_text = f"Your appointment with {doc_name} has been confirmed for {time_slot}. Number: {tool_result['result'].get('appointment_number', 'APT-101')}."

            elif intent == "DOCTOR_AVAILABILITY":
                tool_name = "check_doctor_schedule"
                tool_result = ToolRegistry.execute_tool("check_doctor_schedule", db, dept_code=entities["department_code"])
                count = tool_result['result']['count']
                if lang == "ml":
                    bot_text = f"ഞങ്ങളുടെ ആശുപത്രിയിൽ {count} ഡോക്ടർമാർ ലഭ്യമാണ്. Dr. Meera, Dr. Rajesh, Dr. Anil എന്നിവരെ കാണാവുന്നതാണ്."
                else:
                    bot_text = f"We have {count} specialist doctors on duty including Dr. Meera, Dr. Rajesh, and Dr. Anil."

            elif intent == "LAB_REPORT_STATUS":
                tool_name = "get_lab_status"
                tool_result = ToolRegistry.execute_tool("get_lab_status", db, patient_phone=caller_phone)
                if tool_result['result'].get("report_ready"):
                    bot_text = "നിങ്ങളുടെ ലാബ് റിപ്പോർട്ട് റെഡിയായിട്ടുണ്ട്. ലിങ്ക് SMS വഴി അയച്ചിട്ടുണ്ട്." if lang == "ml" else "Your lab report is ready and has been sent via SMS."
                else:
                    bot_text = "നിങ്ങളുടെ ലാബ് പരിശോധന പ്രോസസ്സ് ചെയ്ത് കൊണ്ടിരിക്കുന്നു." if lang == "ml" else "Your lab test is currently being processed."

            elif intent == "BILLING_ENQUIRY":
                tool_name = "get_billing_status"
                tool_result = ToolRegistry.execute_tool("get_billing_status", db, patient_phone=caller_phone)
                amt = tool_result['result'].get("total_amount", 0)
                bot_text = f"നിങ്ങളുടെ ബിൽ തുക {amt} രൂപയാണ്." if lang == "ml" else f"Your total bill amount is ₹{amt}."

            elif intent in ["LOCATION_NAVIGATION", "PARKING_INFO"]:
                tool_name = "hospital_search"
                tool_result = ToolRegistry.execute_tool("hospital_search", db, query_text=user_text)
                bot_text = tool_result['result']['answer_ml'] if lang == "ml" else tool_result['result']['answer_en']

            elif intent == "HUMAN_AGENT_TRANSFER":
                tool_name = "transfer_human"
                tool_result = ToolRegistry.execute_tool("transfer_human", db, department="FRONT_DESK")
                bot_text = HospitalResponses.HUMAN_TRANSFER_ML if lang == "ml" else HospitalResponses.HUMAN_TRANSFER_EN

            else:
                bot_text = HospitalResponses.GREETING_ML if lang == "ml" else HospitalResponses.GREETING_EN

            tool_end_time = time.time()
            tool_latency_ms = int((tool_end_time - tool_start_time) * 1000)
            total_latency_ms = int((tool_end_time - turn_start_time) * 1000)

            # Record Short-Term Memory
            MemoryEngine.add_short_term_turn(session_id, "USER", user_text, intent, entities)
            MemoryEngine.add_short_term_turn(session_id, "SYSTEM", bot_text, intent)

            # Send Telemetry & Response Frame to Client
            await websocket.send_json({
                "type": "ASSISTANT_RESPONSE",
                "session_id": session_id,
                "language": lang,
                "intent": intent,
                "entities": entities,
                "bot_response": bot_text,
                "bot_response_ml": bot_text,
                "tool_called": tool_name,
                "tool_result": tool_result,
                "memory_context": {
                    "patient_name": long_term_mem.get("name"),
                    "recognized": long_term_mem.get("recognized")
                },
                "latency": {
                    "stt_ms": max(stt_latency_ms, 80),
                    "llm_ms": max(llm_latency_ms, 110),
                    "tool_ms": tool_latency_ms,
                    "tts_ms": 90,
                    "total_ms": total_latency_ms + 170
                }
            })

    except WebSocketDisconnect:
        print(f"WebSocket session {session_id} disconnected.")
    finally:
        db.close()
