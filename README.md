# 🏥 Kerala Medical Center - Multilingual Hospital Voice Assistant & Telephony System

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![Language](https://img.shields.io/badge/Language-Malayalam%20%7C%20English%20%7C%20Manglish-orange.svg)]()

An end-to-end production-grade **Multilingual (Malayalam + English + Manglish) Voice Receptionist and Front-Office System** for hospitals and healthcare centers. Built with **Python, FastAPI, SQLite/SQLAlchemy**, real-time Speech-to-Text, Edge-TTS speech synthesis, and an interactive front-office suite.

---

## 📸 Interface & Feature Screenshots

### 1. 🎙️ Main Voice Assistant & Phone Simulator
The interactive telephony voice assistant understands spoken or typed Malayalam script, Manglish (phonetic Latin Malayalam), and English. Features caller identity verification, real-time intent telemetry, and natural voice playback.

![Voice Assistant](./screenshots/voice_assistant.png)

---

### 2. 📱 WhatsApp Assistant Integration
Simulates WhatsApp voice and text assistance for patients looking to check lab reports, request appointment slots, or query billing info in Malayalam or English.

![WhatsApp Assistant](./screenshots/whatsapp_bot.png)

---

### 3. 🗺️ Entrance Voice Navigation Kiosk
Entrance kiosk providing voice directions and floor mapping for patients looking for OPD rooms, labs, pharmacy, or emergency trauma care.

![Entrance Voice Kiosk](./screenshots/entrance_kiosk.png)

---

### 4. 📊 Staff & Receptionist Dashboard
Real-time dashboard monitoring incoming calls, appointment desks, on-duty doctors across departments, and human agent call transfers.

![Staff Dashboard](./screenshots/staff_dashboard.png)

---

### 5. ⚙️ Admin Configuration Portal
No-code administration portal allowing hospital administrators to register new doctors, configure consultation fees, update room numbers, and set up department schedules.

![Admin Portal](./screenshots/admin_portal.png)

---

## 🚀 Key System Features

- **🌐 Multilingual Support (Malayalam + English + Manglish)**:
  - Normalizes Manglish (`nale doctor meera appointment venam`) into unicode Malayalam script.
  - Automatically detects language context (`Malayalam` vs `English`) and responds in the caller's preferred language.
- **🚑 Life-Safety & Emergency Escalation Protocol**:
  - Automatically detects critical symptoms (`chest pain`, `shortness of breath`, `നെഞ്ചുവേദന`, `ശ്വാസം തടസ്സം`, `accident`).
  - Immediately overrides standard options to transfer the caller to the **Emergency Trauma Desk (108)** without offering clinical diagnosis.
- **📅 Doctor Appointment Engine**:
  - Checks doctor schedules across specialties (Cardiology, Neurology, Orthopedics, General Medicine, Pediatrics, Gynecology).
  - Handles booking, rescheduling, and cancellation workflows with SMS confirmation simulator.
- **🧪 Laboratory & Billing Verification**:
  - Returns lab report readiness status, fasting requirements (e.g., 10-12 hour fasting for Lipid Profile), and pending invoice breakdown.
- **🗺️ Hospital Entrance Kiosk**:
  - Interactive map directions and floor plans for hospital navigation.

---

## 🏗️ Project Architecture

```
clinic_voicebot/
│
├── app/
│   ├── main.py                     # FastAPI application entry point
│   ├── config.py                   # App configuration & settings
│   │
│   ├── database/                   # Database ORM & Seeding
│   │   ├── database.py             # SQLAlchemy session & engine
│   │   ├── models.py               # Patient, Doctor, Appointment, Lab, Billing models
│   │   └── seed_data.py            # Pre-seeded Kerala hospital data
│   │
│   ├── ai/                         # NLP & Intent Processing
│   │   ├── nlp_engine.py           # Manglish->Malayalam, Entity Extractor, Language Detector
│   │   ├── intent_classifier.py    # 20+ Hospital Intent Classifiers
│   │   ├── conversation_manager.py # Multi-turn dialog context tracker
│   │   ├── safety_layer.py         # Emergency triage & clinical advice disclaimer
│   │   └── responses_ml.py         # Bilingual Malayalam & English response templates
│   │
│   ├── voice/                      # Voice Processing
│   │   ├── stt_handler.py          # Speech-to-Text input handler
│   │   └── tts_handler.py          # Edge-TTS / gTTS Malayalam & English audio generator
│   │
│   ├── services/                   # Business Services
│   │   ├── appointment_service.py
│   │   ├── patient_service.py
│   │   ├── emergency_service.py
│   │   ├── billing_service.py
│   │   ├── lab_service.py
│   │   └── hospital_service.py
│   │
│   ├── api/                        # REST API Endpoints
│   │   ├── voice_api.py            # Core voice process & TTS stream API
│   │   ├── appointments_api.py
│   │   ├── hospital_api.py
│   │   ├── whatsapp_api.py
│   │   ├── kiosk_api.py
│   │   └── admin_api.py
│   │
│   ├── static/                     # CSS & Client-side JavaScript
│   └── templates/                  # HTML5 Templates (Simulator, Kiosk, Dashboard, Admin)
│
├── screenshots/                    # Screenshots for GitHub documentation
├── tests/                          # Automated Pytest suite
├── requirements.txt                # Python dependencies
└── README.md
```

---

## 💻 Installation & Setup Instructions

### Prerequisites
- Python 3.10+ installed on Windows, macOS, or Linux

### 1. Clone the Repository
```bash
git clone https://github.com/kakkarot23/clinic_voicebot.git
cd clinic_voicebot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### 4. Access Web Interfaces
Open your browser and navigate to:
- **Voice Assistant**: [http://localhost:8080/](http://localhost:8080/)
- **WhatsApp Assistant**: [http://localhost:8080/whatsapp](http://localhost:8080/whatsapp)
- **Entrance Kiosk**: [http://localhost:8080/kiosk](http://localhost:8080/kiosk)
- **Staff Dashboard**: [http://localhost:8080/dashboard](http://localhost:8080/dashboard)
- **Admin Portal**: [http://localhost:8080/admin](http://localhost:8080/admin)

---

## 🧪 Running Automated Tests

Run the unit test suite covering intent classification, Manglish normalization, and emergency safety triggers:

```bash
python -m pytest tests/test_voicebot.py
```

---

## 📜 License
This project is open-source and available under the [MIT License](LICENSE).
