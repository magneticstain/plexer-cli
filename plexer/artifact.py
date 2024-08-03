"""
Plexer - Normalize media files for use with Plex Media Server

Module: Artifact Class
"""

class Artifact:
    """
    General artifact object
    """

    name = ""
    path = ""
    file_type = ""

    def __init__(self, name: str, path: str, file_type: str) -> None:
        self.name = name
        self.path = path
        self.file_type = file_type
