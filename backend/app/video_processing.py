import os
import cv2
from moviepy.editor import VideoFileClip

def extract_frame(file_path, filename):
    print(">>> Running extract_frame")
    print(f">>> Received file_path: {file_path}")
    print(f">>> Received filename: {filename}")

    # Save to backend/app/temp/frames
    abs_frame_dir = os.path.join(os.path.dirname(__file__), "temp", "frames")
    os.makedirs(abs_frame_dir, exist_ok=True)

    # Load clip
    clip = VideoFileClip(file_path)
    duration = clip.duration
    size = os.path.getsize(file_path)
    size_mb = size / (1024 * 1024)

    # Get 1st second frame (or 0.5s if short)
    frame_time = 1 if duration >= 1 else 0.5
    frame = clip.get_frame(frame_time)

    # Save frame
    frame_filename = filename.replace(".mp4", ".jpg")
    full_save_path = os.path.join(abs_frame_dir, frame_filename)
    cv2.imwrite(full_save_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    # Normalize path
    relative_path = f"/temp/frames/{frame_filename}".replace("\\", "/")

    return {
        "message": "Upload successful!",
        "filename": filename,
        "duration_sec": round(duration, 2),
        "size_mb": round(size_mb, 2),
        "frame_path": relative_path
    }
