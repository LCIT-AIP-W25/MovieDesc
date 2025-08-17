import os
import re
from TTS.api import TTS

# Load Coqui model
tts = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=False)

# 🎙️ Define speaker mapping
SPEAKER_IDS = {
    "female": "p303",
    "male": "p315"
}

# 🧼 Clean filename
def sanitize_filename(text: str) -> str:
    clean = re.sub(r"[^\w\s-]", "", text)
    return "_".join(clean.strip().split())[:30] or "narration"

# 🔊 Chapter narration
def narrate_chapter_text(text: str, chapter_index: int, speaker_gender: str = "female") -> dict:
    try:
        if not text.strip():
            return {"narration_path": None, "message": "Empty summary text"}

        # ✅ Get speaker ID
        speaker_id = SPEAKER_IDS.get(speaker_gender.lower(), "p303")

        # ✅ Force correct folder
        narration_dir = os.path.join(os.getcwd(), "backend", "app", "temp", "narration", "chapters")
        os.makedirs(narration_dir, exist_ok=True)

        filename = f"chapter_{chapter_index}_{sanitize_filename(text)}.mp3"
        save_path = os.path.join(narration_dir, filename)

        # ✅ Pass speaker ID
        tts.tts_to_file(text=text.strip(), file_path=save_path, speaker=speaker_id)

        print(f"✅ [CHAPTER] Narration saved to {save_path}")
        return {
            "narration_path": f"/temp/narration/chapters/{filename}"
        }

    except Exception as e:
        print(f"❌ [CHAPTER] Narration failed:", str(e))
        return {
            "narration_path": None,
            "message": str(e)
        }
