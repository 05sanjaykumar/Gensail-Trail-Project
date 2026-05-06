# backend/routes/audio.py
from fastapi import APIRouter, UploadFile, File
from services.STT import transcribe_audio
from services.LLM import generate_response
from services.TTS import synthesize_speech
from services.sub_agent import verify_response

router = APIRouter()

@router.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    audio_bytes = await file.read()

    text = transcribe_audio(audio_bytes)

    response = generate_response(text)

    verified = verify_response(response)

    audio_output = synthesize_speech(verified)

    return {
        "text": verified,
        "audio": audio_output  # base64 or file path
    }