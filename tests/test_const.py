"""
Plexer Unit Tests - Const.py
"""

import re

import pytest

from plexer_cli.const import (
    ARTIFACT_FILE_EXTENSION_WHITELIST,
    ARTIFACT_METADATA_FILE_EXTENSIONS,
    ARTIFACT_SUBTITLE_FILE_EXTENSIONS,
    ARTIFACT_VIDEO_FILE_EXTENSIONS,
)


class TestConst:
    """
    Unit Tests - Const
    """

    @pytest.mark.parametrize("file_ext", sorted(ARTIFACT_FILE_EXTENSION_WHITELIST))
    def test_file_extension_whitelist_format(self, file_ext):
        """Test that each whitelisted extension is a single, lowercase extension with a leading period

        Guards against malformed entries, e.g. two adjacent strings concatenated by a missing comma (#176)
        """

        assert re.fullmatch(r"\.[a-z0-9]+", file_ext)

    def test_file_extension_whitelist_contents(self):
        """Test that the whitelist is the union of the video, subtitle, and metadata extensions"""

        assert ARTIFACT_FILE_EXTENSION_WHITELIST == (
            ARTIFACT_VIDEO_FILE_EXTENSIONS
            | ARTIFACT_SUBTITLE_FILE_EXTENSIONS
            | ARTIFACT_METADATA_FILE_EXTENSIONS
        )

    @pytest.mark.parametrize("file_ext", [".avi", ".srt", ".sub", ".idx", ".nfo"])
    def test_file_extension_whitelist_previously_deleted(self, file_ext):
        """Test that the file types from #176 that were previously deleted are whitelisted"""

        assert file_ext in ARTIFACT_FILE_EXTENSION_WHITELIST
