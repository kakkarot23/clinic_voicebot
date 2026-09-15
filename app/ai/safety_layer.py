class SafetyLayer:
    EMERGENCY_TRIGGERS = [
        "നെഞ്ചുവേദന", "ശ്വാസം തടസ്സം", "ശ്വാസമെടുക്കാൻ പറ്റുന്നില്ല", "ശ്വാസം എടുക്കാൻ", "ശ്വാസം",
        "അപകടം", "ബോധമില്ല", "ഹാർട്ട് അറ്റാക്ക്", "കുഴഞ്ഞു വീണു", "രക്തസ്രാവം",
        "chest pain", "shortness of breath", "heart attack", "accident", "unconscious", "heavy bleeding"
    ]

    @classmethod
    def check_safety(cls, text: str) -> dict:
        if not text:
            return {"is_emergency": False, "reason": None}
            
        text_lower = text.lower()
        for trigger in cls.EMERGENCY_TRIGGERS:
            if trigger in text_lower:
                return {
                    "is_emergency": True,
                    "trigger": trigger,
                    "response_ml": "ഇത് അടിയന്തര സാഹചര്യമാകാം! ദയവായി പരിഭ്രാന്തരാകരുത്. നിങ്ങളെ ഉടൻ തന്നെ എമർജൻസി ട്രോമ കെയർ ടീമുമായി ബന്ധിപ്പിക്കുന്നു. ദയവായി കോൾ ഡിസ്കണക്ട് ചെയ്യരുത്!",
                    "escalation_desk": "EMERGENCY_DESK_108"
                }
        return {"is_emergency": False, "reason": None}

    @classmethod
    def is_clinical_advice_requested(cls, text: str) -> bool:
        clinical_kw = ["മരുന്ന് മാറ്റി കഴിക്കാമോ", "ഏത് മരുന്ന് കഴിക്കണം", "ഡോസ് എത്രയാണ്", "വ്യാധി എന്താണ്", "prescribe medicine", "change dosage"]
        text_lower = text.lower()
        return any(kw in text_lower for kw in clinical_kw)
