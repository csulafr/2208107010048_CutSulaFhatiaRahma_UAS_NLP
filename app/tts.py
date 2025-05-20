import os
import uuid
import tempfile
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# path ke folder utilitas TTS
COQUI_DIR = os.path.join(BASE_DIR, "coqui_utils")

# File model harus berada di dalam folder coqui_utils/
COQUI_MODEL_PATH = os.path.join(COQUI_DIR, "checkpoint_1260000-inference.pth")
# File config.json harus berada di dalam folder coqui_utils/
COQUI_CONFIG_PATH = os.path.join(COQUI_DIR, "config.json")
# File speakers.pth harus berada di dalam folder coqui_utils/
COQUI_SPEAKERS_PATH = os.path.join(COQUI_DIR, "speakers.pth")
# Nama speaker yang digunakan
COQUI_SPEAKER = "wibowo"

def transcribe_text_to_speech(text: str) -> str:
    """
    Fungsi untuk mengonversi teks menjadi suara menggunakan TTS engine yang ditentukan.
    Args:
        text (str): Teks yang akan diubah menjadi suara.
    Returns:
        str: Path ke file audio hasil konversi.
    """
    path = tts_with_coqui(text)
    return path

# === ENGINE 1: Coqui TTS ===
def tts_with_coqui(text: str) -> str:
    tmp_dir = tempfile.gettempdir()
    output_path = os.path.join(tmp_dir, f"tts_{uuid.uuid4()}.wav")
    
    # Letakkan file speakers.pth ke lokasi yang benar
    # Ini adalah solusi sementara jika file ada di lokasi yang salah
    if not os.path.exists(COQUI_SPEAKERS_PATH):
        print(f"[WARNING] speakers.pth not found at {COQUI_SPEAKERS_PATH}")
    
    # Menambahkan environment variable untuk menemukan file speakers.pth
    env = os.environ.copy()
    env["TTS_SPEAKERS_PATH"] = COQUI_SPEAKERS_PATH
    
    # jalankan Coqui TTS dengan subprocess
    cmd = [
        "tts",
        "--text", text,
        "--model_path", COQUI_MODEL_PATH,
        "--config_path", COQUI_CONFIG_PATH,
        "--speaker_idx", COQUI_SPEAKER,
        "--speakers_file_path", COQUI_SPEAKERS_PATH,  # Tambahkan parameter ini
        "--out_path", output_path
    ]
    
    try:
        # Tambahkan stderr untuk melihat error lengkap
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
        print(f"TTS Output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] TTS subprocess failed: {e}")
        print(f"Error output: {e.stderr}")
        return "[ERROR] Failed to synthesize speech"
    
    return output_path