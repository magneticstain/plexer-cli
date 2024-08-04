"""
Plexer - Normalize media files for use with Plex Media Server

Module: Artifact Class
"""

class Artifact:
    """
    General artifact object
    """

    name = ""
    absolute_path = ""
    mime_type = ""

    def __init__(self, name: str, path: str, mime_type: str) -> None:
        self.name = name
        self.absolute_path = path
        self.mime_type = mime_type
