"""
Plexer - Normalize media files for use with Plex Media Server

Module: File Manager - code for file-related ops
"""

from pathlib import Path
import os
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
        Gather the names of all files and directories in a given directory and return as list.

        Target directory is the source directory by default, but can be specified via parameter.
        """

        artifacts = []
        tgt_dir = tgt_dir if tgt_dir else self.src_dir

        with os.scandir(tgt_dir) as sd_iter:
            for dir_artifact in sd_iter:
                try:
                    artifact_mime_type = from_file(dir_artifact.path, mime=True)
                except IsADirectoryError:
                    artifact_mime_type = "directory"

                artifacts.append(
                    Artifact(
                        name=dir_artifact.name,
                        path=dir_artifact.path,
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

    def rename_artifact(self, artifact: Artifact, video_metadata: Metadata) -> Artifact:
        """
        Rename an artifact to the new name generated from the given metadata

        Returns the new, updated artifact object
        """

        new_artifact_name = f"{video_metadata.name} ({video_metadata.release_year})"

        # get artifact file info for srrc/dst path generation
        artifact_file_path = Path(artifact.absolute_path)
        artifact_parent_dir = artifact_file_path.parent
        artifact_file_ext = (
            "" if artifact.mime_type == "directory" else artifact_file_path.suffix
        )

        src_file = artifact_file_path.absolute()
        dst_file = f"{artifact_parent_dir}/{new_artifact_name}{artifact_file_ext}"

        logger.debug(
            "renaming artifact: [ OLD PATH: %s ] to [ NEW PATH: %s ]",
            src_file,
            dst_file,
        )

        if src_file != dst_file:
            os.rename(src_file, dst_file)
        else:
            logger.debug(
                "source and destination paths are identical; skipping rename operation"
            )

        artifact.name = new_artifact_name
        artifact.absolute_path = dst_file

        return artifact

    def process_directory(self, dir_artifacts: list, video_metadata=Metadata()) -> None:
        """
        Traverse the given directory artifacts, rename the video files accordingly, and delete everything else
        """

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

                # use heuristics to attempt to determine metadata from directory name
                if video_metadata.do_heuristic_analysis(file_name=artifact.name):
                    logger.info(
                        "metadata found for directory via heuristics - name: %s, release_year: %d",
                        video_metadata.name,
                        video_metadata.release_year,
                    )
                else:
                    logger.info(
                        "no metadata found for directory via heuristics; prompting user for manual input"
                    )
                    video_metadata.prompt_user_for_metadata()

                if video_metadata.metadata_found:
                    logger.info("renaming artifact based on gathered metadata")
                    artifact = self.rename_artifact(
                        artifact=artifact, video_metadata=video_metadata
                    )

                    # start recursive subprocessing
                    new_dir_artifacts = self.get_artifacts(
                        tgt_dir=artifact.absolute_path
                    )
                    self.process_directory(
                        dir_artifacts=new_dir_artifacts, video_metadata=video_metadata
                    )
            else:
                logger.info("file artifact found, processing")
