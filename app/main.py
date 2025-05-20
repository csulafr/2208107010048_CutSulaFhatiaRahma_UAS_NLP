from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import shutil

# Import fungsi dari modul lain
from app.stt import transcribe_speech_to_text
from app.llm import generate_response
from app.tts import transcribe_text_to_speech

# Import G2P untuk konversi teks ke fonem
from g2p_id import G2P

# Inisialisasi aplikasi dan G2P
app = FastAPI()
g2p = G2P()

# Izinkan CORS agar bisa diakses dari frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ubah ini sesuai kebutuhan produksi
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/voice-chat")
async def voice_chat(file: UploadFile = File(...)):
    try:
        # 1. Baca file audio dari request
        audio_bytes = await file.read()

        # 2. Transkripsi audio ke teks
        transcribed_text = transcribe_speech_to_text(audio_bytes, file_ext=os.path.splitext(file.filename)[-1])
        if transcribed_text.startswith("[ERROR]"):
            raise HTTPException(status_code=500, detail=transcribed_text)
        
        print(f"[DEBUG] Transcribed text: {transcribed_text}")
        print(f"[INFO] Teks transkripsi: {transcribed_text.strip()}")

        # 3. Kirim ke LLM untuk mendapatkan respons
        response_text = generate_response(transcribed_text.strip())
        if response_text.startswith("[ERROR]"):
            print(f"[ERROR] LLM Response Error: {response_text}")
            raise HTTPException(status_code=500, detail=response_text)

        print(f"[INFO] Respons Gemini: {response_text.strip()}")

        # 4. Konversi teks ke fonem (G2P)
        phonemes = g2p(response_text.strip())
        print(f"[DEBUG] Fonem hasil G2P: {phonemes}")

        # 5. Ubah respons menjadi file audio (TTS)
        # Jika transcribe_text_to_speech() mendukung fonem, ganti argumennya jadi phonemes
        audio_output_path = transcribe_text_to_speech(response_text.strip())
        if audio_output_path.startswith("[ERROR]"):
            raise HTTPException(status_code=500, detail=audio_output_path)

        # 6. Kirimkan kembali audio hasil TTS
        return FileResponse(audio_output_path, media_type="audio/wav", filename="response.wav")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Jalankan server hanya jika file ini dijalankan langsung
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)