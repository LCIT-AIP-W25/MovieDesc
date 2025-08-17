from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

def detect_scenes(file_path: str, threshold: float = 30.0) -> dict:
    try:
        video_manager = VideoManager([file_path])
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=threshold))

        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)

        scene_list = scene_manager.get_scene_list()
        chapters = [{"start_time": str(start.get_timecode()), "end_time": str(end.get_timecode())}
                    for start, end in scene_list]

        return {"status": "success", "chapters": chapters}
    except Exception as e:
        return {"status": "error", "chapters": [], "message": str(e)}
