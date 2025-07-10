import streamlit as st
import torch
import whisper
from moviepy.editor import VideoFileClip, AudioFileClip
import numpy as np

def extract_audio(video_path, output_path="data/temp/audio.wav"):
    """Extract audio from a video file."""
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_path)
    return output_path

import whisper
import os

def transcribe_audio(audio_path):
    """Transcribe audio using Whisper to detect dialogue."""
    try:
        # Debug: Check if audio file exists and is accessible
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        st.write(f"Audio file path: {audio_path}, Size: {os.path.getsize(audio_path)} bytes")

        # Load Whisper model
        model = whisper.load_model("base")
        st.write("Whisper model loaded successfully.")

        # Transcribe audio
        result = model.transcribe(audio_path)
        transcription = result["text"]
        st.write("Raw Transcription:", transcription)  # Debug
        return transcription
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        raise
def detect_dialogue_segments(transcription):
    """Detect dialogue segments from transcription (simplified)."""
    # Assume transcription has timestamps (e.g., Whisper output format)
    segments = []
    for segment in transcription["segments"]:
        start = segment["start"]  # Start time in seconds
        end = segment["end"]  # End time in seconds
        text = segment["text"].strip()
        if text and not text.isspace():  # Basic check for dialogue
            segments.append((start, end))
    return sorted(segments, key=lambda x: x[0])

def integrate_audio_description(video_path, original_audio_path, description_audio_path, output_video_path):
    """Integrate audio descriptions into the video, avoiding overlap with dialogue."""
    # Load video and audio clips
    video = VideoFileClip(video_path)
    original_audio = AudioFileClip(original_audio_path)
    desc_audio = AudioFileClip(description_audio_path)

    # Transcribe original audio to detect dialogue timestamps
    transcription = transcribe_audio(original_audio_path)
    dialogue_segments = detect_dialogue_segments(transcription)

    # Create a new audio track with descriptions inserted where there’s no dialogue
    final_audio = original_audio
    desc_position = 0  # Start position for descriptions
    for segment in dialogue_segments:
        start, end = segment  # Example: (start_time, end_time) in seconds
        if desc_position < len(desc_audio.duration):
            # Insert description audio before or after dialogue, ensuring no overlap
            desc_clip = desc_audio.subclip(desc_position, min(desc_position + 5, desc_audio.duration))
            final_audio = final_audio.set_audio_at(start - 0.1, desc_clip)  # Slight buffer before dialogue
            desc_position += desc_clip.duration

    # Set the final audio to the video
    final_video = video.set_audio(final_audio)
    final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")