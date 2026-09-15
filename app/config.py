import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "കേരള മെഡിക്കൽ - മലയാളം & ഇംഗ്ലീഷ് ഹോസ്പിറ്റൽ വോയ്സ് അസിസ്റ്റന്റ്"
    HOSPITAL_NAME: str = "കേരള മെഡിക്കൽ സെന്റർ & മൾട്ടിസ്പെഷ്യാലിറ്റി ഹോസ്പിറ്റൽ"
    ENGLISH_HOSPITAL_NAME: str = "Kerala Medical Center & Multispecialty Hospital"
    EMERGENCY_CONTACT: str = "+91 484 2999999 / 108"
    EMERGENCY_DESK_NUM: str = "108 / Extension 999"
    DEFAULT_LANGUAGE: str = "ml" # ml or en
    DATABASE_URL: str = "sqlite:///./hospital_voicebot.db"
    TTS_DEFAULT_VOICE_ML: str = "ml-IN-SobhanaNeural" # Edge TTS Malayalam voice
    TTS_DEFAULT_VOICE_EN: str = "en-IN-NeerjaNeural" # Edge TTS English voice

settings = Settings()
