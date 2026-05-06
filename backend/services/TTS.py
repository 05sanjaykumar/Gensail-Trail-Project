from config import KOKORO_VOICE
from pipecat.services.kokoro import KokoroTTSService

def get_tts_service():
    return KokoroTTSService(
        settings=KokoroTTSService.Settings(
            voice=KOKORO_VOICE,
        )
    )