import os
import re
from TTS.api import TTS

# ✅ Load Coqui TTS model once
tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=False)

# 🎙️ Speaker map from VCTK
SPEAKER_IDS = {
    "female": "p303",  # Female voice
    "male": "p315"     # Male voice
}

# 🧼 Clean filename
def sanitize_filename(text: str) -> str:
    clean_text = re.sub(r'[^\w\s-]', '', text)
    return "_".join(clean_text.strip().split())[:30] or "narration"

# 🔊 Narrate text locally
def narrate_text(text: str, speaker_gender: str = "female") -> dict:
    try:
        if not text.strip():
            return {"status": "error", "narration_path": "Empty text - narration skipped"}

        text = text.strip()[:2400]
        speaker_id = SPEAKER_IDS.get(speaker_gender.lower(), "p303")

        # ✅ FIXED: use correct global folder: backend/app/temp/narration
        narration_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "temp", "narration"))
        os.makedirs(narration_dir, exist_ok=True)

        filename = sanitize_filename(text) + ".mp3"
        output_path = os.path.join(narration_dir, filename)

        tts.tts_to_file(text=text, speaker=speaker_id, file_path=output_path)

        print(f"✅ Narration saved to {output_path}")
        return {
            "status": "success",
            "narration_path": f"/temp/narration/{filename}"
        }

    except Exception as e:
        print("❌ Narration failed:", str(e))
        return {"status": "error", "narration_path": str(e)}
