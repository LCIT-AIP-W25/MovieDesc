import unittest
import re
import os

# Function to extract cluster and video ID from frame filenames
def extract_video_id_and_cluster(frame_filename):
    match = re.search(r"cluster_(\d+)_video_(\d+)", frame_filename)
    if match:
        return match.group(1), match.group(2)  # Return cluster ID and video ID
    return None, None

# Function to map extracted frames based on cluster and video ID
def map_extracted_frames(frame_dir):
    frame_mapping = {}
    for frame_filename in os.listdir(frame_dir):
        if frame_filename.endswith((".png", ".jpg", ".jpeg")):
            cluster_id, video_id = extract_video_id_and_cluster(frame_filename)
            if cluster_id and video_id:
                frame_mapping.setdefault((cluster_id, video_id), []).append(frame_filename)
    return frame_mapping

# Unit test class for frame mapping
class TestFrameMapping(unittest.TestCase):
    def setUp(self):
        self.input_dir = "test_frames"
        os.makedirs(self.input_dir, exist_ok=True)
        self.test_files = [
            "cluster_1_video_2_frame_001.jpg", 
            "cluster_1_video_2_frame_002.jpg", 
            "cluster_3_video_4_frame_001.jpg"
        ]
        for filename in self.test_files:
            open(os.path.join(self.input_dir, filename), 'a').close()

    def tearDown(self):
        for filename in os.listdir(self.input_dir):
            os.remove(os.path.join(self.input_dir, filename))
        os.rmdir(self.input_dir)
    
    def test_valid_filename(self):
        frame_filename = "cluster_12_video_34_frame_001.jpg"
        cluster_id, video_id = extract_video_id_and_cluster(frame_filename)
        self.assertEqual(cluster_id, "12")
        self.assertEqual(video_id, "34")
    
    def test_invalid_filename(self):
        frame_filename = "random_image.jpg"
        cluster_id, video_id = extract_video_id_and_cluster(frame_filename)
        self.assertIsNone(cluster_id)
        self.assertIsNone(video_id)
    
    def test_partial_match(self):
        frame_filename = "cluster_7_video_.jpg"
        cluster_id, video_id = extract_video_id_and_cluster(frame_filename)
        self.assertIsNone(cluster_id)
        self.assertIsNone(video_id)
    
    def test_frame_mapping(self):
        expected_mapping = {
            ('1', '2'): ["cluster_1_video_2_frame_001.jpg", "cluster_1_video_2_frame_002.jpg"],
            ('3', '4'): ["cluster_3_video_4_frame_001.jpg"]
        }
        frame_mapping = map_extracted_frames(self.input_dir)
        self.assertEqual(frame_mapping, expected_mapping)

if __name__ == "__main__":
    unittest.main()
