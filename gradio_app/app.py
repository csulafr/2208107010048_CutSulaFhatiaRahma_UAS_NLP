import os
import tempfile
import requests
import gradio as gr
import scipy.io.wavfile

def voice_chat(audio):
    if audio is None:
        return None
    
    sr, audio_data = audio
    
    # simpan sebagai .wav
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        scipy.io.wavfile.write(tmpfile.name, sr, audio_data)
        audio_path = tmpfile.name
    
    # kirim ke endpoint FastAPI
    with open(audio_path, "rb") as f:
        files = {"file": ("voice.wav", f, "audio/wav")}
        response = requests.post("http://localhost:8000/voice-chat", files=files)
    
    if response.status_code == 200:
        # simpan file respons audio dari chatbot
        output_audio_path = os.path.join(tempfile.gettempdir(), "tts_output.wav")
        with open(output_audio_path, "wb") as f:
            f.write(response.content)
        return output_audio_path
    else:
        return None

# UI Gradio dengan tema kustom
theme = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="blue",
    neutral_hue="slate"
)

with gr.Blocks(theme=theme, css="""
    .container { margin: 0 auto; }
    .header { text-align: center; margin-bottom: 20px; }
    .audio-container { padding: 15px; border-radius: 10px; background-color: #f5f7ff; }
    .response-container { padding: 15px; border-radius: 10px; background-color: #f0f7ff; }
""") as demo:
    gr.HTML("""
    <div class="header">
        <h1>🎙️ Voice Chatbot Indonesia</h1>
        <p>Berbicara langsung ke mikrofon dan dapatkan jawaban suara dari asisten AI</p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🎤 Pertanyaan Anda")
            audio_input = gr.Audio(
                sources="microphone", 
                type="numpy",
                label="Rekam suara Anda"
            )
            submit_btn = gr.Button("🚀 Kirim Pesan", variant="primary", size="lg")
        
        with gr.Column(scale=1):
            gr.Markdown("### 🔊 Jawaban Asisten")
            audio_output = gr.Audio(
                type="filepath",
                label="Dengarkan jawaban",
                elem_id="response-audio",
                interactive=False
            )
    
    # Footer dengan informasi tambahan
    gr.Markdown("""
    ---
    ### Cara Menggunakan
    1. Klik tombol mikrofon untuk merekam pertanyaan Anda
    2. Klik tombol "Kirim Pesan" untuk mendapatkan respons
    3. Dengarkan jawaban dari asisten AI
    """)
    
    # Menghubungkan fungsi dengan UI
    submit_btn.click(
        fn=voice_chat,
        inputs=audio_input,
        outputs=audio_output
    )

if __name__ == "__main__":
    demo.launch()
