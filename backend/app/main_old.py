from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import cv2
from moviepy.editor import VideoFileClip

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
FRAME_DIR = "temp/frames"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FRAME_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"message": "Backend is working!"}

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Get video metadata
        clip = VideoFileClip(file_path)
        duration = round(clip.duration, 2)
        clip.close()
        size_mb = round(os.path.getsize(file_path) / (1024 * 1024), 2)

        # Extract frame at 2 seconds
        cap = cv2.VideoCapture(file_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, 2000)  # 2 seconds
        success, frame = cap.read()
        cap.release()

        if success:
            frame_filename = f"{os.path.splitext(file.filename)[0]}.jpg"
            frame_path = os.path.join(FRAME_DIR, frame_filename)
            cv2.imwrite(frame_path, frame)
        else:
            frame_path = None

        return {
            "message": "Upload successful!",
            "filename": file.filename,
            "size_mb": size_mb,
            "duration_sec": duration,
            "frame_path": frame_path
        }

    except Exception as e:
        return {"error": str(e)}

from fastapi.staticfiles import StaticFiles
import os

# Serve extracted frames
app.mount(
    "/temp/frames",
    StaticFiles(directory=os.path.join("temp", "frames")),
    name="frames"
)
