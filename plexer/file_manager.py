"""
Plexer - Normalize media files for use with Plex Media Server

Module: File Manager - code for file-related ops
"""

from os import scandir
from magic import from_file

from .artifact import Artifact

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
                artifacts.append(
                    Artifact(
                        name=artifact_entry.name,
                        path=artifact_entry.path,
                        file_type=from_file(artifact_entry.path, mime=True)
                    )
                )

        return artifacts
