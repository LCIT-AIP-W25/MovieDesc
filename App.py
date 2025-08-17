import streamlit as st
import os
import tempfile
from datetime import datetime

try:
    import moviepy.editor as mp
except ModuleNotFoundError:
    import subprocess
    subprocess.check_call(["pip", "install", "moviepy"])
    import moviepy.editor as mp

import whisper

def extract_audio(video_path, audio_path):
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def transcribe_audio(audio_path):
    model = whisper.load_model("base")  # Load Whisper model
    result = model.transcribe(audio_path)
    return result["text"]

def main():
    st.title("🎬 AI Movie Descriptor")
    st.write("Upload a video to generate audio description and transcript.")

    uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov", "mkv"])
    
    if uploaded_file is not None:
        # Create timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("data/temp", exist_ok=True)

        # Save uploaded video
        saved_video_path = os.path.join("data", "temp", f"video_{timestamp}.mp4")
        with open(saved_video_path, "wb") as f:
            f.write(uploaded_file.read())

        # Extract audio to WAV
        audio_path = os.path.join("data", "temp", f"audio_{timestamp}.wav")
        st.write("🔊 Extracting audio...")
        extract_audio(saved_video_path, audio_path)

        # Transcribe audio
        st.write("🧠 Transcribing audio...")
        transcript_text = transcribe_audio(audio_path)

        # Save transcript to .txt
        transcript_path = os.path.join("data", "temp", f"transcript_{timestamp}.txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        # Show transcript
        st.subheader("📝 Generated Transcript:")
        st.code(transcript_text, language='markdown')

        # Download button for transcript
        with open(transcript_path, "rb") as file:
            st.download_button(
                label="📥 Download Transcript",
                data=file,
                file_name=f"transcript_{timestamp}.txt",
                mime="text/plain"
            )

        # Show video
        st.subheader("🎥 Uploaded Video:")
        st.video(saved_video_path)

if __name__ == "__main__":
    main()
