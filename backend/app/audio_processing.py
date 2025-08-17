import os
from moviepy.editor import VideoFileClip

# Save audio to: backend/app/temp/audio
AUDIO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "temp", "audio"))
os.makedirs(AUDIO_DIR, exist_ok=True)

def extract_audio(file_path: str, filename: str) -> dict:
    try:
        print(">>> Running extract_audio")
        video_clip = VideoFileClip(file_path)

        if video_clip.audio is None:
            raise ValueError("❌ No audio stream found in video")

        base_filename = os.path.splitext(filename)[0]
        output_audio_path = os.path.join(AUDIO_DIR, f"{base_filename}.wav")

        video_clip.audio.write_audiofile(output_audio_path, codec='pcm_s16le')
        print(f"✅ Audio saved to: {output_audio_path}")

        return {"audio_path": output_audio_path}

    except Exception as e:
        print(f"❌ Error extracting audio: {e}")
        return {"error": str(e), "audio_path": None}
