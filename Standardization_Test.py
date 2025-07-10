import unittest
import os
import cv2
from collections import defaultdict

# FILE: Extracting Frames/test_Standardization.ipynb

from Extracting_Frames.Standardization import main_function  # type: ignore # Assuming the main code is encapsulated in a function

class TestStandardization(unittest.TestCase):
    def setUp(self):
        # Setup code to create a mock environment if necessary
        self.input_dir = "../downloaded_videos"
        self.output_dir = "standardized_videos"
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        # Create mock video files for testing
        self.create_mock_video("video_1.mp4", 640, 480, 30)
        self.create_mock_video("video_2.mp4", 320, 240, 15)
    def tearDown(self):
        # Cleanup code to remove mock environment
        for filename in os.listdir(self.input_dir):
            os.remove(os.path.join(self.input_dir, filename))
        for filename in os.listdir(self.output_dir):
            os.remove(os.path.join(self.output_dir, filename))
        os.rmdir(self.input_dir)
        os.rmdir(self.output_dir)
    
    def create_mock_video(self, filename, width, height, fps):
        # Create a mock video file with given specifications
        filepath = os.path.join(self.input_dir, filename)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filepath, fourcc, fps, (width, height))
        for _ in range(30):  # 30 frames
            frame = cv2.imread('path_to_sample_image.jpg')  # Use a sample image
            frame = cv2.resize(frame, (width, height))
            out.write(frame)
        out.release()
    
    def test_input_directory_exists(self):
        self.assertTrue(os.path.exists(self.input_dir))
    
    def test_lowest_resolution_and_fps(self):
        min_width, min_height, min_fps = main_function.analyze_videos(self.input_dir)
        self.assertEqual(min_width, 320)
        self.assertEqual(min_height, 240)
        self.assertEqual(min_fps, 15)
    
    def test_video_clustering(self):
        clusters = main_function.group_videos(self.input_dir)
        self.assertIn('1', clusters)
        self.assertIn('2', clusters)
    
    def test_standardization_process(self):
        main_function.standardize_videos(self.input_dir, self.output_dir)
        for filename in os.listdir(self.output_dir):
            self.assertTrue(filename.endswith(".mp4"))
            output_path = os.path.join(self.output_dir, filename)
            self.assertTrue(os.path.getsize(output_path) > 0)

if __name__ == '__main__':
    unittest.main()