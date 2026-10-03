"""
Plexer Unit Tests - File_Manager.py
"""

from os import mkdir
import os

import pytest
from moviepy import ColorClip

from plexer_cli.file_manager import FileManager
from plexer_cli.artifact import Artifact
from plexer_cli.metadata import Metadata


class TestFileManager:
    """
    Unit Tests - FileManager
    """

    @pytest.fixture
    def video_data(self):
        """Create in-mem video data

        Currently generates a 100 x 100, 3s black video clip"""

        vid_clip = ColorClip(size=(100, 100), color=(0, 0, 0), duration=3)

        return vid_clip

    @pytest.fixture
    def preloaded_media_dir(self, video_data, tmp_path):
        """Create a tmp directory containing all files needed for testing"""

        # generate test files
        invalid_file = f"{tmp_path}/invalid.txt"
        media_file = f"{tmp_path}/test.mp4"

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

    def test_check_artifact_valid_format(self, file_mgr):
        """Test artifact validation with valid Plex naming format"""

        valid_artifact = Artifact(
            name="Movie Title (2020)",
            path="/tmp/Movie Title (2020)",
            mime_type="directory",
        )

        result = file_mgr.check_artifact(valid_artifact)

        assert result is True

    def test_check_artifact_valid_with_options(self, file_mgr):
        """Test artifact validation with valid Plex format including edition tag"""

        valid_artifact = Artifact(
            name="Movie Title (2020) {edition-Test Cut}",
            path="/tmp/Movie Title (2020) {edition-Test Cut}",
            mime_type="directory",
        )

        result = file_mgr.check_artifact(valid_artifact)

        assert result is True

    def test_check_artifact_invalid_format(self, file_mgr):
        """Test artifact validation with invalid format"""

        invalid_artifact = Artifact(
            name="InvalidMovieName", path="/tmp/InvalidMovieName", mime_type="directory"
        )

        result = file_mgr.check_artifact(invalid_artifact)

        assert result is False

    def test_check_artifact_invalid_missing_year(self, file_mgr):
        """Test artifact validation with missing year"""

        invalid_artifact = Artifact(
            name="Movie Title", path="/tmp/Movie Title", mime_type="directory"
        )

        result = file_mgr.check_artifact(invalid_artifact)

        assert result is False

    def test_rename_artifact(self, file_mgr, tmp_path):
        """Test artifact renaming with valid metadata"""

        # Create a test file
        test_file = f"{tmp_path}/oldname.txt"
        with open(test_file, "w") as f:
            f.write("test")

        artifact = Artifact(name="oldname.txt", path=test_file, mime_type="text/plain")

        metadata = Metadata(name="New Title", release_year=2021, metadata_found=True)
        renamed_artifact = file_mgr.rename_artifact(artifact, metadata)

        # Check that artifact object was updated
        assert renamed_artifact.name == "New Title (2021)"
        assert "New Title (2021).txt" in renamed_artifact.absolute_path

    def test_rename_artifact_dry_run(self, file_mgr, tmp_path):
        """Test artifact renaming in dry run mode"""

        # Create a test file
        test_file = f"{tmp_path}/oldname.txt"
        with open(test_file, "w") as f:
            f.write("test")

        original_path = test_file
        artifact = Artifact(name="oldname.txt", path=test_file, mime_type="text/plain")

        metadata = Metadata(name="New Title", release_year=2021, metadata_found=True)
        renamed_artifact = file_mgr.rename_artifact(artifact, metadata, dry_run=True)

        # In dry run mode, artifact object is NOT updated
        assert renamed_artifact.name == "oldname.txt"
        # Original file should still exist and not be renamed
        assert os.path.exists(original_path)

    def test_rename_artifact_same_source_and_dest(self, file_mgr, tmp_path):
        """Test renaming when source and destination paths are identical"""

        test_file = f"{tmp_path}/oldname (1900).txt"
        with open(test_file, "w") as f:
            f.write("test")

        # Use path that matches metadata to avoid actual rename
        artifact = Artifact(
            name="oldname (1900).txt", path=test_file, mime_type="text/plain"
        )

        # Use metadata that will generate the same name as what we have
        metadata = Metadata(name="oldname", release_year=1900, metadata_found=True)
        file_mgr.rename_artifact(artifact, metadata)

        # File should not be renamed since src/dst are same
        assert os.path.exists(test_file)

    def test_process_artifacts(self, file_mgr, preloaded_media_dir):
        """Process the artifacts in preloaded media directory as is and confirm the results"""

        pmd_artifacts = file_mgr.get_artifacts(tgt_dir=preloaded_media_dir)

        # Should complete without raising an exception
        file_mgr.process_artifacts(
            artifacts=pmd_artifacts,
            video_metadata=Metadata(
                name="New Title", release_year=2021, metadata_found=True
            ),
            prompt_behavior="none",
        )

        # Verify the video file is still present
        assert os.path.exists(f"{preloaded_media_dir}/New Title (2021).mp4")

    def test_process_artifacts_dry_run(self, file_mgr, preloaded_media_dir):
        """Process the artifacts in preloaded media directory in dry run mode"""

        pmd_artifacts = file_mgr.get_artifacts(tgt_dir=preloaded_media_dir)

        # Get original file list
        original_files = set(os.listdir(preloaded_media_dir))

        # Process in dry run mode
        file_mgr.process_artifacts(
            artifacts=pmd_artifacts,
            video_metadata=Metadata(
                name="New Title", release_year=2021, metadata_found=True
            ),
            prompt_behavior="none",
            dry_run=True,
        )

        # Verify no files were modified
        current_files = set(os.listdir(preloaded_media_dir))
        assert original_files == current_files

    def test_process_artifacts_empty_dir(self, file_mgr):
        """Process the artifacts of empty dir"""

        # Should complete without raising an exception
        file_mgr.process_artifacts(artifacts=[])
