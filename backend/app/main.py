from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from dotenv import load_dotenv
from pydub import AudioSegment
import time
import subprocess
import shutil
import logging

import logging
import sys

# Configure logging
logger = logging.getLogger("app.main")
logger.setLevel(logging.INFO)

# Create console handler if not already present
if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Prevent propagation to root logger to avoid duplicate logs
logger.propagate = False

from app.video_processing import extract_frames
from app.audio_processing import (
    extract_audio,
    transcribe_audio,
    create_audio_descriptions,
    integrate_audio_descriptions,
    load_whisper_model
)
from app.utils import ensure_directory, file_to_base64, cleanup_files

# Load environment variables
load_dotenv()

# --- Configuration ---
API_PORT = int(os.getenv("API_PORT", 8000))
TEMP_DIR = os.getenv("TEMP_DIR", "data/temp")
ensure_directory(TEMP_DIR)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
logger.info(f"Loaded ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")
BLIP_MODEL = os.getenv("BLIP_MODEL", "Salesforce/blip-image-captioning-base")
NUM_FRAMES = int(os.getenv("NUM_FRAMES", 10))
FRAME_METHOD = os.getenv("FRAME_METHOD", "uniform")
MAX_DESCRIPTION_LENGTH = int(os.getenv("MAX_DESCRIPTION_LENGTH", 50))
NUM_BEAMS = int(os.getenv("NUM_BEAMS", 4))

# --- Logging ---


# --- Initialize Models ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
blip_processor = None
blip_model = None

def load_models():
    global blip_processor, blip_model
    try:
        logger.info(f"Loading BLIP model '{BLIP_MODEL}' onto device: {device}")
        blip_processor = BlipProcessor.from_pretrained(BLIP_MODEL)
        blip_model = BlipForConditionalGeneration.from_pretrained(BLIP_MODEL)
        blip_model.to(device)
        blip_model.eval()
        logger.info("BLIP model loaded successfully.")
        load_whisper_model()
    except Exception as e:
        logger.error(f"FATAL: Failed to load models: {e}", exc_info=True)
        raise RuntimeError(f"Model loading failed: {e}") from e

load_models()

