import whisper
import os

# ✅ Load model once globally (prefer 'base' for balance between speed & accuracy)
try:
    model = whisper.load_model("base")
except Exception as e:
    print("❌ Failed to load Whisper model:", str(e))
    model = None

# 🔊 Transcribe full audio
def transcribe_audio_whisper(audio_path: str) -> dict:
    try:
        abs_path = os.path.abspath(audio_path)
        if not os.path.exists(abs_path):
            return {"status": "error", "message": f"File not found: {abs_path}"}
        if model is None:
            return {"status": "error", "message": "Whisper model not loaded"}

        print(f"🧠 Whisper is transcribing full audio: {abs_path}")
        result = model.transcribe(abs_path)

        return {
            "status": "success",
            "text": result["text"]
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

# 🔁 Transcribe multiple chapter audio segments
def transcribe_chapter_audios(chapter_audio_paths: list) -> list:
    results = []

    for chapter in chapter_audio_paths:
        audio_path = chapter.get("audio_path")
        scene_number = chapter.get("scene_number")

        print(f"🧠 Transcribing Chapter {scene_number}...")

        if not os.path.exists(audio_path):
            results.append({
                "scene_number": scene_number,
                "start_time": chapter.get("start_time"),
                "end_time": chapter.get("end_time"),
                "transcript": f"[Error]: File not found"
            })
            continue

        try:
            result = model.transcribe(audio_path)
            results.append({
                "scene_number": scene_number,
                "start_time": chapter.get("start_time"),
                "end_time": chapter.get("end_time"),
                "transcript": result["text"]
            })

        except Exception as e:
            results.append({
                "scene_number": scene_number,
                "start_time": chapter.get("start_time"),
                "end_time": chapter.get("end_time"),
                "transcript": f"[Error]: {str(e)}"
            })

    return results
