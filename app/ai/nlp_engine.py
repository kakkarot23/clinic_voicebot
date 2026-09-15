import re

# Phonetic Manglish to Malayalam mapping dictionary
MANGLISH_MAP = {
    "nale": "നാളെ",
    "naale": "നാളെ",
    "innu": "ഇന്ന്",
    "mattennal": "മറ്റന്നാൾ",
    "doctor": "ഡോക്ടർ",
    "dr": "ഡോക്ടർ",
    "appointment": "അപ്പോയിന്റ്മെന്റ്",
    "apointmet": "അപ്പോയിന്റ്മെന്റ്",
    "venam": "വേണം",
    "kananam": "കാണണം",
    "enikku": "എനിക്ക്",
    "enikk": "എനിക്ക്",
    "pani": "പനി",
    "nenchuvedana": "നെഞ്ചുവേദന",
    "shwasam": "ശ്വാസം",
    "cardiology": "കാർഡിയോളജി",
    "ortho": "ഓർത്തോപീഡിക്സ്",
    "orthopedics": "ഓർത്തോപീഡിക്സ്",
    "general": "ജനറൽ",
    "medicine": "മെഡിസിൻ",
    "gynecology": "ഗൈനക്കോളജി",
    "pediatrics": "പീഡിയാട്രിക്സ്",
    "report": "റിപ്പോർട്ട്",
    "lab": "ലാബ്",
    "bill": "ബിൽ",
    "billing": "ബില്ലിംഗ്",
    "pharmacy": "ഫാർമസി",
    "emergency": "എമർജൻസി",
    "staff": "സ്റ്റാഫ്",
    "connect": "കണക്ട്",
    "samsarikkanam": "സംസാരിക്കണം",
    "meera": "മീര",
    "rajesh": "രാജേഷ്",
    "anil": "അനിൽ",
    "suresh": "സുരേഷ്",
    "priya": "പ്രിയ",
    "harish": "ഹരീഷ്"
}

DOCTOR_KEYWORDS_MAP = {
    "രാജേഷ്": "Dr. Rajesh Kumar",
    "rajesh": "Dr. Rajesh Kumar",
    "മീര": "Dr. Meera Nair",
    "meera": "Dr. Meera Nair",
    "അനിൽ": "Dr. Anil Viki",
    "anil": "Dr. Anil Viki",
    "സുരേഷ്": "Dr. Suresh Menon",
    "suresh": "Dr. Suresh Menon",
    "പ്രിയ": "Dr. Priya Varma",
    "priya": "Dr. Priya Varma",
    "ഹരീഷ്": "Dr. Harish Joseph",
    "harish": "Dr. Harish Joseph"
}

DEPARTMENT_KEYWORDS_MAP = {
    "കാർഡിയോളജി": "CARD",
    "cardiology": "CARD",
    "ഹൃദയ": "CARD",
    "ജനറൽ മെഡിസിൻ": "GEN",
    "general medicine": "GEN",
    "പനി": "GEN",
    "ഓർത്തോപീഡിക്സ്": "ORTHO",
    "ortho": "ORTHO",
    "അസ്ഥി": "ORTHO",
    "ഗൈനക്കോളജി": "GYN",
    "gynecology": "GYN",
    "പീഡിയാട്രിക്സ്": "PED",
    "കുട്ടികളുടെ": "PED",
    "pediatrics": "PED",
    "റേഡിയോളജി": "RAD",
    "radiology": "RAD",
    "സ്കാൻ": "RAD",
    "ലാബ്": "LAB",
    "lab": "LAB",
    "ഫാർമസി": "PHARM",
    "pharmacy": "PHARM",
    "എമർജൻസി": "EMG",
    "emergency": "EMG"
}

class MalayalamNLPEngine:
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detects whether input is primarily English or Malayalam/Manglish
        """
        if not text:
            return "ml"
        # Check for Malayalam Unicode range (\u0D00-\u0D7F)
        if re.search(r'[\u0D00-\u0D7F]', text):
            return "ml"
        
        # Check for pure English phrases vs Manglish
        english_words = {"i", "want", "to", "book", "an", "appointment", "with", "tomorrow", "today", "doctor", "department", "is", "available", "my", "report", "ready", "bill", "amount", "where", "is", "the"}
        words = set(re.sub(r'[^\w\s]', '', text.lower()).split())
        match_count = len(words.intersection(english_words))
        
        if match_count >= 2:
            return "en"
        return "ml"

    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        text = text.strip().lower()
        words = text.split()
        normalized_words = []
        for w in words:
            clean_w = re.sub(r'[^\w\s]', '', w)
            if clean_w in MANGLISH_MAP:
                normalized_words.append(MANGLISH_MAP[clean_w])
            else:
                normalized_words.append(w)
        return " ".join(normalized_words)

    @staticmethod
    def extract_entities(text: str) -> dict:
        text_lower = text.lower()
        entities = {
            "doctor_name": None,
            "department_code": None,
            "date_relative": None,
            "time_slot": None,
            "phone_number": None,
            "patient_code": None
        }

        # 1. Doctor extraction
        for kw, doc_full_name in DOCTOR_KEYWORDS_MAP.items():
            if kw.lower() in text_lower:
                entities["doctor_name"] = doc_full_name
                break

        # 2. Department extraction
        for kw, dept_code in DEPARTMENT_KEYWORDS_MAP.items():
            if kw.lower() in text_lower:
                entities["department_code"] = dept_code
                break

        # 3. Relative Date extraction
        if any(w in text_lower for w in ["നാളെ", "nale", "tomorrow"]):
            entities["date_relative"] = "TOMORROW"
        elif any(w in text_lower for w in ["ഇന്ന്", "innu", "today"]):
            entities["date_relative"] = "TODAY"
        elif any(w in text_lower for w in ["മറ്റന്നാൾ", "mattennal", "day after tomorrow"]):
            entities["date_relative"] = "DAY_AFTER_TOMORROW"

        # 4. Time slot extraction
        time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm|എഎം|പിഎം)?)', text_lower)
        if time_match:
            entities["time_slot"] = time_match.group(1)
        elif any(w in text_lower for w in ["രാവിലെ", "morning"]):
            entities["time_slot"] = "10:00 AM"
        elif any(w in text_lower for w in ["ഉച്ചയ്ക്ക്", "afternoon"]):
            entities["time_slot"] = "12:00 PM"
        elif any(w in text_lower for w in ["വൈകുന്നേരം", "evening"]):
            entities["time_slot"] = "04:30 PM"

        # 5. Phone number extraction
        phone_match = re.search(r'\b\d{10}\b', text)
        if phone_match:
            entities["phone_number"] = phone_match.group(0)

        # 6. Patient code extraction
        kmc_match = re.search(r'kmc-\d{4}', text_lower)
        if kmc_match:
            entities["patient_code"] = kmc_match.group(0).upper()

        return entities
