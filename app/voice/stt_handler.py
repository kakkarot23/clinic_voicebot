class STTHandler:
    @staticmethod
    def process_speech_input(text_or_audio: str) -> str:
        """
        Accepts recognized speech text or string from front-end WebSpeech / STT API
        and cleans it.
        """
        if not text_or_audio:
            return ""
        cleaned = text_or_audio.strip()
        return cleaned
