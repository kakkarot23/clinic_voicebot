class NotificationService:
    @staticmethod
    def send_appointment_sms(phone: str, doctor_name: str, date: str, time: str, app_num: str):
        msg = f"കേരള മെഡിക്കൽ സെന്റർ: നിങ്ങളുടെ അപ്പോയിന്റ്മെന്റ് {doctor_name}-നൊപ്പം {date} {time}-ന് സ്ഥിരീകരിച്ചു (No: {app_num}). നന്ദി!"
        print(f"[SMS SIMULATOR] Sent to {phone}: {msg}")
        return True

    @staticmethod
    def send_whatsapp_notification(phone: str, message: str):
        print(f"[WHATSAPP SIMULATOR] Sent to {phone}: {message}")
        return True
