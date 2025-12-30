"""
Plexer - Normalize media files for use with Plex Media Server

Module: Metadata - code for analyzing and managing video metadata
"""

import json
import re
from logzero import logger
from prompt_toolkit import PromptSession


class Metadata:
    """
    Code used for managing the metadata of a given video file, especially names
    """

    name = ""
    release_year = 1900
    metadata_found = False
    heuristics_patterns = {
        "name": r"^(.+?)([\-\_\(\[])",  # anything before the first instance of a common separator
        "release_year": r"(19|20)[0-9]{2}",  # any 4 digit number between 1900 and 2099
    }

    def __init__(self, name="", release_year=1900) -> None:
        self.name = name
        if release_year >= 0:
            self.release_year = release_year

    def do_heuristic_analysis(self, file_name: str) -> bool:
        """
        Analyze given file name and attempt to extract metadata values via heuristics
        """

        logger.debug("performing heuristic analysis on artifact: %s", file_name)

        # basic heuristics
        possible_name = re.search(self.heuristics_patterns["name"], file_name)
        if possible_name:
            self.name = possible_name.group(1).replace(".", " ").strip()
        possible_release_year = re.search(
            self.heuristics_patterns["release_year"], file_name
        )
        if possible_release_year:
            self.release_year = int(possible_release_year.group(0))

        if possible_name and possible_release_year:
            logger.debug(
                "heuristic analysis results - name: %s, release_year: %d",
                self.name,
                self.release_year,
            )

            self.metadata_found = True
            return True

        logger.debug("heuristic analysis produced partial or no results")
        return False

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
            logger.error(
                'data missing in metadata file; "%s" field was not found', e.args[0]
            )

    def prompt_user_for_metadata(self) -> None:
        """
        Prompt the user for metadata values via CLI input
        """

        logger.debug("prompting user for metadata input")

        prompt_sess = PromptSession()

        user_name = prompt_sess.prompt(
            "Enter the correct name for this media: ", default=self.name
        )
        user_release_year = prompt_sess.prompt(
            "Enter the release year for this media: ", default=str(self.release_year)
        )

        self.name = user_name
        self.release_year = int(user_release_year)
        self.metadata_found = True
