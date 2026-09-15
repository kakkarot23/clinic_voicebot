import uuid
from typing import Dict, Any, Optional

class ConversationSession:
    def __init__(self, session_id: str, caller_phone: str = "9876543210"):
        self.session_id = session_id
        self.caller_phone = caller_phone
        self.patient_id: Optional[int] = None
        self.verified_identity: bool = False
        self.patient_name: Optional[str] = None
        
        # State tracking for booking
        self.current_intent: Optional[str] = None
        self.pending_slot: Optional[str] = None # e.g., "NEEDS_DOCTOR", "NEEDS_DATE", "NEEDS_TIME", "CONFIRMATION"
        self.selected_doctor: Optional[str] = None
        self.selected_department: Optional[str] = None
        self.selected_date: Optional[str] = None
        self.selected_time: Optional[str] = None

        # Call transcript history
        self.transcripts = []

    def add_transcript(self, sender: str, text: str):
        self.transcripts.append({"sender": sender, "text": text})

class ConversationManager:
    _sessions: Dict[str, ConversationSession] = {}

    @classmethod
    def get_or_create_session(cls, session_id: Optional[str] = None, caller_phone: str = "9876543210") -> ConversationSession:
        if not session_id or session_id not in cls._sessions:
            new_id = session_id or str(uuid.uuid4())
            session = ConversationSession(new_id, caller_phone)
            cls._sessions[new_id] = session
            return session
        return cls._sessions[session_id]

    @classmethod
    def reset_session(cls, session_id: str):
        if session_id in cls._sessions:
            del cls._sessions[session_id]
