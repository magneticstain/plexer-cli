"""
Plexer - Normalize media files for use with Plex Media Server

Module: File Manager - code for file-related ops
"""

from os import scandir
from magic import from_file
from logzero import logger

from .artifact import Artifact
from .metadata import Metadata

class FileManager:
    """
    Class used for any file-related ops
    """

    def __init__(self) -> None:
        pass

    def get_artifacts(self, tgt_dir: str) -> list:
        """
        Gather the names of all files and directories in a given directory and return as list
        """

        artifacts = []

        with scandir(tgt_dir) as sd_iter:
            for artifact_entry in sd_iter:
                new_artifact = Artifact(
                    name=artifact_entry.name,
                    path=artifact_entry.path,
                    mime_type=from_file(artifact_entry.path, mime=True)
                )

                logger.debug(
                    "new file artifact found: [ FILE: %s | PATH: %s | FILE TYPE: %s ]",
                    new_artifact.name,
                    new_artifact.absolute_path,
                    new_artifact.mime_type
                )

                # metadata file must be prepended to ensure it's read in first during processing
                if artifact_entry.name == ".plexer":
                    artifacts = [new_artifact] + artifacts
                else:
                    artifacts.append(new_artifact)

        return artifacts

    def process_directory(self, dir_artifacts: list) -> bool:
        """
        Traverse the given directory artifacts, rename the 
          video files accordingly, and delete everything else
        
        NOTE: the artifact for the metadata file MUST come first 
          in the artifact list. Failing to do so may lead to instability
          during artifact processing.
        """

        video_metadata = Metadata()

        for artifact in dir_artifacts:
            if artifact.mime_type == "directory":
                # process each directory recursively
                logger.debug("found directory inside directory; processing new directory")
                new_dir_artifacts = self.get_artifacts(tgt_dir=artifact.absolute_path)
                self.process_directory(dir_artifacts=new_dir_artifacts)
            elif artifact.name == ".plexer":
                # read in video metadata
                video_metadata.import_metadata_from_file(file_path=artifact.absolute_path)
            elif artifact.mime_type.startswith("video/"):
                # rename
                pass
            else:
                # delete the file
                pass

        return True
