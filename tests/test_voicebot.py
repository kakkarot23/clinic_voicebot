import pytest
from app.ai.intent_classifier import IntentClassifier
from app.ai.nlp_engine import MalayalamNLPEngine
from app.ai.safety_layer import SafetyLayer
from app.ai.tool_registry import ToolRegistry
from app.ai.memory_engine import MemoryEngine
from app.ai.personality import PersonalityConfig
from app.database.database import SessionLocal

def test_intent_classification():
    # Malayalam appointment test
    intent1 = IntentClassifier.classify("നാളെ ഡോക്ടർ മീരയെ കാണാൻ അപ്പോയിന്റ്മെന്റ് വേണം")
    assert intent1 == "BOOK_APPOINTMENT"

    # English appointment test
    intent2 = IntentClassifier.classify("I want to book an appointment with Dr. Meera tomorrow")
    assert intent2 == "BOOK_APPOINTMENT"

    # Emergency escalation test
    intent3 = IntentClassifier.classify("എനിക്ക് ശക്തമായ നെഞ്ചുവേദന അനുഭവപ്പെടുന്നു")
    assert intent3 == "EMERGENCY_ESCALATION"

def test_language_detection():
    lang1 = MalayalamNLPEngine.detect_language("നാളെ ഡോക്ടർ മീരയെ കാണണം")
    assert lang1 == "ml"

    lang2 = MalayalamNLPEngine.detect_language("I want to check my lab report status")
    assert lang2 == "en"

def test_safety_emergency():
    res1 = SafetyLayer.check_safety("എനിക്ക് ശ്വാസം എടുക്കാൻ പറ്റുന്നില്ല")
    assert res1["is_emergency"] == True

    res2 = SafetyLayer.check_safety("ഡോക്ടർ മീരയുടെ സമയം എപ്പോഴാണ്")
    assert res2["is_emergency"] == False

def test_tool_registry():
    db = SessionLocal()
    try:
        res = ToolRegistry.execute_tool("check_doctor_schedule", db, doc_name="Meera")
        assert res["success"] == True
        assert "doctors" in res["result"]

        emergency_res = ToolRegistry.execute_tool("escalate_emergency", db, patient_phone="9876543210", trigger_word="chest pain")
        assert emergency_res["success"] == True
        assert emergency_res["result"]["status"] == "ESCALATED"
    finally:
        db.close()

def test_memory_engine():
    MemoryEngine.add_short_term_turn("sess_101", "USER", "Hello", "GREETING")
    history = MemoryEngine.get_short_term_history("sess_101")
    assert len(history) == 1
    assert history[0]["sender"] == "USER"
