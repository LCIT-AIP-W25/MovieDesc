from moviepy.editor import VideoFileClip
import os

# Point to a real video
file_path = "uploads/sample_640x360.mp4"  # replace with your file
filename = os.path.basename(file_path)
audio_dir = "temp/audio"
os.makedirs(audio_dir, exist_ok=True)

clip = VideoFileClip(file_path)
audio = clip.audio
audio_path = os.path.join(audio_dir, filename.replace(".mp4", ".wav"))
audio.write_audiofile(audio_path)
print("✅ Done:", audio_path)
