# Gensail Voice AI

A real-time, low-latency voice AI assistant built with [Pipecat](https://github.com/pipecat-ai/pipecat). Speak into the mic — the bot listens, thinks, and talks back. End-to-end pipeline: **STT → LLM → TTS** over a WebSocket connection.

---

## Architecture

```
Browser (Next.js)
    │
    │  WebSocket (Protobuf frames)
    ▼
FastAPI Backend (Pipecat Pipeline)
    │
    ├── NVIDIA Nemotron  →  Speech-to-Text
    ├── Groq (Llama 3.1 8B)  →  LLM Response
    └── Kokoro TTS (local)  →  Text-to-Speech
```

Audio flows in both directions over a single persistent WebSocket connection. The Pipecat pipeline orchestrates all three services in sequence with VAD (Voice Activity Detection) handling turn-taking automatically.

---

## Tech Stack

### Backend
| Component | Service | Details |
|---|---|---|
| Framework | FastAPI | WebSocket server, REST health endpoint |
| Pipeline | Pipecat | Orchestrates the STT → LLM → TTS chain |
| STT | NVIDIA Nemotron | Cloud-based, high-accuracy speech recognition |
| LLM | Groq — Llama 3.1 8B Instant | Ultra-fast inference via Groq API |
| TTS | Kokoro TTS (local) | Runs on-device, voice: `af_heart` |
| VAD | Silero VAD | Detects when the user starts/stops speaking |
| Serialization | Protobuf | Efficient binary framing over WebSocket |

### Frontend
| Component | Library |
|---|---|
| Framework | Next.js 16 (App Router) |
| Pipecat Client | `@pipecat-ai/client-js` |
| Transport | `@pipecat-ai/websocket-transport` |
| Styling | Tailwind CSS |

---

## Project Structure

```
Gensail-Trail-Project/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Env vars and model config
│   ├── requirements.txt
│   ├── .example.env
│   ├── routes/
│   │   └── audio.py             # WebSocket endpoint + Pipecat pipeline
│   └── services/
│       ├── STT.py               # NVIDIA Nemotron STT setup
│       ├── LLM.py               # Groq LLM + context aggregator setup
│       └── TTS.py               # Kokoro TTS setup
└── frontend/
    ├── app/
    │   └── page.tsx             # Main UI — mic button, status, transcripts
    └── ...
```

---

## How It Works

### 1. WebSocket Connection
When the user clicks the mic button, the frontend connects to `ws://localhost:8000/api/ws/voice` using the Pipecat JS client with Protobuf serialization. Both audio input (mic) and output (bot voice) travel over this single connection.

### 2. Voice Activity Detection
Silero VAD runs on the backend, listening to the incoming audio stream. It detects when the user starts and stops speaking, triggering the STT service only when speech is active (`stop_secs=0.5` — 500ms of silence ends the turn).

### 3. Speech-to-Text
NVIDIA Nemotron receives the speech audio frames and returns a text transcript. Pipecat's context aggregator appends this as a user message to the conversation history.

### 4. LLM Inference
The full conversation context is sent to Groq's Llama 3.1 8B Instant model. The system prompt keeps responses short and conversational (2–3 sentences max, no markdown formatting) — optimized for voice output.

### 5. Text-to-Speech
Kokoro TTS runs **locally** on the server and converts the LLM response to audio using the `af_heart` voice at 24kHz. Audio is streamed back as raw PCM chunks (no WAV header) over the WebSocket to the frontend.

### 6. Playback
The Pipecat JS client receives the PCM audio chunks and plays them through the browser's Web Audio API. The frontend UI updates status (`listening` / `speaking`) and displays live transcripts for both the user and the bot.

---

## Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- `espeak-ng` installed on your system (required by Kokoro TTS)

```bash
# macOS
brew install espeak-ng

# Ubuntu/Debian
sudo apt-get install espeak-ng
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy the example env file and fill in your API keys:

```bash
cp .example.env .env
```

```env
GROQ_API_KEY=your_groq_api_key
NVIDIA_API_KEY=your_nvidia_api_key
KOKORO_VOICE=af_heart
```

Run the server:

```bash
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
```

Create `.env.local`:

```env
NEXT_PUBLIC_BACKEND_WS_URL=ws://localhost:8000/api/ws/voice
```

Run the dev server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000), click the mic button, and start talking.

---

## Docker (Recommended for Deployment)

### Backend `Dockerfile`

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    espeak-ng libsndfile1 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download Kokoro voice model at build time
RUN python -c "from kokoro import KPipeline; KPipeline(lang_code='a')"

COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `docker-compose.yml`

```yaml
version: "3.9"
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_BACKEND_WS_URL=ws://backend:8000/api/ws/voice
    depends_on:
      - backend
    restart: unless-stopped
```

```bash
docker-compose up --build
```

> **Note:** Kokoro TTS is CPU-intensive. A minimum of **4GB RAM** is recommended for the backend container.

---

## Key Configuration Decisions

| Setting | Value | Reason |
|---|---|---|
| `add_wav_header` | `False` | WAV headers on every chunk break streaming — raw PCM only |
| `playerSampleRate` | `24000` | Matches Kokoro TTS output rate; mismatches cause distorted audio |
| `vad_audio_passthrough` | `False` | Prevents mic audio bleeding into the TTS output stream (causes motor noise) |
| `stop_secs` | `0.5` | 500ms silence threshold — responsive without cutting off mid-sentence |
| `allow_interruptions` | `True` | User can interrupt the bot mid-speech |

---

## API Keys

| Service | Where to get |
|---|---|
| Groq | [console.groq.com](https://console.groq.com) |
| NVIDIA Nemotron | [build.nvidia.com](https://build.nvidia.com) |

Kokoro TTS is fully local — no API key needed.

---

## Built With

- [Pipecat](https://github.com/pipecat-ai/pipecat) — Real-time voice AI pipeline framework
- [Kokoro TTS](https://github.com/hexgrad/kokoro) — Open-source local TTS
- [Groq](https://groq.com) — Ultra-fast LLM inference
- [NVIDIA NIM](https://build.nvidia.com) — Cloud STT via Nemotron
- [Next.js](https://nextjs.org) — Frontend framework
