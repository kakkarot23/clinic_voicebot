from sqlalchemy.orm import Session
from app.database.models import (
    Patient, Department, Doctor, DoctorSchedule,
    LabOrder, LabReport, BillingRecord, AdmissionRecord,
    HospitalKnowledgeBase, HospitalLocation, PharmacyItem
)
from datetime import datetime, timedelta

def seed_database(db: Session):
    # Check if already seeded
    if db.query(Department).first():
        print("Database already seeded.")
        return

    print("Seeding Kerala Medical Voicebot Database...")

    # 1. Departments
    depts = [
        Department(name_ml="എമർജൻസി & ട്രോമ കെയർ", name_en="Emergency & Trauma Care", code="EMG", floor="Ground Floor", room_number="G-01", description_ml="24x7 അടിയന്തര ചികിത്സയും ആംബുലൻസ് സേവനവും"),
        Department(name_ml="ജനറൽ മെഡിസിൻ", name_en="General Medicine", code="GEN", floor="Ground Floor", room_number="G-12", description_ml="സാധാരണ രോഗങ്ങൾ, പനി, പ്രമേഹം എന്നിവയ്ക്കുള്ള പരിശോധന"),
        Department(name_ml="കാർഡിയോളജി", name_en="Cardiology", code="CARD", floor="1st Floor", room_number="102", description_ml="ഹൃദ്രോഗ ചികിത്സാ വിഭാഗം & ഇസിജി / എക്കോ"),
        Department(name_ml="ന്യൂറോളജി", name_en="Neurology", code="NEURO", floor="1st Floor", room_number="108", description_ml="നാഡീവ്യൂഹ ബന്ധമായ പ്രശ്നങ്ങൾ"),
        Department(name_ml="ഓർത്തോപീഡിക്സ്", name_en="Orthopedics", code="ORTHO", floor="2nd Floor", room_number="205", description_ml="അസ്ഥി, സന്ധി, ഫ്രാക്ചർ ചികിത്സ"),
        Department(name_ml="പീഡിയാട്രിക്സ്", name_en="Pediatrics", code="PED", floor="2nd Floor", room_number="210", description_ml="കുട്ടികളുടെ ചികിത്സയും പ്രതിരോധ കുത്തിവെയ്പും"),
        Department(name_ml="ഗൈനക്കോളജി", name_en="Gynecology & Obstetrics", code="GYN", floor="3rd Floor", room_number="304", description_ml="സ്ത്രീരോഗ നിദാനവും ഗർഭകാല പരിചരണവും"),
        Department(name_ml="ഡെർമറ്റോളജി", name_en="Dermatology", code="DERM", floor="1st Floor", room_number="115", description_ml="ചർമ്മ രോഗ ചികിത്സ"),
        Department(name_ml="ഇ.എൻ.ടി (ENT)", name_en="ENT", code="ENT", floor="Ground Floor", room_number="G-20", description_ml="ചെവി, മൂക്ക്, തൊണ്ട സംബന്ധമായ ചികിത്സ"),
        Department(name_ml="ഒഫ്താൽമോളജി", name_en="Ophthalmology", code="EYE", floor="Ground Floor", room_number="G-22", description_ml="കണ്ണ് പരിശോധനയും തിമിര ശസ്ത്രക്രിയയും"),
        Department(name_ml="റേഡിയോളജി & സ്കാനിംഗ്", name_en="Radiology", code="RAD", floor="Basement 1", room_number="B1-05", description_ml="X-Ray, CT, MRI, അൾട്രാസൗണ്ട് സ്കാനിംഗ്"),
        Department(name_ml="ലബോറട്ടറി", name_en="Laboratory", code="LAB", floor="Basement 1", room_number="B1-10", description_ml="രക്ത പരിശോധന, മൂത്ര പരിശോധന, പാത്തോളജി"),
        Department(name_ml="ഫാർമസി", name_en="Pharmacy", code="PHARM", floor="Ground Floor", room_number="G-05", description_ml="24 മണിക്കുറുമ പ്രവർത്തിക്കുന്ന മരുന്ന് വിതരണ കേന്ദ്രം"),
        Department(name_ml="ബ്ലഡ് ബാങ്ക്", name_en="Blood Bank", code="BB", floor="Ground Floor", room_number="G-08", description_ml="24x7 രക്ത ബാങ്കും പ്ലാസ്മ കേന്ദ്രവും"),
    ]
    db.add_all(depts)
    db.commit()

    # Query created depts
    gen_dept = db.query(Department).filter_by(code="GEN").first()
    card_dept = db.query(Department).filter_by(code="CARD").first()
    ortho_dept = db.query(Department).filter_by(code="ORTHO").first()
    gyn_dept = db.query(Department).filter_by(code="GYN").first()
    ped_dept = db.query(Department).filter_by(code="PED").first()

    # 2. Doctors
    doctors = [
        Doctor(name_ml="ഡോക്ടർ രാജേഷ് കുമാർ", name_en="Dr. Rajesh Kumar", department_id=gen_dept.id, specialization_ml="Senior Consultant General Physician", qualifications="MD, MBBS", consultation_fee=400.0, follow_up_fee=250.0, room_number="G-12"),
        Doctor(name_ml="ഡോക്ടർ അനിൽ വിക്കി", name_en="Dr. Anil Viki", department_id=card_dept.id, specialization_ml="Interventional Cardiologist", qualifications="DM (Cardio), MD, MBBS", consultation_fee=700.0, follow_up_fee=400.0, room_number="102"),
        Doctor(name_ml="ഡോക്ടർ മീരാ നായർ", name_en="Dr. Meera Nair", department_id=card_dept.id, specialization_ml="Consultant Cardiologist", qualifications="MD, DM (Cardio)", consultation_fee=650.0, follow_up_fee=350.0, room_number="104"),
        Doctor(name_ml="ഡോക്ടർ സുരേഷ് മേനോൻ", name_en="Dr. Suresh Menon", department_id=ortho_dept.id, specialization_ml="Orthopedic Surgeon", qualifications="MS (Ortho), D.Ortho", consultation_fee=600.0, follow_up_fee=350.0, room_number="205"),
        Doctor(name_ml="ഡോക്ടർ പ്രിയ വർമ്മ", name_en="Dr. Priya Varma", department_id=gyn_dept.id, specialization_ml="Gynecologist & Obstetrician", qualifications="MD, DGO", consultation_fee=500.0, follow_up_fee=300.0, room_number="304"),
        Doctor(name_ml="ഡോക്ടർ ഹരീഷ് ജോസഫ്", name_en="Dr. Harish Joseph", department_id=ped_dept.id, specialization_ml="Consultant Pediatrician", qualifications="MD (Pediatrics), DCH", consultation_fee=500.0, follow_up_fee=300.0, room_number="210"),
    ]
    db.add_all(doctors)
    db.commit()

    # 3. Doctor Schedules
    doc_rajesh = db.query(Doctor).filter_by(name_en="Dr. Rajesh Kumar").first()
    doc_anil = db.query(Doctor).filter_by(name_en="Dr. Anil Viki").first()
    doc_meera = db.query(Doctor).filter_by(name_en="Dr. Meera Nair").first()
    doc_suresh = db.query(Doctor).filter_by(name_en="Dr. Suresh Menon").first()

    schedules = [
        DoctorSchedule(doctor_id=doc_rajesh.id, day_of_week="Monday", start_time="09:00 AM", end_time="01:00 PM"),
        DoctorSchedule(doctor_id=doc_rajesh.id, day_of_week="Tuesday", start_time="09:00 AM", end_time="01:00 PM"),
        DoctorSchedule(doctor_id=doc_rajesh.id, day_of_week="Wednesday", start_time="09:00 AM", end_time="01:00 PM"),
        DoctorSchedule(doctor_id=doc_anil.id, day_of_week="Monday", start_time="10:00 AM", end_time="02:00 PM"),
        DoctorSchedule(doctor_id=doc_anil.id, day_of_week="Wednesday", start_time="10:00 AM", end_time="02:00 PM"),
        DoctorSchedule(doctor_id=doc_anil.id, day_of_week="Friday", start_time="10:00 AM", end_time="02:00 PM"),
        DoctorSchedule(doctor_id=doc_meera.id, day_of_week="Tuesday", start_time="09:00 AM", end_time="01:00 PM"),
        DoctorSchedule(doctor_id=doc_meera.id, day_of_week="Thursday", start_time="09:00 AM", end_time="01:00 PM"),
        DoctorSchedule(doctor_id=doc_meera.id, day_of_week="Saturday", start_time="09:00 AM", end_time="01:00 PM"),
        DoctorSchedule(doctor_id=doc_suresh.id, day_of_week="Monday", start_time="02:00 PM", end_time="06:00 PM"),
        DoctorSchedule(doctor_id=doc_suresh.id, day_of_week="Thursday", start_time="02:00 PM", end_time="06:00 PM"),
    ]
    db.add_all(schedules)
    db.commit()

    # 4. Patients
    patients = [
        Patient(patient_code="KMC-1001", name="അജിത്ത് കുമാർ", dob="1985-05-12", gender="Male", phone="9876543210", address="എം. ജി. റോഡ്, എറണാകുളം, കൊച്ചി", email="ajith@example.com", emergency_contact="9876543211", insurance_info="Star Health Insurance (Pol #SH-88492)"),
        Patient(patient_code="KMC-1002", name="ലക്ഷ്മി പി", dob="1992-09-24", gender="Female", phone="9447012345", address="കവടിയാർ, തിരുവനന്തപുരം", email="lakshmi@example.com", emergency_contact="9447012346", insurance_info="Religare Health"),
        Patient(patient_code="KMC-1003", name="മുഹമ്മദ് ഷാഫി", dob="1978-11-03", gender="Male", phone="9846055443", address="മിഠായി തെരുവ്, കോഴിക്കോട്", email="shafi@example.com", emergency_contact="9846055444", insurance_info="Ayushman Bharat Pradhan Mantri Jan Arogya Yojana"),
    ]
    db.add_all(patients)
    db.commit()

    patient1 = db.query(Patient).filter_by(patient_code="KMC-1001").first()

    # 5. Lab Orders & Reports
    lab_order = LabOrder(
        order_number="LAB-202609-001",
        patient_id=patient1.id,
        test_name_ml="കംപ്ലീറ്റ് ബ്ലഡ് കൗണ്ട് (CBC) & ലിപിഡ് പ്രൊഫൈൽ",
        test_name_en="Complete Blood Count (CBC) & Lipid Profile",
        price=850.0,
        preparation_instructions_ml="ലിപിഡ് പ്രൊഫൈൽ പരിശോധനയ്ക്കായി 10-12 മണിക്കൂർ ഉപവാസം (Fasting) ആവശ്യമാണ്. രാവിലെ വെള്ളം മാത്രം കുടിക്കാം.",
        fasting_required=True,
        status="READY",
        report_ready=True
    )
    db.add(lab_order)
    db.commit()

    lab_report = LabReport(
        order_id=lab_order.id,
        patient_id=patient1.id,
        report_summary_ml="ഹീമോഗ്ലോബിൻ: 14.2 g/dL (സാധാരണ നില). ടോട്ടൽ കൊളസ്ട്രോൾ: 185 mg/dL (സാധാരണ നില). എല്ലാ ഫലങ്ങളും സാധാരണ പരിധിയിലാണ്.",
        pdf_url="/static/reports/lab_kmc_1001.pdf",
        doctor_verified=True
    )
    db.add(lab_report)

    # 6. Billing Records
    bill = BillingRecord(
        invoice_number="INV-2026-9901",
        patient_id=patient1.id,
        consultation_fee=650.0,
        lab_charges=850.0,
        pharmacy_charges=420.0,
        room_charges=0.0,
        total_amount=1920.0,
        paid_amount=1920.0,
        status="PAID",
        payment_link="https://keralamedical.org/pay/INV-2026-9901",
        due_date="2026-09-15"
    )
    db.add(bill)

    # 7. Knowledge Base
    kb_items = [
        HospitalKnowledgeBase(category="PARKING", key_phrase_ml="പാർക്കിംഗ്", answer_ml="ആശുപത്രിയുടെ ബി-2 ലെവലിൽ (Basement 2) വിശാലമായ കാർ / ടൂവീലർ പാർക്കിംഗ് ലഭ്യമാണ്. ആദ്യ 2 മണിക്കൂർ പാർക്കിംഗ് സൗജന്യമാണ്. ആംബുലൻസ് പ്രവേശനം മെയിൻ ഗേറ്റിന് സമീപമാണ്.", answer_en="Ample parking for cars and two-wheelers is available in Basement 2. First 2 hours free. Ambulance entrance is near Main Gate."),
        HospitalKnowledgeBase(category="TIMINGS", key_phrase_ml="സന്ദർശന സമയം", answer_ml="പേഷ്യന്റ് വിസിറ്റിംഗ് സമയം: രാവിലെ 11:00 മുതൽ ഉച്ചയ്ക്ക് 12:00 വരെയും, വൈകുന്നേരം 4:30 മുതൽ 6:30 വരെയുമാണ്. ഒരു രോഗിക്ക് ഒരു അറ്റൻഡർ പാസ് മാത്രമേ അനുവദിക്കൂ.", answer_en="Patient visiting hours: 11:00 AM - 12:00 PM and 4:30 PM - 6:30 PM. Only one attender pass per patient."),
        HospitalKnowledgeBase(category="LAB", key_phrase_ml="ബ്ലഡ് ടെസ്റ്റ് ഉപവാസം", answer_ml="ഫാസ്റ്റിംഗ് ബ്ലഡ് ഷുഗർ, ലിപിഡ് പ്രൊഫൈൽ എന്നീ പരിശോധനകൾക്ക് 10-12 മണിക്കൂർ വെള്ളം ഒഴികെ മറ്റൊന്നും കഴിക്കാതെ ഉപവസിക്കേണ്ടതാണ്.", answer_en="For Fasting Blood Sugar and Lipid Profile, 10-12 hours of fasting (water allowed) is mandatory."),
        HospitalKnowledgeBase(category="LOCATION", key_phrase_ml="വിലാസം", answer_ml="കേരള മെഡിക്കൽ സെന്റർ, ബൈപാസ് റോഡ്, വൈറ്റില, കൊച്ചി, കേരളം - 682019. ഫോൺ: 0484-2999999", answer_en="Kerala Medical Center, Bypass Road, Vyttila, Kochi, Kerala - 682019. Phone: 0484-2999999")
    ]
    db.add_all(kb_items)

    # 8. Locations
    locations = [
        HospitalLocation(name_ml="ഓർത്തോപീഡിക്സ് ഒ.പി", name_en="Orthopedics OP", category="Department", floor="Second Floor (2nd Floor)", block="Main Block", directions_ml="മെയിൻ ലോബിയിൽ നിന്ന് ലിഫ്റ്റ് ഉപയോഗിച്ച് രണ്ടാം നിലയിലേക്ക് പോകുക. ലിഫ്റ്റിൽ നിന്നിറങ്ങി ഇടത്തോട്ട് തിരിഞ്ഞാൽ റൂം നമ്പർ 205-ൽ കാണാം."),
        HospitalLocation(name_ml="കാർഡിയോളജി ഒ.പി", name_en="Cardiology OP", category="Department", floor="First Floor (1st Floor)", block="Block A", directions_ml="ആദ്യ നിലയിലെ ബ്ലോക്ക് എ-യിൽ റൂം 102, 104 എന്നിവ കാർഡിയോളജി വിഭാഗമാണ്."),
        HospitalLocation(name_ml="മെയിൻ ഫാർമസി", name_en="Main Pharmacy", category="Pharmacy", floor="Ground Floor", room_number="G-05", block="Main Entrance", directions_ml="മെയിൻ ഗേറ്റ് വഴി പ്രവേശിച്ച് റിസപ്ഷന്റെ വലതുവശത്ത് ഫാർമസി കാണാം. 24 മണിക്കൂറും പ്രവർത്തിക്കുന്നു."),
        HospitalLocation(name_ml="ലബോറട്ടറി & ബ്ലഡ് ബാങ്ക്", name_en="Laboratory & Blood Bank", category="Lab", floor="Basement 1", block="Block B", directions_ml="ബേസ്മെന്റ് 1-ലേക്ക് എസ്കലേറ്റർ അല്ലെങ്കിൽ ലിഫ്റ്റ് വഴി പോകുക. സാമ്പിൾ കളക്ഷൻ കൗണ്ടറുകൾ B1-10 ൽ ലഭ്യമാണ്.")
    ]
    db.add_all(locations)

    db.commit()
    print("Database seeding completed successfully!")
