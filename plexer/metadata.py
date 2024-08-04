"""
Plexer - Normalize media files for use with Plex Media Server

Module: Metadata - code for analyzing and managing video metadata
"""

import json
from logzero import logger

class Metadata:
    """
    Code used for managing the metadata of a given video file, especially names
    """

    name = ""
    release_year = 0

    def __init__(self, name="", release_year=1900) -> None:
        self.name = name
        self.release_year = release_year

    def import_metadata_from_file(self, file_path: str) -> None:
        """
        Read in given file and process data into metadata values
        """

        logger.debug("metadata file found @ %s - importing data", file_path)

        with open(file_path, mode="r", encoding="utf-8") as metadata_file:
            imported_metadata = json.load(metadata_file)

        logger.debug("data imported as: %s", imported_metadata)

        try:
            self.name = imported_metadata["name"]
            self.release_year = imported_metadata["release_year"]
        except KeyError as e:
            logger.error("data missing in metadata file; \"%s\" field was not found", e.args[0])
