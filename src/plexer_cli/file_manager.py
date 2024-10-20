"""
Plexer - Normalize media files for use with Plex Media Server

Module: File Manager - code for file-related ops
"""

import os
from pathlib import Path
from magic import from_file
from logzero import logger

from .artifact import Artifact
from .const import METADATA_FILE_NAME
from .metadata import Metadata


class FileManager:
    """
    Class used for any file-related ops
    """

    src_dir = ""
    dst_dir = ""

    def __init__(self, src_dir, dst_dir) -> None:
        self.src_dir = src_dir
        self.dst_dir = dst_dir

    def get_artifacts(self, tgt_dir="") -> list:
        """
        Gather the names of all files and directories in a given directory and return as list


        Target directory is the source directory by default.
        """

        artifacts = []
        tgt_dir = tgt_dir if tgt_dir else self.src_dir

        with os.scandir(tgt_dir) as sd_iter:
            for artifact_entry in sd_iter:
                try:
                    artifact_mime_type = from_file(artifact_entry.path, mime=True)
                except IsADirectoryError:
                    artifact_mime_type = "directory"

                artifacts.append(
                    Artifact(
                        name=artifact_entry.name,
                        path=artifact_entry.path,
                        mime_type=artifact_mime_type,
                    )
                )

        return artifacts

    def prep_artifacts(self, artifacts: list) -> list:
        """
        Perform any processing needed to prepare the artifact data for further processing

        Right now, this includes:
            * Properly ordering artifacts such that the metadata file is first
        """

        for idx, artifact in enumerate(artifacts):
            if artifact.name == METADATA_FILE_NAME:
                # float it to the top of the artifact set
                artifacts.pop(idx)
                artifacts.insert(0, artifact)

                break

        return artifacts

    def process_directory(self, dir_artifacts: list) -> None:
        """
        Traverse the given directory artifacts, rename the
          video files accordingly, and delete everything else

        NOTE: the artifact for the metadata file MUST come first
          in the artifact list. Failing to do so may lead to instability
          during artifact processing.
        """

        metadata_file_found = False
        video_metadata = Metadata()

        logger.debug("starting directory artifact processing")

        for artifact in dir_artifacts:
            logger.info(
                "processing artifact: [ FILE: %s | PATH: %s | FILE TYPE: %s ]",
                artifact.name,
                artifact.absolute_path,
                artifact.mime_type,
            )

            if artifact.mime_type == "directory":
                logger.info("subdirectory found, processing")

                # start recursive subprocessing
                new_dir_artifacts = self.get_artifacts(tgt_dir=artifact.absolute_path)
                self.process_directory(dir_artifacts=new_dir_artifacts)
            elif artifact.name == METADATA_FILE_NAME:
                # read in video metadata
                logger.info("metadata file found, importing")

                video_metadata.import_metadata_from_file(
                    file_path=artifact.absolute_path
                )

                metadata_file_found = True
            elif artifact.mime_type.startswith("video/"):
                # move + rename
                logger.info("video file found, renaming")

                file_path = Path(artifact.absolute_path)
                file_dir = file_path.parent
                file_ext = file_path.suffix

                src_file = artifact.absolute_path
                dst_file = (
                    f"{file_dir}/{video_metadata.name}"
                    f" ({video_metadata.release_year}){file_ext}"
                )

                logger.debug("moving %s to %s", src_file, dst_file)

                os.rename(src_file, dst_file)
            else:
                # delete the file
                logger.info("unnecessary file found, deleting")

                os.remove(artifact.absolute_path)
        
        if not metadata_file_found:
            pass
