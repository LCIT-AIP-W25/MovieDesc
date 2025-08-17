import os
import re
from backend.app.utils.audio_utils import slice_audio_segment
from backend.app.utils.chapter_narration import narrate_chapter_text

def sanitize_filename(text: str) -> str:
    clean_text = re.sub(r'[^\w\s-]', '', text)
    return "_".join(clean_text.strip().split())[:30] or "narration"

# 🔁 Chapter Processing Pipeline
def process_chapters(chapters: list, audio_path: str, speaker_gender: str = "female") -> list:
    if not chapters:
        print("⚠️ No chapters provided to process.")
        return []

    if not os.path.exists(audio_path):
        print(f"❌ Audio file not found: {audio_path}")
        return []

    processed_chapters = []

    for i, chapter in enumerate(chapters):
        try:
            start = chapter.get("start_sec")
            end = chapter.get("end_sec")
            summary_text = chapter.get("summary", "")

            if start is None or end is None or not summary_text.strip():
                print(f"⚠️ Skipping Chapter {i + 1} due to missing data.")
                continue

            # ✅ Slice audio segment
            audio_result = slice_audio_segment(audio_path, start, end, i + 1)
            audio_segment_path = audio_result.get("audio_segment_path")

            if not audio_segment_path or not os.path.exists(audio_segment_path):
                print(f"❌ Audio slice failed for Chapter {i + 1}")
                audio_segment_path = "Audio segment not available"

            # ✅ Narrate summary and use direct path
            narration_path = None
            try:
                narrate_result = narrate_chapter_text(
                    text=summary_text,
                    chapter_index=i + 1,
                    speaker_gender=speaker_gender
                )
                raw_path = narrate_result.get("narration_path")

                if raw_path:
                    narration_path = raw_path
                else:
                    narration_path = "Narration failed"
            except Exception as narrate_err:
                narration_path = "Narration failed"
                print(f"⚠️ Narration failed for Chapter {i + 1}:", narrate_err)

            # ✅ Combine results
            processed_chapters.append({
                "chapter": chapter.get("chapter", f"Chapter {i + 1}"),
                "start_sec": start,
                "end_sec": end,
                "start_time": chapter.get("start_time"),
                "end_time": chapter.get("end_time"),
                "transcript": chapter.get("transcript", ""),
                "summary": summary_text,
                "audio_segment_path": audio_segment_path,
                "narration_path": narration_path
            })

        except Exception as chapter_err:
            print(f"❌ Error processing Chapter {i + 1}:", chapter_err)
            continue

    return processed_chapters
