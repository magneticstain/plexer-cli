"""
Plexer - Normalize media files for use with Plex Media Server

Module: File Manager - code for file-related ops
"""

import os
import re

from pathlib import Path
from magic import from_file
from logzero import logger

from .artifact import Artifact
from .const import ARTIFACT_NAME_REGEX, ARTIFACT_FILE_TYPE_WHITELIST
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

    def check_artifact(self, artifact: Artifact) -> bool:
        """
        Perform any checks needed to determine if the artifact is valid for further processing

        Right now, this includes:
            * Checking if the artifact name is in a valid format required by Plex
        """

        valid_artifact = False

        artifact_name_reg = re.compile(ARTIFACT_NAME_REGEX)
        if artifact_name_reg.match(artifact.name):
            logger.debug(f"artifact name format is VALID: {artifact.name}")

            valid_artifact = True
        else:
            logger.debug(f"artifact name format is INVALID: {artifact.name}")

        return valid_artifact

    def rename_artifact(
        self, artifact: Artifact, video_metadata: Metadata, dry_run=False
    ) -> Artifact:
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
            f"renaming artifact: [ OLD PATH: {src_file} ] to [ NEW PATH: {dst_file} ]"
        )

        if src_file != dst_file:
            logger.debug(
                f"executing rename operation on filesystem: {src_file} -> {dst_file}"
            )
            if not dry_run:
                os.rename(src_file, dst_file)
                artifact.name = new_artifact_name
                artifact.absolute_path = dst_file
            else:
                logger.debug("dry run enabled; skipping actual rename operation")
        else:
            logger.debug(
                "source and destination paths are identical; skipping rename operation"
            )

        return artifact

    def analyze_artifact(
        self, artifact: Artifact, prompt_behavior: str, dry_run: bool
    ) -> Metadata:
        """
        Analyze the given artifact and return a Metadata object with the relevant info
        """

        logger.debug(f"starting analysis of artifact: {artifact.name}")

        # use heuristics to attempt to determine metadata from directory name
        video_metadata = Metadata()
        video_metadata.metadata_found = False

        if video_metadata.do_heuristic_analysis(file_name=artifact.name):
            logger.info(
                f"metadata found for directory via heuristics - name: {video_metadata.name}, release_year: {video_metadata.release_year}",
            )
            video_metadata.metadata_found = True

        if prompt_behavior == "all" or (
            prompt_behavior == "default" and not video_metadata.metadata_found
        ):
            logger.info(
                "user requested all prompts OR empty or incomplete metadata found for directory via heuristics; prompting user for manual input"
            )
            video_metadata.prompt_user_for_metadata()

        return video_metadata

    def process_artifacts(
        self,
        artifacts: list,
        video_metadata=Metadata(),
        prompt_behavior="default",
        dry_run=False,
    ) -> None:
        """
        Traverse the given set of artifacts, rename the video files accordingly, and delete everything else.

        Subdirectories are processed recursively.
        """

        logger.debug("starting artifact processing")

        for artifact in artifacts:
            logger.info(
                f"processing artifact: [ FILE: {artifact.name} | PATH: {artifact.absolute_path} | FILE TYPE: {artifact.mime_type} ]"
            )

            if artifact.mime_type == "directory":
                logger.info(
                    "subdirectory found; assuming media directory and processing accordingly"
                )

                # perform analysis for video metadata
                generated_video_metadata = self.analyze_artifact(
                    artifact=artifact,
                    prompt_behavior=prompt_behavior,
                    dry_run=dry_run,
                )

                if generated_video_metadata.metadata_found:
                    logger.info(
                        "analysis successful, metadata found; renaming artifact based on gathered metadata"
                    )

                    artifact = self.rename_artifact(
                        artifact=artifact,
                        video_metadata=generated_video_metadata,
                        dry_run=dry_run,
                    )

                    video_metadata = generated_video_metadata
                else:
                    logger.warning(
                        "no metadata found for directory after exhausting all methods; skipping artifact processing"
                    )

                    continue

                # once metadata is available, start recursive subprocessing
                new_dir_artifacts = self.get_artifacts(tgt_dir=artifact.absolute_path)
                if new_dir_artifacts:
                    self.process_artifacts(
                        artifacts=new_dir_artifacts,
                        video_metadata=video_metadata,
                        prompt_behavior=prompt_behavior,
                        dry_run=dry_run,
                    )
            else:
                if not video_metadata.metadata_found:
                    raise ValueError(
                        f"file artifact found ({artifact.name}) but no video metadata provided; unable to proceed"
                    )

                logger.info(
                    f"file artifact found, processing accordingly: {artifact.name}"
                )

                # delete any files with file-types not whitelisted; rename whitelisted files accordingly
                if artifact.mime_type not in ARTIFACT_FILE_TYPE_WHITELIST:
                    logger.warning(
                        f"file artifact is not a whitelisted file type; deleting: {artifact.name}"
                    )
                    if not dry_run:
                        os.remove(artifact.absolute_path)
                    else:
                        logger.debug(
                            "dry run enabled; skipping actual delete operation"
                        )
                else:
                    logger.debug(
                        "file artifact is a whitelisted file type", artifact.mime_type
                    )

                    if self.check_artifact(artifact=artifact):
                        logger.info(
                            "file artifact already in a valid format, skipping rename operation"
                        )
                    else:
                        logger.info(
                            "file artifact is NOT in a valid format; renaming accordingly"
                        )

                        artifact = self.rename_artifact(
                            artifact=artifact,
                            video_metadata=video_metadata,
                            dry_run=dry_run,
                        )
