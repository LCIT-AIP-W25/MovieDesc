import os
import datetime
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.frame_timecode import FrameTimecode
from fastapi import APIRouter

router = APIRouter()

# 🧠 Helper: seconds to hh:mm:ss
def seconds_to_hms(seconds):
    return str(datetime.timedelta(seconds=int(seconds)))

# 🧠 Helper: summarizer (placeholder)
def summarize_text(text: str) -> str:
    return f"Summary: {text.strip()}" if text.strip() else "No content"

# 🧠 Main scene detection
def detect_scenes(video_path: str, full_transcript: str = "") -> list:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"❌ Video not found at: {video_path}")

    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=30.0))

    try:
        video_manager.set_downscale_factor()
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)

        scene_list = scene_manager.get_scene_list()
        duration = video_manager.get_duration()

        # ✅ Get video duration in seconds
        if isinstance(duration[0], FrameTimecode):
            video_duration = duration[0].get_seconds()
        else:
            video_duration = float(duration[0])

        if video_duration == 0:
            raise ValueError("❌ Video duration is zero.")

        transcript_words = full_transcript.split()
        total_words = len(transcript_words)

        scenes = []
        for i, (start, end) in enumerate(scene_list):
            try:
                start_sec = start.get_seconds()
                end_sec = end.get_seconds()
                start_idx = int((start_sec / video_duration) * total_words)
                end_idx = int((end_sec / video_duration) * total_words)
                chapter_text = " ".join(transcript_words[start_idx:end_idx])

                scenes.append({
                    "chapter": f"Chapter {i + 1}",
                    "start_sec": round(start_sec, 2),
                    "end_sec": round(end_sec, 2),
                    "start_time": seconds_to_hms(start_sec),
                    "end_time": seconds_to_hms(end_sec),
                    "transcript": chapter_text.strip(),
                    "summary": summarize_text(chapter_text)
                })
            except Exception as chapter_err:
                print(f"⚠️ Failed to process chapter {i+1}: {chapter_err}")

        return scenes

    except Exception as e:
        raise RuntimeError(f"❌ Scene detection failed: {str(e)}")
    finally:
        video_manager.release()
