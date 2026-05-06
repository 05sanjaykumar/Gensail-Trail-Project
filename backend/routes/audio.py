# backend/routes/audio.py
from fastapi import APIRouter, WebSocket
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.transports.websocket.fastapi import (
    FastAPIWebsocketTransport,
    FastAPIWebsocketParams,
)
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from services.STT import get_stt_service
from services.LLM import get_llm_service, get_llm_context
from services.TTS import get_tts_service

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    transport = FastAPIWebsocketTransport(
        websocket=websocket,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            add_wav_header=True,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(
                params=VADParams(stop_secs=0.5)
            ),
            vad_audio_passthrough=True,
        ),
    )

    stt = get_stt_service()
    llm = get_llm_service()
    tts = get_tts_service()
    context_aggregator = get_llm_context()

    pipeline = Pipeline([
        transport.input(),         # mic audio in
        stt,                       # speech → text
        context_aggregator.user(), # add user msg to context
        llm,                       # text → response
        tts,                       # response → audio
        context_aggregator.assistant(), # save assistant reply
        transport.output(),        # audio → browser
    ])

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
        ),
    )

    await transport.connect()

    runner = PipelineRunner()
    await runner.run(task)