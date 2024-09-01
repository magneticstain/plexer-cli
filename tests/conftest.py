"""
Plexer Unit Tests - Conftest.py - Shared Fixtures
"""

import json
import pytest

TEST_MEDIA_NAME = "Unit Test 2: The Failures Return (in 3-D)"
TEST_MEDIA_RELEASE_YEAR = 2024

@pytest.fixture
def sample_metadata() -> dict:
    """Return sample metadata used for tests in raw dict format"""

    return {
        "name": TEST_MEDIA_NAME,
        "release_year": TEST_MEDIA_RELEASE_YEAR
    }

@pytest.fixture
def good_serialized_metadata(sample_metadata) -> str:
    """Generate JSON containing valid media metadata"""

    return json.dumps(sample_metadata)

@pytest.fixture
def bad_serialized_metadata() -> str:
    """Generate JSON containing invalid media metadata"""

    sample_bad_metadata = {
        "name": TEST_MEDIA_NAME
    }

    return json.dumps(sample_bad_metadata)