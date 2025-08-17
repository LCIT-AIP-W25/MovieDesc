from backend.app.routes.results import router as results_router
from backend.app.routes.auth import router as auth_router
from backend.app.routes.fetch import router as fetch_router
from backend.app.routes.upload import router as upload_router
import os
from fastapi.responses import FileResponse
from fastapi import Request
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize FastAPI app
app = FastAPI(title="EchoMind API", version="1.0")

# 🔍 Debug print
print("✅ Connected to MongoDB Atlas")
print("🔑 ELEVEN API KEY:", os.getenv("ELEVENLABS_API_KEY"))

# ✅ CORS config (for Vite frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or "*" for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Import routers (absolute paths)

# ✅ Mount routers
app.include_router(upload_router, prefix="/upload", tags=["Upload"])
app.include_router(fetch_router, prefix="/fetch", tags=["Fetch"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(results_router, tags=["Results"])


@app.get("/download/{folder}/{filename}")
async def download_file(folder: str, filename: str, request: Request):
    file_path = os.path.join("backend", "app", "temp", folder, filename)
    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            media_type="application/octet-stream",
            filename=filename,
        )
    return {"error": "File not found"}


# ✅ Mount static folders
app.mount("/temp/frames",
          StaticFiles(directory="backend/app/temp/frames"), name="frames")
app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")
app.mount("/temp_videos",
          StaticFiles(directory="backend/temp_videos"), name="temp_videos")
app.mount("/temp/narration",
          StaticFiles(directory="backend/app/temp/narration"), name="narration")
app.mount("/temp/narration/chapters", StaticFiles(
    directory="backend/app/temp/narration/chapters"), name="narration_chapters")

# ✅ Root check


@app.get("/", tags=["Root"])
def root():
    return {"message": "✅ EchoMind Backend is running"}
