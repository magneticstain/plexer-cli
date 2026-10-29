"""
Plexer - Normalize media files for use with Plex Media Server

Module: Const - collection of global variables used across the application
"""

ARTIFACT_NAME_REGEX = r"^(.+) (\([\d]{4}\)) ?(\{edition-.+\})?$"
ARTIFACT_HEURISTICS_PATTERNS = {
    "name": r"^(.+?)([\.\-\_\(\[][1|2])",  # anything before the first instance of commonly-used separators
    "common_editions": r"(?:[Dd]irector(?:')?s|[Ff]inal|[Ee]xtended|[Tt]heatrical|[Uu]nrated)[\.\-\_ ](?:Cut|Edit)|Uncut",  # common multi-word edition names (e.g., "Directors Cut", "Theatrical Edit", etc.)
    "edition": r"([A-Za-z0-9']+)([\.\-\_ ]{1})([Ee][Dd][Ii][Tt][Ii][Oo][Nn])|(?:{edition-)(.+)(?:})",  # "XXX edition" (case-insensitive) or standard Plex format
    "release_year": r"(19|20)([0-9]{2})",  # any 4 digit number between 1900 and 2099
}
# file extensions to keep (and rename) inside media directories; any other file is deleted
# extensions are compared in lowercase, so entries must be lowercase and include the leading period
ARTIFACT_VIDEO_FILE_EXTENSIONS = frozenset(
    {
        ".avi",
        ".m2ts",
        ".m4v",
        ".mkv",
        ".mov",
        ".mp4",
        ".mpeg",
        ".mpg",
        ".ts",
        ".webm",
        ".wmv",
    }
)
ARTIFACT_SUBTITLE_FILE_EXTENSIONS = frozenset(
    {
        ".ass",
        ".idx",  # VobSub index (paired with .sub)
        ".smi",
        ".srt",
        ".ssa",
        ".sub",
        ".vtt",
    }
)
ARTIFACT_METADATA_FILE_EXTENSIONS = frozenset({".nfo"})
ARTIFACT_FILE_EXTENSION_WHITELIST = (
    ARTIFACT_VIDEO_FILE_EXTENSIONS
    | ARTIFACT_SUBTITLE_FILE_EXTENSIONS
    | ARTIFACT_METADATA_FILE_EXTENSIONS
)
# fallback for videos with an unrecognized extension: keep any file libmagic detects as video
ARTIFACT_VIDEO_MIME_TYPE_PREFIX = "video/"
