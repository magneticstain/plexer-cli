"""
Plexer Unit Tests - File_Manager.py
"""

from os import mkdir

import pytest
import moviepy.editor

from plexer_cli.const import METADATA_FILE_NAME
from plexer_cli.file_manager import FileManager


class TestFileManager:
    """
    Unit Tests - FileManager
    """

    @pytest.fixture
    def video_data(self):
        """Create in-mem video data

        Currently generates a 100 x 100, 3s black video clip"""

        vid_clip = moviepy.editor.ColorClip(
            size=(100, 100), color=(0, 0, 0), duration=3
        )

        return vid_clip

    @pytest.fixture
    def preloaded_media_dir(self, good_serialized_metadata, video_data, tmp_path):
        """Create a tmp directory containing all files needed for testing"""

        # generate metadata file, invalid file, and video file
        metadata_file = f"{tmp_path}/{METADATA_FILE_NAME}"
        invalid_file = f"{tmp_path}/invalid.txt"
        media_file = f"{tmp_path}/test.mp4"

        with open(metadata_file, "w", encoding="utf-8") as mf:
            mf.write(good_serialized_metadata)

        with open(invalid_file, "w", encoding="utf-8") as mf:
            mf.write(":()")

        video_data.write_videofile(media_file, fps=24)

        return str(tmp_path)

    @pytest.fixture
    def file_mgr(self, tmp_path):
        """Generate a FileManager() object for tests"""

        src_dir = f"{tmp_path}/src"
        dst_dir = f"{tmp_path}/dst"

        mkdir(src_dir)
        mkdir(dst_dir)

        return FileManager(src_dir=src_dir, dst_dir=dst_dir)

    def test_get_artifacts_default_dir(self, file_mgr):
        """Test get_artifacts() function with default directory as target"""

        artifacts = file_mgr.get_artifacts()

        assert artifacts == []

    def test_get_artifacts_random_dir(self, file_mgr, tmp_path):
        """Test get_artifacts() function with tmp directory as target"""

        artifacts = file_mgr.get_artifacts(tgt_dir=tmp_path)

        # src/ and dst/ directories
        assert len(artifacts) == 2

    def test_get_artifacts_nonexistant_dir(self, file_mgr):
        """Test get_artifacts() function with nonexistant directory as target"""

        tgt_dir = "/a/b/c/d/e"

        with pytest.raises(FileNotFoundError):
            file_mgr.get_artifacts(tgt_dir=tgt_dir)

    def test_prep_artifacts(self, file_mgr, preloaded_media_dir):
        """Test the prepping of artifacts using default/expected values"""

        artifacts = file_mgr.get_artifacts(tgt_dir=preloaded_media_dir)
        artifacts = file_mgr.prep_artifacts(artifacts=artifacts)

        assert artifacts[0].name == ".plexer"

    def test_prep_artifacts_empty_dir(self, file_mgr):
        """Test the prepping of artifacts when no artifacts are found"""

        orig_artifacts = []
        prepped_artifacts = file_mgr.prep_artifacts(artifacts=orig_artifacts)

        assert prepped_artifacts == orig_artifacts

    def test_process_directory(self, file_mgr, preloaded_media_dir):
        """Process the artifacts in preloaded media directory as is and confirm the results"""

        pmd_artifacts = file_mgr.get_artifacts(tgt_dir=preloaded_media_dir)

        prepped_pmd_artifacts = file_mgr.prep_artifacts(artifacts=pmd_artifacts)

        file_mgr.process_directory(dir_artifacts=prepped_pmd_artifacts)

        assert True

    def test_process_directory_empty_dir(self, file_mgr):
        """Process the artifacts of empty dir"""

        file_mgr.process_directory(dir_artifacts=[])

        assert True
