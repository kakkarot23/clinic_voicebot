class IntentClassifier:
    INTENTS = {
        "BOOK_APPOINTMENT": ["അപ്പോയിന്റ്മെന്റ്", "appointment", "ബുക്ക്", "കാണണം", "കാണാൻ", "slot", "സമയവും"],
        "CANCEL_APPOINTMENT": ["ക്യാൻസൽ", "cancel", "വേണ്ട", "അപ്പോയിന്റ്മെന്റ് ഒഴിവാക്കണം"],
        "RESCHEDULE_APPOINTMENT": ["reschedule", "മാറ്റണം", "മറ്റൊരു ദിവസത്തേക്ക്"],
        "DOCTOR_AVAILABILITY": ["ഡോക്ടർ ഉണ്ടോ", "available", "ഏത് സമയത്ത്", "ആരൊക്കെയാണ്", "timings", "ഒ.പി"],
        "DEPARTMENT_INFO": ["വിഭാഗം", "department", "ഡിപ്പാർട്ട്മെന്റ്"],
        "EMERGENCY_ESCALATION": ["നെഞ്ചുവേദന", "ശ്വാസം", "അപകടം", "ബോധമില്ല", "ഹാർട്ട് അറ്റാക്ക്", "കുഴഞ്ഞു വീണു", "ആംബുലൻസ്", "emergency"],
        "LAB_TEST_INFO": ["ബ്ലഡ് ടെസ്റ്റ്", "ലാബ്", "fasting", "ഉപവാസം", "ടെസ്റ്റ് വില", "test"],
        "LAB_REPORT_STATUS": ["റിപ്പോർട്ട്", "report", "ലാബ് ഫലം", "റിപ്പോർട്ട് റെഡിയായോ"],
        "RADIOLOGY_INFO": ["mri", "ct", "x-ray", "xray", "സ്കാൻ", "scan", "അൾട്രാസൗണ്ട്"],
        "PHARMACY_INFO": ["മരുന്ന്", "ഫാർമസി", "pharmacy", "medicine"],
        "BILLING_ENQUIRY": ["ബിൽ", "bill", "ഫീസ്", "ചാർജ്", "പണം", "തുക", "payment"],
        "ADMISSION_ENQUIRY": ["അഡ്മിഷൻ", "admission", "റൂം", "room", "ward", "വാർഡ്", "വിസിറ്റിംഗ്"],
        "DISCHARGE_ENQUIRY": ["ഡിസ്ചാർജ്", "discharge"],
        "LOCATION_NAVIGATION": ["എവിടെയാണ്", "എങ്ങനെ പോകാം", "ഏത് ഫ്ലോർ", "floor", "വഴി", "location"],
        "PARKING_INFO": ["പാർക്കിംഗ്", "parking"],
        "HUMAN_AGENT_TRANSFER": ["സ്റ്റാഫ്", "staff", "സംസാരിക്കണം", "മനുഷ്യൻ", "receptionist", "ഓപ്പറേറ്റർ", "human"],
        "COMPLAINT_FEEDBACK": ["പരാതി", "complaint", "ഫീഡ്ബാക്ക്", "feedback"],
        "GREETING": ["ഹലോ", "നമസ്കാരം", "hello", "hi"]
    }

    @classmethod
    def classify(cls, text: str) -> str:
        if not text:
            return "UNKNOWN_QUERY"
        text_lower = text.lower()

        # Priority 1: Check Emergency
        for kw in cls.INTENTS["EMERGENCY_ESCALATION"]:
            if kw in text_lower:
                return "EMERGENCY_ESCALATION"

        # Priority 2: Check Human Transfer
        for kw in cls.INTENTS["HUMAN_AGENT_TRANSFER"]:
            if kw in text_lower:
                return "HUMAN_AGENT_TRANSFER"

        # Check other intents
        scores = {}
        for intent, keywords in cls.INTENTS.items():
            if intent in ["EMERGENCY_ESCALATION", "HUMAN_AGENT_TRANSFER"]:
                continue
            score = 0
            for kw in keywords:
                if kw in text_lower:
                    score += 1
            if score > 0:
                scores[intent] = score

        if scores:
            sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return sorted_intents[0][0]

        return "UNKNOWN_QUERY"
