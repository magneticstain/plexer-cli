"""
Plexer - Normalize media files for use with Plex Media Server

Module: Const - collection of global variables used across the application
"""

ARTIFACT_NAME_REGEX = r"^(.+) (\([\d]{4}\)) ?(\{edition-.+\})?$"
ARTIFACT_HEURISTICS_PATTERNS = {
    "name": r"^(.+?)([\.\-\_\(\[][1|2])",  # anything before the first instance of commonly-used separators
    "release_year": r"(19|20)([0-9]{2})",  # any 4 digit number between 1900 and 2099
}
ARTIFACT_FILE_TYPE_WHITELIST = [
    # Videos
    "video/mp4",
    "video/x-matroska",  # .mkv
    "video/x-msvideo"  # .avi
    # Subtitles
    "application/x-subrip"  # .srt
    "text/plain"  # .sub subtitle files
    "text/subtitle"  # .sub subtitle files (ALT)
    "application/octet-stream"  # .sub index files
    # Metadata
    "text/x-nfo",  # .nfo
]

METADATA_FILE_NAME = ".plexer"
