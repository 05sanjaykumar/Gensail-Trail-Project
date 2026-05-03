from fastapi import FastAPI
from routes.audio import router as audio_router

app = FastAPI()

app.include_router(audio_router)

@app.get("/")
def root():
    return {"status": "running 🚀"}