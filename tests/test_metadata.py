"""
Plexer Unit Tests - Metadata.py
"""

import pytest

from plexer_cli.metadata import Metadata


class TestMetadata:
    """
    Unit Tests - Metadata
    """

    @pytest.fixture
    def metadata(self) -> Metadata:
        """Generate a Metadata() obj for tests"""
        return Metadata()

    def test_metadata_initialization(self):
        """Test Metadata object initialization with custom values"""

        custom_name = "Custom Title"
        custom_edition = "Director's Cut"
        custom_year = 2020

        metadata = Metadata(
            name=custom_name, edition=custom_edition, release_year=custom_year
        )

        assert metadata.name == custom_name
        assert metadata.edition == custom_edition
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
        assert metadata.name == "The Matrix"
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

    def test_do_heuristic_analysis_period_delimited(self, metadata):
        """Test heuristic analysis with period-delimited file naming convention"""

        # Use format that matches the pattern (name followed by separator)
        file_name = "Movie.Title.2015.1080p.BluRay.mkv"
        result = metadata.do_heuristic_analysis(file_name)

        assert result is True
        assert metadata.name == "Movie Title"
        assert metadata.release_year == 2015
        assert metadata.metadata_found is True

    def test_do_heuristic_analysis_multiple_years(self, metadata):
        """Test heuristic analysis with multiple years - should use the last one"""

        file_name = "Movie_1999-2020-Release"
        result = metadata.do_heuristic_analysis(file_name)

        assert result is True
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

    def test_do_heuristic_analysis_edition_common(self, metadata):
        """Test heuristic analysis for common edition names"""

        file_name = "Movie.Title.2015.1080p.BluRay.Directors.Cut.Edition.mkv"
        result = metadata.do_heuristic_analysis(file_name)

        assert result is True
        assert metadata.name == "Movie Title"
        assert metadata.edition == "Directors Cut"
        assert metadata.release_year == 2015
        assert metadata.metadata_found is True

    def test_do_heuristic_analysis_edition_generic(self, metadata):
        """Test heuristic analysis for more generic edition names"""

        file_name = "Movie.Title.2015.1080p.BluRay.SuperDuper.Edition.mkv"
        result = metadata.do_heuristic_analysis(file_name)

        assert result is True
        assert metadata.name == "Movie Title"
        assert metadata.edition == "SuperDuper"
        assert metadata.release_year == 2015
        assert metadata.metadata_found is True
