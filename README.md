# 🎬 MovieDesc

**MovieDesc** is an AI-powered tool that generates intelligent scene-by-scene descriptions, transcriptions, summaries, and human-like narrations from any uploaded video. It's designed to help users understand and explore the content of movies, lectures, or interviews without watching the full video.

---

## 🔍 Features

- 🎞️ **Scene Detection** — Detects and separates key moments in the video.
- 📝 **Transcription** — Converts speech to accurate text using Whisper.
- 📚 **Summarization** — Provides chapter-wise and overall summaries using LLMs.
- 🔊 **Narration** — Generates natural voiceovers for summaries using Coqui TTS.
- 📌 **Chapter Markers** — Timestamped breakdown of video chapters.
- 🖼️ **Frame Extraction** — Captures key visual frames from each scene.
- 🎧 **Audio Extraction** — Extracts audio for analysis and playback.

---

## 🚀 How It Works

1. **Upload** a video via the frontend interface.
2. The backend:
   - Extracts audio & key frames.
   - Runs transcription (via Whisper).
   - Chops video into chapters using scene detection.
   - Summarizes each chapter.
   - Generates narration for each summary.
3. Results (transcript, summary, narration, and visuals) are saved to MongoDB and displayed to the user.

---

## 🛠️ Tech Stack

| Frontend     | Backend       | AI Models     | Storage       |
|--------------|---------------|---------------|---------------|
| React.js     | FastAPI       | OpenAI / LLMs | MongoDB Atlas |
| Tailwind CSS | Python        | Whisper       | Local + Cloud |
| Axios        | Uvicorn       | Coqui TTS     | GridFS (opt)  |

---

## 📁 Project Structure




