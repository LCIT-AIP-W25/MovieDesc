import torch
import av
import numpy as np
from PIL import Image
from torchvision.transforms import ToTensor
import gtts  # Google Text-to-Speech for generating audio from text

def extract_frames(video_path, num_frames=16, method="uniform"):
    """Extract a fixed number of key frames from a video for BLIP analysis.
    
    Args:
        video_path: Path to the video file (MP4)
        num_frames: Number of frames to extract
        method: Sampling method ('uniform' for evenly spaced, or 'scene' for scene-based detection)
    
    Returns:
        List of PIL Image objects representing key frames.
    """
    frames = []
    container = av.open(video_path)
    stream = container.streams.video[0]
    total_frames = stream.frames
    frame_interval = max(1, total_frames // num_frames)  # Ensure at least 1 frame interval

    if method == "uniform":
        frame_count = 0
        for i, frame in enumerate(container.decode(stream)):
            if i % frame_interval == 0 and len(frames) < num_frames:
                frame = frame.to_rgb().to_ndarray()
                frames.append(Image.fromarray(frame))
    elif method == "scene":
        # Hypothetical scene detection (e.g., using PySceneDetect or motion analysis)
        # For simplicity, use uniform sampling for now
        frame_count = 0
        for i, frame in enumerate(container.decode(stream)):
            if i % frame_interval == 0 and len(frames) < num_frames:
                frame = frame.to_rgb().to_ndarray()
                frames.append(Image.fromarray(frame))

    container.close()
    return frames

def create_audio_description(descriptions, output_path, lang='en', slow=False):
    """Convert descriptions (e.g., LLM narrative) to audio using text-to-speech."""
    # Handle a single narrative or list of descriptions
    if isinstance(descriptions, str):
        text = descriptions
    else:
        text = " ".join(descriptions)
    
    tts = gtts.gTTS(text=text, lang=lang, slow=slow)
    tts.save(output_path)
    return output_path