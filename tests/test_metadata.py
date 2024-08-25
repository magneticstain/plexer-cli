"""
Plexer Unit Tests - Metadata.py
"""

import pytest
import const
from plexer.const import METADATA_FILE_NAME
from plexer.metadata import Metadata

class TestMetadata:

    @pytest.fixture
    def metadata_file(self, tmp_path) -> str:
        metadata_file_path = f"{tmp_path}/{METADATA_FILE_NAME}"

        with open(metadata_file_path, "w", encoding="utf-8") as f:
            f.write(const.get_serialized_test_metadata())
        
        return metadata_file_path

    @pytest.fixture
    def bad_metadata_file(self, tmp_path) -> str:
        metadata_file_path = f"{tmp_path}/{METADATA_FILE_NAME}"

        with open(metadata_file_path, "w", encoding="utf-8") as f:
            f.write(const.get_serialized_test_metadata(tainted=True))
        
        return metadata_file_path

    @pytest.fixture
    def metadata(self) -> Metadata:
        return Metadata()


    def test_import_metadata_from_file(self, metadata, metadata_file):
        metadata.import_metadata_from_file(metadata_file)

        assert metadata.name == const.TEST_MEDIA_NAME
        assert metadata.release_year == const.TEST_MEDIA_RELEASE_YEAR
