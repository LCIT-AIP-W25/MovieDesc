import os
from pydub import AudioSegment

def split_audio_by_chapters(audio_path: str, chapters: list, output_dir: str = "backend/app/temp/chapter_audios") -> list:
    os.makedirs(output_dir, exist_ok=True)
    audio = AudioSegment.from_file(audio_path)

    chapter_audio_paths = []

    for chapter in chapters:
        start_ms = int(chapter["start_time"] * 1000)
        end_ms = int(chapter["end_time"] * 1000)
        segment = audio[start_ms:end_ms]

        filename = f"chapter_{chapter['scene_number']}.mp3"
        output_path = os.path.join(output_dir, filename)
        segment.export(output_path, format="mp3")

        chapter_audio_paths.append({
            "scene_number": chapter["scene_number"],
            "start_time": chapter["start_time"],
            "end_time": chapter["end_time"],
            "audio_path": output_path
        })

    return chapter_audio_paths
