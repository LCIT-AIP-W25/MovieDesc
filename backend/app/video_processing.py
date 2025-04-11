import os
import logging
import time
import cv2  # OpenCV for fallback
import moviepy.editor as mp
from PIL import Image
from typing import List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_frames(video_path: str, num_frames: int = 16, method: str = "uniform") -> Tuple[List[Image.Image], float]:
    """
    Extracts frames from a video file using MoviePy with an OpenCV fallback and retry mechanism.

    Args:
        video_path (str): Path to the video file.
        num_frames (int): Number of frames to extract.
        method (str): Method for selecting frames ('uniform' or 'random').

    Returns:
        Tuple[List[Image.Image], float]: A list of PIL Image objects and the video duration in seconds.

    Raises:
        ValueError: If the video cannot be opened or frames cannot be extracted by either method.
    """
    max_retries = 3
    moviepy_failed = False

    # --- Try MoviePy First ---
    for attempt in range(max_retries):
        video = None  # Initialize video object outside try block for cleanup
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries} using MoviePy to open: {video_path}")
            video = mp.VideoFileClip(video_path)
            video_duration = video.duration
            if video_duration is None or video_duration <= 0:
                raise ValueError("MoviePy could not determine video duration.")
            logger.info(f"MoviePy: Video duration: {video_duration:.2f} seconds")
            logger.info(f"MoviePy: Video reader FPS: {getattr(video, 'fps', 'N/A')}, size: {getattr(video, 'size', 'N/A')}")

            frame_times = []
            if method == "uniform":
                if num_frames == 1:
                    frame_times = [video_duration / 2]
                else:
                    step = video_duration / (num_frames - 1)
                    frame_times = [min(i * step, video_duration) for i in range(num_frames)]
                    frame_times[-1] = min(frame_times[-1], video_duration)
            elif method == "random":
                import random
                frame_times = sorted([video_duration * random.random() for _ in range(num_frames)])
            else:
                raise ValueError(f"Unsupported frame extraction method: {method}")

            frame_times = [max(0, min(t, video_duration)) for t in frame_times]
            logger.info(f"MoviePy: Target frame times: {[f'{t:.2f}' for t in frame_times]}")

            frames_data = [video.get_frame(t) for t in frame_times]
            if not frames_data or any(f is None for f in frames_data):
                raise ValueError("MoviePy failed to retrieve one or more frames.")

            frames = [Image.fromarray(frame) for frame in frames_data]
            logger.info(f"MoviePy: Successfully extracted {len(frames)} frames.")
            video.close()
            return frames, video_duration

        except Exception as e:
            logger.error(f"MoviePy Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if video:
                try:
                    video.close()
                except Exception as close_err:
                    logger.error(f"Error closing video clip after failure: {close_err}")
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                logger.warning("MoviePy failed after all retries.")
                moviepy_failed = True

    # --- Fallback to OpenCV ---
    if moviepy_failed:
        logger.info("Attempting fallback using OpenCV.")
        cap = None  # Initialize cap outside try block for cleanup
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"OpenCV could not open video file: {video_path}")

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            if fps <= 0 or frame_count <= 0:
                raise ValueError("OpenCV could not determine valid video properties (fps/frame_count).")

            video_duration_cv = frame_count / fps
            logger.info(f"OpenCV: Video duration: {video_duration_cv:.2f} seconds, FPS: {fps:.2f}, Frames: {int(frame_count)}")

            frame_times = []
            if method == "uniform":
                if num_frames == 1:
                    frame_times = [video_duration_cv / 2]
                else:
                    step = video_duration_cv / (num_frames - 1)
                    frame_times = [min(i * step, video_duration_cv) for i in range(num_frames)]
                    frame_times[-1] = min(frame_times[-1], video_duration_cv)
            elif method == "random":
                import random
                frame_times = sorted([video_duration_cv * random.random() for _ in range(num_frames)])
            else:
                raise ValueError(f"Unsupported frame extraction method: {method}")

            frame_times = [max(0, min(t, video_duration_cv)) for t in frame_times]
            logger.info(f"OpenCV: Target frame times: {[f'{t:.2f}' for t in frame_times]}")

            frames = []
            for t in frame_times:
                frame_idx = int(t * fps)
                frame_idx = max(0, min(frame_idx, int(frame_count) - 1))
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"OpenCV: Failed to read frame at index {frame_idx} (time {t:.2f}s). Skipping.")
                    continue
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(frame_rgb))

            cap.release()
            if not frames:
                raise ValueError("OpenCV fallback extracted 0 frames.")
            logger.info(f"OpenCV: Successfully extracted {len(frames)} frames.")
            return frames, video_duration_cv

        except Exception as e:
            logger.error(f"OpenCV fallback failed: {str(e)}")
            if cap and cap.isOpened():
                cap.release()
            raise ValueError(f"Failed to extract frames using both MoviePy and OpenCV. Last error (OpenCV): {str(e)}") from e

    raise RuntimeError("Frame extraction failed unexpectedly.")