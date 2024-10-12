"""
Plexer Unit Tests - Metadata.py
"""

import pytest

from plexer_cli.const import METADATA_FILE_NAME
from plexer_cli.metadata import Metadata


class TestMetadata:
    """
    Unit Tests - Metadata
    """

    @pytest.fixture
    def metadata_file(self, good_serialized_metadata, tmp_path) -> str:
        """Generate a tmp directory containing a prefilled metadata file"""
        metadata_file_path = f"{tmp_path}/{METADATA_FILE_NAME}"

        with open(metadata_file_path, "w", encoding="utf-8") as f:
            f.write(good_serialized_metadata)

        return metadata_file_path

    @pytest.fixture
    def bad_metadata_file(self, bad_serialized_metadata, tmp_path) -> str:
        """Generate a tmp directory containing a prefilled metadata file with bad/invalid data"""
        metadata_file_path = f"{tmp_path}/{METADATA_FILE_NAME}"

        with open(metadata_file_path, "w", encoding="utf-8") as f:
            f.write(bad_serialized_metadata)

        return metadata_file_path

    @pytest.fixture
    def metadata(self) -> Metadata:
        """Generate a Metadata() obj for tests"""
        return Metadata()

    def test_import_metadata_from_file(self, metadata, metadata_file, sample_metadata):
        """Test metadata file import with valid data"""

        metadata.import_metadata_from_file(metadata_file)

        assert metadata.name == sample_metadata["name"]
        assert metadata.release_year == sample_metadata["release_year"]
