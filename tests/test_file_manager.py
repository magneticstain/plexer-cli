"""
Plexer Unit Tests - File_Manager.py
"""

import pytest

import moviepy.editor

from const import get_serialized_test_metadata
from plexer.const import METADATA_FILE_NAME

class TestFileManager:

    @pytest.fixture
    def video_data(self):
        # create iin-mem video data
        vid_clip = moviepy.editor.TextClip("Test Video File - Plexer", fontsize=64, color="white")
        vid_clip = vid_clip.set_duration(3)

        return vid_clip

    @pytest.fixture
    def preloaded_media_dir(self, video_data, tmp_path):
        # generate metadata file, invalid file, and video file
        metadata_file = f"{tmp_path}/{METADATA_FILE_NAME}"
        invalid_file = f"{tmp_path}/invalid.txt"
        media_file = f"{tmp_path}/test.mp4"

        with open(metadata_file, "w", encoding="utf-8") as mf:
            mf.write(get_serialized_test_metadata())

        with open(invalid_file, "w", encoding="utf-8") as mf:
            mf.write(":()")
        
        video_data.write_videofile(media_file)
