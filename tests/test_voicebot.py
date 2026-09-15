import pytest
from app.ai.intent_classifier import IntentClassifier
from app.ai.nlp_engine import MalayalamNLPEngine
from app.ai.safety_layer import SafetyLayer

def test_intent_classification():
    # Malayalam appointment test
    intent1 = IntentClassifier.classify("നാളെ ഡോക്ടർ മീരയെ കാണാൻ അപ്പോയിന്റ്മെന്റ് വേണം")
    assert intent1 == "BOOK_APPOINTMENT"

    # Manglish appointment test
    intent2 = IntentClassifier.classify("nale doctor meera appointment venam")
    assert intent2 == "BOOK_APPOINTMENT"

    # Emergency escalation test
    intent3 = IntentClassifier.classify("എനിക്ക് ശക്തമായ നെഞ്ചുവേദന അനുഭവപ്പെടുന്നു")
    assert intent3 == "EMERGENCY_ESCALATION"

    # Lab report test
    intent4 = IntentClassifier.classify("എന്റെ ലബോറട്ടറി ബ്ലഡ് ടെസ്റ്റ് റിപ്പോർട്ട് റെഡിയായോ")
    assert intent4 == "LAB_REPORT_STATUS"

def test_manglish_normalization():
    norm = MalayalamNLPEngine.normalize_text("nale doctor meera venam")
    assert "നാളെ" in norm
    assert "ഡോക്ടർ" in norm
    assert "മീര" in norm

def test_safety_emergency():
    res1 = SafetyLayer.check_safety("എനിക്ക് ശ്വാസം എടുക്കാൻ പറ്റുന്നില്ല")
    assert res1["is_emergency"] == True

    res2 = SafetyLayer.check_safety("ഡോക്ടർ മീരയുടെ സമയം എപ്പോഴാണ്")
    assert res2["is_emergency"] == False
