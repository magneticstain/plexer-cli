"""
Plexer Unit Tests - File_Manager.py
"""

import os
import shutil
import threading
from os import mkdir
from pathlib import Path

import pytest
from moviepy import ColorClip

from plexer_cli.artifact import Artifact
from plexer_cli.const import ARTIFACT_FILE_EXTENSION_WHITELIST
from plexer_cli.file_manager import FileManager
from plexer_cli.metadata import Metadata

BOOTSTRAP_DIR = Path(__file__).parent / "bootstrap"


def snapshot_dir(tgt_dir) -> dict:
    """Map every path under the given directory to its contents (None for directories)"""

    snapshot = {}
    for root, dirs, files in os.walk(tgt_dir):
        for dir_name in dirs:
            snapshot[os.path.relpath(f"{root}/{dir_name}", tgt_dir)] = None
        for file_name in files:
            with open(f"{root}/{file_name}", "rb") as f:
                snapshot[os.path.relpath(f"{root}/{file_name}", tgt_dir)] = f.read()

    return snapshot


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
    def preloaded_media_dir(self, video_data, file_mgr):
        """Create a media directory in the source directory containing all files needed for testing"""

        media_dir = f"{file_mgr.src_dir}/media"
        mkdir(media_dir)

        # generate test files
        invalid_file = f"{media_dir}/invalid.txt"
        media_file = f"{media_dir}/test.mp4"

        with open(invalid_file, "w", encoding="utf-8") as mf:
            mf.write(":()")

        video_data.write_videofile(media_file, fps=24)

        return media_dir

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

    def test_rename_artifact(self, file_mgr):
        """Test artifact renaming with valid metadata"""

        # Create a test file
        test_file = f"{file_mgr.src_dir}/oldname.txt"
        with open(test_file, "w") as f:
            f.write("test")

        artifact = Artifact(name="oldname.txt", path=test_file, mime_type="text/plain")

        metadata = Metadata(name="New Title", release_year=2021, metadata_found=True)
        renamed_artifact = file_mgr.rename_artifact(artifact, metadata)

        # Check that artifact object was updated
        assert renamed_artifact.name == "New Title (2021)"
        assert "New Title (2021).txt" in renamed_artifact.absolute_path

    def test_rename_artifact_dry_run(self, file_mgr):
        """Test artifact renaming in dry run mode"""

        # Create a test file
        test_file = f"{file_mgr.src_dir}/oldname.txt"
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

    def test_rename_artifact_same_source_and_dest(self, file_mgr):
        """Test renaming when source and destination paths are identical"""

        test_file = f"{file_mgr.src_dir}/oldname (1900).txt"
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

    # Symlink handling - regression tests for GHSA-6hrq-p4m3-h6rf

    @pytest.fixture
    def outside_dir(self, tmp_path):
        """Create a directory outside of the source directory that plexer must never modify"""

        outside_dir = f"{tmp_path}/outside"

        mkdir(outside_dir)
        mkdir(f"{outside_dir}/notes")

        with open(f"{outside_dir}/important.txt", "w", encoding="utf-8") as f:
            f.write("secret")
        with open(f"{outside_dir}/photo.jpg", "w", encoding="utf-8") as f:
            f.write("not really a photo")
        with open(f"{outside_dir}/notes/todo.md", "w", encoding="utf-8") as f:
            f.write("- [ ] todo")

        return outside_dir

    def test_get_artifacts_regular_entries(self, file_mgr):
        """Test get_artifacts() still classifies regular directories and files"""

        mkdir(f"{file_mgr.src_dir}/Movie.2019.1080p")
        shutil.copy(BOOTSTRAP_DIR / "blank.mkv", f"{file_mgr.src_dir}/movie.mkv")

        artifacts = file_mgr.get_artifacts()

        assert {(a.name, a.mime_type) for a in artifacts} == {
            ("Movie.2019.1080p", "directory"),
            ("movie.mkv", "video/x-matroska"),
        }

    def test_get_artifacts_skips_symlinked_dir(self, file_mgr, outside_dir):
        """Test get_artifacts() skips symlinks to directories instead of treating them as media directories"""

        os.symlink(outside_dir, f"{file_mgr.src_dir}/Evil.2019.1080p")

        artifacts = file_mgr.get_artifacts()

        assert artifacts == []

    def test_get_artifacts_skips_symlinked_file(self, file_mgr, outside_dir):
        """Test get_artifacts() skips symlinks to files"""

        shutil.copy(BOOTSTRAP_DIR / "blank.mkv", f"{outside_dir}/movie.mkv")
        os.symlink(f"{outside_dir}/movie.mkv", f"{file_mgr.src_dir}/movie.mkv")

        artifacts = file_mgr.get_artifacts()

        assert artifacts == []

    def test_get_artifacts_skips_dangling_symlink(self, file_mgr):
        """Test get_artifacts() skips dangling symlinks instead of raising FileNotFoundError"""

        os.symlink("/a/b/c/d/e", f"{file_mgr.src_dir}/Missing.2019.1080p")

        artifacts = file_mgr.get_artifacts()

        assert artifacts == []

    @pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="requires os.mkfifo()")
    def test_get_artifacts_skips_fifo(self, file_mgr):
        """Test get_artifacts() skips FIFOs instead of blocking on them forever"""

        os.mkfifo(f"{file_mgr.src_dir}/pipe.mkv")

        # run in a daemon thread so a regression fails the test rather than hanging the suite
        artifacts = []
        worker = threading.Thread(
            target=lambda: artifacts.extend(file_mgr.get_artifacts()), daemon=True
        )
        worker.start()
        worker.join(timeout=5)

        assert not worker.is_alive(), "get_artifacts() blocked on a FIFO"
        assert artifacts == []

    @pytest.mark.skipif(
        not hasattr(os, "geteuid") or os.geteuid() == 0,
        reason="file permissions are not enforced for root",
    )
    def test_get_artifacts_skips_unreadable_file(self, file_mgr):
        """Test get_artifacts() skips unreadable files instead of raising PermissionError"""

        unreadable_file = f"{file_mgr.src_dir}/unreadable.mkv"
        shutil.copy(BOOTSTRAP_DIR / "blank.mkv", unreadable_file)
        os.chmod(unreadable_file, 0o000)

        try:
            artifacts = file_mgr.get_artifacts()
        finally:
            os.chmod(unreadable_file, 0o644)

        assert artifacts == []

    def test_process_artifacts_symlinked_dir_in_media_dir(self, file_mgr, outside_dir):
        """Test that a symlinked directory inside a media directory does not cause files outside the source directory to be modified"""

        media_dir = f"{file_mgr.src_dir}/Movie.2019.1080p"
        mkdir(media_dir)
        os.symlink(outside_dir, f"{media_dir}/Extras.2019.x")

        original_outside = snapshot_dir(outside_dir)

        file_mgr.process_artifacts(
            artifacts=file_mgr.get_artifacts(), prompt_behavior="none"
        )

        assert snapshot_dir(outside_dir) == original_outside
        # the media directory is still processed, but the symlink is left as is
        renamed_link = f"{file_mgr.src_dir}/Movie (2019)/Extras.2019.x"
        assert os.path.islink(renamed_link)
        assert os.readlink(renamed_link) == outside_dir

    def test_process_artifacts_symlinked_dir_in_src_dir(self, file_mgr, outside_dir):
        """Test that a symlinked directory at the top of the source directory is not processed as a media directory"""

        link = f"{file_mgr.src_dir}/Evil.2019.1080p"
        os.symlink(outside_dir, link)

        original_outside = snapshot_dir(outside_dir)

        file_mgr.process_artifacts(
            artifacts=file_mgr.get_artifacts(), prompt_behavior="none"
        )

        assert snapshot_dir(outside_dir) == original_outside
        assert os.path.islink(link)

    def test_process_artifacts_symlinked_file(self, file_mgr, outside_dir):
        """Test that a symlinked file is neither deleted nor renamed, and its target is untouched"""

        media_dir = f"{file_mgr.src_dir}/Movie.2019.1080p"
        mkdir(media_dir)
        shutil.copy(BOOTSTRAP_DIR / "blank.mkv", f"{outside_dir}/movie.mkv")
        os.symlink(f"{outside_dir}/movie.mkv", f"{media_dir}/movie.mkv")

        original_outside = snapshot_dir(outside_dir)

        file_mgr.process_artifacts(
            artifacts=file_mgr.get_artifacts(), prompt_behavior="none"
        )

        assert snapshot_dir(outside_dir) == original_outside
        assert os.path.islink(f"{file_mgr.src_dir}/Movie (2019)/movie.mkv")

    def test_process_artifacts_symlink_loop(self, file_mgr):
        """Test that a symlink to a parent directory does not cause infinite recursion"""

        media_dir = f"{file_mgr.src_dir}/Movie.2019.1080p"
        mkdir(media_dir)
        os.symlink("..", f"{media_dir}/Loop.2019.x")

        # Should complete without raising an exception (e.g. ELOOP)
        file_mgr.process_artifacts(
            artifacts=file_mgr.get_artifacts(), prompt_behavior="none"
        )

        assert os.listdir(file_mgr.src_dir) == ["Movie (2019)"]
        assert os.path.islink(f"{file_mgr.src_dir}/Movie (2019)/Loop.2019.x")

    def test_process_artifacts_dangling_symlink(self, file_mgr):
        """Test that a dangling symlink inside a media directory does not abort processing"""

        media_dir = f"{file_mgr.src_dir}/Movie.2019.1080p"
        mkdir(media_dir)
        os.symlink("/a/b/c/d/e", f"{media_dir}/missing.mkv")

        # Should complete without raising an exception
        file_mgr.process_artifacts(
            artifacts=file_mgr.get_artifacts(), prompt_behavior="none"
        )

        assert os.path.islink(f"{file_mgr.src_dir}/Movie (2019)/missing.mkv")

    # source directory containment - defense in depth for GHSA-6hrq-p4m3-h6rf
    def test_is_within_src_dir_inside(self, file_mgr):
        """Test that paths inside the source directory are allowed, whether or not they exist yet"""

        assert file_mgr.is_within_src_dir(f"{file_mgr.src_dir}/movie.mkv") is True
        assert (
            file_mgr.is_within_src_dir(f"{file_mgr.src_dir}/Movie (2019)/movie.mkv")
            is True
        )

    def test_is_within_src_dir_src_dir_itself(self, file_mgr):
        """Test that the source directory itself is not a valid target"""

        assert file_mgr.is_within_src_dir(file_mgr.src_dir) is False

    def test_is_within_src_dir_outside(self, file_mgr, tmp_path):
        """Test that paths outside the source directory are rejected, including siblings sharing its name as a prefix"""

        assert file_mgr.is_within_src_dir(f"{tmp_path}/outside/movie.mkv") is False
        assert file_mgr.is_within_src_dir(f"{tmp_path}/src-other/movie.mkv") is False

    def test_is_within_src_dir_traversal(self, file_mgr):
        """Test that paths escaping the source directory via '..' are rejected"""

        assert (
            file_mgr.is_within_src_dir(f"{file_mgr.src_dir}/a/../../outside/movie.mkv")
            is False
        )
        assert file_mgr.is_within_src_dir(f"{file_mgr.src_dir}/a/..") is False

    def test_is_within_src_dir_symlinked_parent(self, file_mgr, outside_dir):
        """Test that paths reaching outside the source directory via a symlinked directory are rejected"""

        os.symlink(outside_dir, f"{file_mgr.src_dir}/link")

        assert (
            file_mgr.is_within_src_dir(f"{file_mgr.src_dir}/link/important.txt")
            is False
        )

    def test_is_within_src_dir_symlink_itself(self, file_mgr, outside_dir):
        """Test that a symlink inside the source directory is allowed, since operations act on the link and not its target"""

        os.symlink(outside_dir, f"{file_mgr.src_dir}/link")

        assert file_mgr.is_within_src_dir(f"{file_mgr.src_dir}/link") is True

    def test_is_within_src_dir_symlinked_src_dir(self, tmp_path):
        """Test that a source directory given as a symlink is resolved before comparing"""

        real_src_dir = f"{tmp_path}/real_src"
        mkdir(real_src_dir)
        os.symlink(real_src_dir, f"{tmp_path}/src_link")

        file_mgr = FileManager(src_dir=f"{tmp_path}/src_link", dst_dir="")

        assert file_mgr.is_within_src_dir(f"{tmp_path}/src_link/movie.mkv") is True
        assert file_mgr.is_within_src_dir(f"{real_src_dir}/movie.mkv") is True

    def test_rename_artifact_outside_src_dir(self, file_mgr, outside_dir):
        """Test that artifacts outside the source directory are not renamed"""

        test_file = f"{outside_dir}/important.txt"
        artifact = Artifact(
            name="important.txt", path=test_file, mime_type="text/plain"
        )

        metadata = Metadata(name="New Title", release_year=2021, metadata_found=True)
        renamed_artifact = file_mgr.rename_artifact(artifact, metadata)

        assert renamed_artifact.name == "important.txt"
        assert renamed_artifact.absolute_path == test_file
        assert os.path.exists(test_file)
        assert not os.path.exists(f"{outside_dir}/New Title (2021).txt")

    def test_rename_artifact_dst_outside_src_dir(self, file_mgr, tmp_path):
        """Test that artifacts are not renamed to a destination outside the source directory"""

        test_file = f"{file_mgr.src_dir}/oldname.txt"
        with open(test_file, "w") as f:
            f.write("test")

        artifact = Artifact(name="oldname.txt", path=test_file, mime_type="text/plain")

        # e.g. a name entered at the metadata prompt
        metadata = Metadata(name="../New Title", release_year=2021, metadata_found=True)
        renamed_artifact = file_mgr.rename_artifact(artifact, metadata)

        assert renamed_artifact.name == "oldname.txt"
        assert os.path.exists(test_file)
        assert not os.path.exists(f"{tmp_path}/New Title (2021).txt")

    def test_process_artifacts_dir_outside_src_dir(self, file_mgr, outside_dir):
        """Test that a directory artifact outside the source directory is neither renamed nor emptied"""

        original_outside = snapshot_dir(outside_dir)

        file_mgr.process_artifacts(
            artifacts=[
                Artifact(
                    name="Evil.2019.1080p", path=outside_dir, mime_type="directory"
                )
            ],
            prompt_behavior="none",
        )

        assert os.path.isdir(outside_dir)
        assert snapshot_dir(outside_dir) == original_outside

    def test_process_artifacts_file_outside_src_dir(self, file_mgr, outside_dir):
        """Test that a non-whitelisted file artifact outside the source directory is not deleted"""

        original_outside = snapshot_dir(outside_dir)

        file_mgr.process_artifacts(
            artifacts=[
                Artifact(
                    name="photo.jpg",
                    path=f"{outside_dir}/photo.jpg",
                    mime_type="image/jpeg",
                )
            ],
            video_metadata=Metadata(
                name="New Title", release_year=2021, metadata_found=True
            ),
            prompt_behavior="none",
        )

        assert snapshot_dir(outside_dir) == original_outside

    ###
    # File type whitelist - regression tests for #176
    ###

    @pytest.mark.parametrize("file_ext", sorted(ARTIFACT_FILE_EXTENSION_WHITELIST))
    def test_is_whitelisted_artifact_extension(self, file_mgr, file_ext):
        """Test that files with a whitelisted extension are kept, regardless of their detected MIME type"""

        artifact = Artifact(
            name=f"movie{file_ext}",
            path=f"/tmp/movie{file_ext}",
            mime_type="application/octet-stream",
        )

        assert file_mgr.is_whitelisted_artifact(artifact) is True

    def test_is_whitelisted_artifact_extension_case_insensitive(self, file_mgr):
        """Test that file extensions are matched case-insensitively"""

        artifact = Artifact(
            name="MOVIE.SRT", path="/tmp/MOVIE.SRT", mime_type="text/plain"
        )

        assert file_mgr.is_whitelisted_artifact(artifact) is True

    def test_is_whitelisted_artifact_video_mime_type(self, file_mgr):
        """Test that files detected as video are kept even with an unrecognized extension"""

        artifact = Artifact(
            name="movie.mkv.part", path="/tmp/movie.mkv.part", mime_type="video/mp4"
        )

        assert file_mgr.is_whitelisted_artifact(artifact) is True

    @pytest.mark.parametrize(
        "file_name, mime_type",
        [
            ("notes.txt", "text/plain"),
            ("cover.jpg", "image/jpeg"),
            (".DS_Store", "application/octet-stream"),
            (".srt", "application/x-subrip"),  # dotfile with no extension
            ("movie.srt.txt", "text/plain"),
            ("download.part", "application/octet-stream"),
            ("RARBG.com.url", "text/plain"),
        ],
    )
    def test_is_whitelisted_artifact_not_whitelisted(
        self, file_mgr, file_name, mime_type
    ):
        """Test that non-media files are not kept, including generic text and binary files"""

        artifact = Artifact(
            name=file_name, path=f"/tmp/{file_name}", mime_type=mime_type
        )

        assert file_mgr.is_whitelisted_artifact(artifact) is False

    def test_process_artifacts_keeps_subtitles_and_metadata(self, file_mgr):
        """Test that video, subtitle, and metadata files survive processing and are renamed, while other files are deleted"""

        media_dir = f"{file_mgr.src_dir}/Movie.2019.1080p"
        mkdir(media_dir)

        shutil.copy(BOOTSTRAP_DIR / "blank.mp4", f"{media_dir}/movie.avi")
        shutil.copy(BOOTSTRAP_DIR / "blank.mkv", f"{media_dir}/movie.mkv.part")
        with open(f"{media_dir}/movie.srt", "w", encoding="utf-8") as f:
            f.write("1\n00:00:01,000 --> 00:00:02,000\nHello\n")
        with open(f"{media_dir}/movie.idx", "w", encoding="utf-8") as f:
            f.write("# VobSub index file, v7 (do not modify this line!)\n")
        with open(f"{media_dir}/movie.sub", "wb") as f:
            f.write(b"\x00\x00\x01\xba" + bytes(60))
        with open(f"{media_dir}/movie.nfo", "w", encoding="utf-8") as f:
            f.write("Movie (2019)\n")
        with open(f"{media_dir}/junk.txt", "w", encoding="utf-8") as f:
            f.write("downloaded from somewhere")
        with open(f"{media_dir}/cover.jpg", "w", encoding="utf-8") as f:
            f.write("not really a photo")

        file_mgr.process_artifacts(
            artifacts=file_mgr.get_artifacts(), prompt_behavior="none"
        )

        assert set(os.listdir(f"{file_mgr.src_dir}/Movie (2019)")) == {
            "Movie (2019).avi",
            "Movie (2019).part",
            "Movie (2019).srt",
            "Movie (2019).idx",
            "Movie (2019).sub",
            "Movie (2019).nfo",
        }
