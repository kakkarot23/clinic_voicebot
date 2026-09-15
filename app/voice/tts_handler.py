import os
import io
import asyncio
import edge_tts
from gtts import gTTS
from app.config import settings

class TTSHandler:
    @staticmethod
    async def generate_malayalam_audio(text: str) -> bytes:
        """
        Generates Malayalam audio bytes using Edge-TTS (ml-IN-SobhanaNeural)
        with fallback to gTTS (ml).
        """
        if not text:
            text = "നമസ്കാരം"
            
        try:
            # Primary: edge-tts for high quality neural Malayalam voice
            communicate = edge_tts.Communicate(text, settings.TTS_DEFAULT_VOICE)
            audio_buffer = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.write(chunk["data"])
            audio_buffer.seek(0)
            data = audio_buffer.read()
            if len(data) > 0:
                return data
        except Exception as e:
            print(f"EdgeTTS failed ({e}), falling back to gTTS...")

        try:
            # Fallback: gTTS
            tts = gTTS(text=text, lang="ml")
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer.read()
        except Exception as e:
            print(f"gTTS failed: {e}")
            return b""
