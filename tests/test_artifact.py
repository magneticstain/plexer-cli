"""
Plexer Unit Tests - Artifact.py
"""

from plexer_cli.artifact import Artifact


class TestArtifact:
    """
    Unit Tests - Artifact
    """

    def test_artifact_initialization(self):
        """Test Artifact object initialization with valid data"""

        name = "test.mp4"
        path = "/tmp/test.mp4"
        mime_type = "video/mp4"

        artifact = Artifact(name=name, path=path, mime_type=mime_type)

        assert artifact.name == name
        assert artifact.absolute_path == path
        assert artifact.mime_type == mime_type

    def test_artifact_initialization_directory(self):
        """Test Artifact object initialization for a directory"""

        name = "test_dir"
        path = "/tmp/test_dir"
        mime_type = "directory"

        artifact = Artifact(name=name, path=path, mime_type=mime_type)

        assert artifact.name == name
        assert artifact.absolute_path == path
        assert artifact.mime_type == mime_type

    def test_artifact_name_modification(self):
        """Test modifying artifact name after initialization"""

        artifact = Artifact(
            name="old_name", path="/tmp/old_name", mime_type="text/plain"
        )
        new_name = "new_name"

        artifact.name = new_name

        assert artifact.name == new_name

    def test_artifact_path_modification(self):
        """Test modifying artifact path after initialization"""

        artifact = Artifact(name="test", path="/tmp/old_path", mime_type="text/plain")
        new_path = "/tmp/new_path"

        artifact.absolute_path = new_path

        assert artifact.absolute_path == new_path

    def test_artifact_mime_type_modification(self):
        """Test modifying artifact mime type after initialization"""

        artifact = Artifact(name="test", path="/tmp/test", mime_type="text/plain")
        new_mime_type = "application/json"

        artifact.mime_type = new_mime_type

        assert artifact.mime_type == new_mime_type

    def test_artifact_with_special_characters(self):
        """Test Artifact initialization with special characters in name"""

        name = "Movie Title (2020) {edition}.mkv"
        path = "/tmp/Movie Title (2020) {edition}.mkv"
        mime_type = "video/x-matroska"

        artifact = Artifact(name=name, path=path, mime_type=mime_type)

        assert artifact.name == name
        assert artifact.absolute_path == path
        assert artifact.mime_type == mime_type

    def test_artifact_with_unicode_characters(self):
        """Test Artifact initialization with unicode characters"""

        name = "文件名.txt"
        path = "/tmp/文件名.txt"
        mime_type = "text/plain"

        artifact = Artifact(name=name, path=path, mime_type=mime_type)

        assert artifact.name == name
        assert artifact.absolute_path == path
        assert artifact.mime_type == mime_type

    def test_artifact_empty_mime_type(self):
        """Test Artifact with empty mime type"""

        name = "test"
        path = "/tmp/test"
        mime_type = ""

        artifact = Artifact(name=name, path=path, mime_type=mime_type)

        assert artifact.mime_type == ""