logger.info(f"PyTorch version: {torch.__version__}")
logger.info(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    logger.info(f"CUDA version: {torch.version.cuda}")
    logger.info(f"GPU Name: {torch.cuda.get_device_name(0)}")

# --- FastAPI App ---
app = FastAPI(title="Video Description API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware applied successfully.")
@app.post("/process-video/")
async def process_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    add_audio_desc: bool = True
):
    logger.debug("Received request to /process-video/")
    request_id = str(int(time.time() * 1000))
    base_filename = f"video_{request_id}"
    video_path = os.path.join(TEMP_DIR, f"{base_filename}.mp4")
    preprocessed_video_path = os.path.join(TEMP_DIR, f"{base_filename}_prep.mp4")
    audio_path = os.path.join(TEMP_DIR, f"{base_filename}_audio.wav")
    output_video_path = os.path.join(TEMP_DIR, f"{base_filename}_output.mp4")
    silent_audio_path = os.path.join(TEMP_DIR, f"{base_filename}_silent.wav")

    files_to_cleanup = [
        video_path, preprocessed_video_path, audio_path,
        output_video_path, silent_audio_path
    ]
    description_audio_files = []

    try:
        # 1. Save Uploaded Video
        logger.info(f"[{request_id}] Saving uploaded video to {video_path}")
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"[{request_id}] Video saved successfully.")
        file.file.close()

        # 2. Preprocess Video (FFmpeg)
        logger.info(f"[{request_id}] Preprocessing video: {video_path} -> {preprocessed_video_path}")
        ffmpeg_command = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-map', '0:v:0?',
            '-map', '0:a:0?',
            '-vf', 'scale=w=min(1080\,iw):h=min(1350\,ih):force_original_aspect_ratio=decrease',
            '-r', '30',
            '-c:v', 'libx264', '-preset', 'fast',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '128k',
            '-movflags', '+faststart',
            '-max_muxing_queue_size', '1024',
            '-shortest',
            preprocessed_video_path
        ]
        process = subprocess.run(ffmpeg_command, capture_output=True, text=True, check=False)
        if process.returncode != 0:
            logger.error(f"[{request_id}] FFmpeg preprocessing failed: {process.stderr}")
            raise ValueError(f"Video preprocessing failed: {process.stderr[:500]}")
        if not os.path.exists(preprocessed_video_path) or os.path.getsize(preprocessed_video_path) == 0:
            logger.error(f"[{request_id}] Preprocessed video file missing or empty.")
            raise ValueError("Preprocessed video file is missing or empty.")
        logger.info(f"[{request_id}] Video preprocessing successful.")

        # 3. Extract Frames
        logger.info(f"[{request_id}] Extracting frames...")
        frames, video_duration = extract_frames(preprocessed_video_path, num_frames=NUM_FRAMES, method=FRAME_METHOD)
        if not frames:
            raise ValueError("Failed to extract frames from the video.")
        logger.info(f"[{request_id}] Extracted {len(frames)} frames. Video duration: {video_duration:.2f}s")

        # 4. Generate Visual Descriptions (BLIP)
        logger.info(f"[{request_id}] Generating visual descriptions...")
        visual_descriptions = []
        for i, frame in enumerate(frames):
            try:
                if frame.mode == 'RGBA':
                    frame = frame.convert('RGB')
                inputs = blip_processor(frame, return_tensors="pt").to(device)
                with torch.no_grad():
                    outputs = blip_model.generate(
                        **inputs,
                        max_length=MAX_DESCRIPTION_LENGTH,
                        num_beams=NUM_BEAMS,
                        early_stopping=True
                    )
                description = blip_processor.decode(outputs[0], skip_special_tokens=True)
                visual_descriptions.append(description.strip())
            except Exception as e:
                logger.error(f"[{request_id}] Error processing frame {i}: {e}", exc_info=True)
                visual_descriptions.append("")
        logger.info(f"[{request_id}] Generated {len(visual_descriptions)} descriptions.")

        # 5. Extract and Transcribe Audio
        logger.info(f"[{request_id}] Extracting audio...")
        original_audio_path = extract_audio(preprocessed_video_path)
        has_audio_track = original_audio_path is not None
        if has_audio_track:
            audio_path_for_transcription = original_audio_path
            logger.info(f"[{request_id}] Audio extracted to {audio_path_for_transcription}")
        else:
            logger.info(f"[{request_id}] No audio track. Creating silent audio: {silent_audio_path}")
            AudioSegment.silent(duration=int(video_duration * 1000)).export(silent_audio_path, format="wav")
            audio_path_for_transcription = silent_audio_path
            files_to_cleanup.append(silent_audio_path)

        transcription_text = ""
        if audio_path_for_transcription and os.path.exists(audio_path_for_transcription):
            logger.info(f"[{request_id}] Transcribing audio...")
            transcription_result = transcribe_audio(audio_path_for_transcription)
            transcription_text = transcription_result.get("text", "").strip()
            logger.info(f"[{request_id}] Transcription complete. Text length: {len(transcription_text)}")
        else:
            logger.warning(f"[{request_id}] No valid audio for transcription.")

        has_actual_dialogue = has_audio_track and bool(transcription_text)

        # 6. Generate and Integrate Audio Descriptions
        final_video_to_encode = preprocessed_video_path
        if add_audio_desc:
            logger.info(f"[{request_id}] Generating audio descriptions...")
            frame_times = [float(i * (video_duration / max(1, len(frames) - 1))) for i in range(len(frames))]
            description_audio_tuples = create_audio_descriptions(
                visual_descriptions=visual_descriptions,
                frame_times=frame_times,
                video_duration=float(video_duration),
                transcription=transcription_text,
                has_actual_dialogue=has_actual_dialogue
            )
            description_audio_files = [t[0] for t in description_audio_tuples if t and os.path.exists(t[0])]
            files_to_cleanup.extend(description_audio_files)

            if description_audio_files:
                logger.info(f"[{request_id}] Integrating {len(description_audio_files)} audio descriptions...")
                integrate_audio_descriptions(
                    video_path=preprocessed_video_path,
                    original_audio_path=original_audio_path,
                    description_audios=description_audio_tuples,
                    output_path=output_video_path
                )
                if os.path.exists(output_video_path):
                    final_video_to_encode = output_video_path
                    logger.info(f"[{request_id}] Audio descriptions integrated into {output_video_path}")
                else:
                    logger.error(f"[{request_id}] Output video not generated.")
                    raise ValueError("Failed to generate output video with audio descriptions.")
            else:
                logger.warning(f"[{request_id}] No audio descriptions generated. Using preprocessed video.")
                shutil.copy(preprocessed_video_path, output_video_path)
                final_video_to_encode = output_video_path
        else:
            logger.info(f"[{request_id}] Audio descriptions disabled.")
            shutil.copy(preprocessed_video_path, output_video_path)
            final_video_to_encode = output_video_path

        # 7. Prepare Response
        logger.info(f"[{request_id}] Encoding final video...")
        output_video_base64 = file_to_base64(final_video_to_encode)
        first_audio_desc_base64 = file_to_base64(description_audio_files[0]) if description_audio_files else None

        if not output_video_base64:
            raise HTTPException(status_code=500, detail="Failed to encode final video.")

        response_data = {
            "message": "Video processed successfully.",
            "output_video": f"data:video/mp4;base64,{output_video_base64}",
            "audio_description_sample": f"data:audio/wav;base64,{first_audio_desc_base64}" if first_audio_desc_base64 else None,
            "transcription": transcription_text,
            "visual_descriptions": visual_descriptions
        }
        logger.info(f"[{request_id}] Processing complete.")
        return JSONResponse(content=response_data)

    except ValueError as ve:
        logger.error(f"[{request_id}] ValueError: {ve}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(ve))
    except FileNotFoundError as fnf:
        logger.error(f"[{request_id}] FileNotFoundError: {fnf}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

    finally:
        background_tasks.add_task(cleanup_files, files_to_cleanup)
        logger.info(f"[{request_id}] Cleanup task added for {len(files_to_cleanup)} files.")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Uvicorn server on port {API_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)