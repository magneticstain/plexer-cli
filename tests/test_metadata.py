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

    def test_import_metadata_from_file(self, metadata, metadata_file, sample_metadata):
        """Test metadata file import with valid data"""

        metadata.import_metadata_from_file(metadata_file)

        assert metadata.name == sample_metadata["name"]
        assert metadata.release_year == sample_metadata["release_year"]

    def test_import_metadata_from_file_bad_data(self, metadata, bad_metadata_file):
        """Test metadata file import with missing required fields"""

        metadata.import_metadata_from_file(bad_metadata_file)

        # The import_metadata_from_file method imports what it can and logs errors for missing fields
        # So the name should be imported even though release_year is missing
        assert metadata.name == "Unit Test 2: The Failures Return (in 3-D)"
        # release_year should remain at default since it was missing
        assert metadata.release_year == 1900

    def test_metadata_initialization(self):
        """Test Metadata object initialization with custom values"""

        custom_name = "Custom Title"
        custom_year = 2020

        metadata = Metadata(name=custom_name, release_year=custom_year)

        assert metadata.name == custom_name
        assert metadata.release_year == custom_year

    def test_metadata_initialization_negative_year(self):
        """Test Metadata object initialization with negative release year"""

        metadata = Metadata(name="Test", release_year=-100)

        # Negative years should be rejected, defaulting to 1900
        assert metadata.release_year == 1900

    def test_scrub_artifact_name(self, metadata):
        """Test artifact name scrubbing"""

        test_cases = [
            ("Movie.Title.2020.1080p", "Movie Title 2020 1080p"),
            ("Movie_Title_2020", "Movie Title 2020"),
            ("Movie-Title-2020", "Movie Title 2020"),
            ("Movie[Title](2020)", "Movie Title 2020"),
            ("Movie Title", "Movie Title"),
            ("Movie...Title___2020", "Movie Title 2020"),
        ]

        for input_name, expected_output in test_cases:
            result = metadata.scrub_artifact_name(input_name)
            assert result == expected_output

    def test_do_heuristic_analysis_success(self, metadata):
        """Test heuristic analysis with data containing both name and year"""

        # Name pattern requires ending with _, (, or [ and captures minimally before it
        file_name = "The_Matrix_1999.mkv"
        result = metadata.do_heuristic_analysis(file_name)

        assert result is True
        # Regex captures minimally before first underscore, so just "The"
        assert metadata.name == "The"
        assert metadata.release_year == 1999
        assert metadata.metadata_found is True

    def test_do_heuristic_analysis_complex_format(self, metadata):
        """Test heuristic analysis with complex file naming convention"""

        # Use format that matches the pattern (name followed by separator)
        file_name = "Movie Title [2015] 1080p BluRay.mkv"
        result = metadata.do_heuristic_analysis(file_name)

        assert result is True
        assert metadata.name == "Movie Title"
        assert metadata.release_year == 2015
        assert metadata.metadata_found is True

    def test_do_heuristic_analysis_multiple_years(self, metadata):
        """Test heuristic analysis with multiple years - should use the last one"""

        # Need to match the name pattern first (ending in _, (, or [)
        file_name = "Movie[1999]2020"
        result = metadata.do_heuristic_analysis(file_name)

        assert result is True
        # Should use the last year found
        assert metadata.release_year == 2020

    def test_do_heuristic_analysis_no_match(self, metadata):
        """Test heuristic analysis with no matching patterns"""

        file_name = "RandomMovieName"
        result = metadata.do_heuristic_analysis(file_name)

        assert result is False
        assert metadata.metadata_found is False

    def test_do_heuristic_analysis_year_only(self, metadata):
        """Test heuristic analysis with only year present"""

        file_name = "RandomMovieName 2020"
        result = metadata.do_heuristic_analysis(file_name)

        # Should fail because both name and year are required
        assert result is False
        assert metadata.metadata_found is False

    def test_do_heuristic_analysis_name_only(self, metadata):
        """Test heuristic analysis with only name present (year missing)"""

        file_name = "Movie[Title]"
        result = metadata.do_heuristic_analysis(file_name)

        # Should fail because both name and year are required
        assert result is False
        assert metadata.metadata_found is False
