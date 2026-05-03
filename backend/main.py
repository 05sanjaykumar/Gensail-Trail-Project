from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Backend running 🚀"}

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    return {"message": "Audio received"}