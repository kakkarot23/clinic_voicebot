from typing import Dict, Any, Callable
from sqlalchemy.orm import Session
from app.services.appointment_service import AppointmentService
from app.services.patient_service import PatientService
from app.services.lab_service import LabService
from app.services.billing_service import BillingService
from app.services.hospital_service import HospitalService
from app.services.emergency_service import EmergencyService

class ToolRegistry:
    _registry: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(func: Callable):
            cls._registry[name] = func
            return func
        return decorator

    @classmethod
    def execute_tool(cls, name: str, db: Session, **kwargs) -> dict:
        if name not in cls._registry:
            return {"success": False, "error": f"Tool '{name}' not found."}
        try:
            result = cls._registry[name](db, **kwargs)
            return {"success": True, "tool_name": name, "result": result}
        except Exception as e:
            return {"success": False, "tool_name": name, "error": str(e)}

@ToolRegistry.register("book_appointment")
def tool_book_appointment(db: Session, patient_phone: str, doctor_name: str, time_slot: str = "10:30 AM", date_str: str = "2026-09-16") -> dict:
    patient = PatientService.get_by_phone(db, patient_phone)
    if not patient:
        patient = PatientService.create_patient(db, name="Registered Caller", phone=patient_phone)
    
    docs = AppointmentService.get_available_doctors(db, doc_name=doctor_name)
    doc_id = docs[0].id if docs else 2
    doc_name = docs[0].name_en if docs else doctor_name
    
    app_rec = AppointmentService.book_appointment(db, patient_id=patient.id, doctor_id=doc_id, date_str=date_str, time_slot=time_slot)
    return {
        "appointment_number": app_rec.appointment_number,
        "doctor": doc_name,
        "date": date_str,
        "time": time_slot,
        "patient": patient.name
    }

@ToolRegistry.register("check_doctor_schedule")
def tool_check_doctor_schedule(db: Session, doctor_name: str = None, doc_name: str = None, dept_code: str = None) -> dict:
    target_name = doctor_name or doc_name
    docs = AppointmentService.get_available_doctors(db, dept_code=dept_code, doc_name=target_name)
    doc_list = [{"id": d.id, "name_ml": d.name_ml, "name_en": d.name_en, "room": d.room_number, "fee": d.consultation_fee} for d in docs]
    return {"count": len(doc_list), "doctors": doc_list}

@ToolRegistry.register("get_lab_status")
def tool_get_lab_status(db: Session, patient_phone: str) -> dict:
    order = LabService.get_lab_status(db, patient_phone)
    if not order:
        return {"found": False, "message": "No lab orders found"}
    return {
        "found": True,
        "order_number": order.order_number,
        "test_ml": order.test_name_ml,
        "test_en": order.test_name_en,
        "status": order.status,
        "report_ready": order.report_ready,
        "fasting_required": order.fasting_required
    }

@ToolRegistry.register("get_billing_status")
def tool_get_billing_status(db: Session, patient_phone: str) -> dict:
    bill = BillingService.get_patient_bill(db, patient_phone)
    if not bill:
        return {"found": False, "total": 0.0, "status": "PAID"}
    return {
        "found": True,
        "invoice_number": bill.invoice_number,
        "total_amount": bill.total_amount,
        "paid_amount": bill.paid_amount,
        "status": bill.status
    }

@ToolRegistry.register("hospital_search")
def tool_hospital_search(db: Session, query_text: str) -> dict:
    kb = HospitalService.search_knowledge_base(db, query_text)
    if kb:
        return {"found": True, "answer_ml": kb.answer_ml, "answer_en": kb.answer_en}
    loc = HospitalService.get_location_directions(db, query_text)
    if loc:
        return {"found": True, "answer_ml": f"{loc.name_ml} {loc.floor}-ലാണ്. {loc.directions_ml}", "answer_en": f"{loc.name_en} is on {loc.floor}."}
    return {"found": False, "answer_ml": "വിവരങ്ങൾ ലഭ്യമല്ല", "answer_en": "Information not found"}

@ToolRegistry.register("escalate_emergency")
def tool_escalate_emergency(db: Session, patient_phone: str, trigger_word: str = "chest pain") -> dict:
    res = EmergencyService.handle_emergency_trigger(db, patient_phone, trigger_word)
    return res

@ToolRegistry.register("transfer_human")
def tool_transfer_human(db: Session, department: str = "FRONT_DESK") -> dict:
    return {"transferred": True, "department": department, "status": "CONNECTING"}
