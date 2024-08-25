"""
Plexer Unit Tests - Constant Global Vars
"""


import json


TEST_MEDIA_NAME = "Unit Test 2: The Failures Return (in 3-D)"
TEST_MEDIA_RELEASE_YEAR = 2024

def get_serialized_test_metadata(tainted=False) -> str:
    metadata = {
        "name": TEST_MEDIA_NAME,
        "release_year": TEST_MEDIA_RELEASE_YEAR
    }

    if tainted:
        del metadata["release_year"]

    return json.dumps(metadata)
