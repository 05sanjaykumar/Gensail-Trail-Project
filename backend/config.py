# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# LLM
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = "llama3-70b-8192"

# STT - NVIDIA Nemotron
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# TTS - Kokoro (local, no key needed)
KOKORO_VOICE = os.getenv("KOKORO_VOICE", "af_heart")

# App
DEBUG = os.getenv("DEBUG", "false").lower() == "true"