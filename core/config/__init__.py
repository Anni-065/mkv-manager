"""
Config Module

This module contains configuration constants and settings
for the MKV Manager application.
"""

from .constants import (
    LANG_TITLES, QUALITY_TAGS, QUALITY_PATTERNS, QUALITY_TAGS_SERIES,
    ABBREVIATIONS, SEASON_EPISODE_PATTERN, QUALITY_PATTERN_SERIES, SOURCE_PATTERN
)

try:
    from .config import *
except ImportError:
    from .config_example import *

__all__ = [
    "LANG_TITLES",
    "QUALITY_TAGS",
    "QUALITY_PATTERNS",
    "QUALITY_TAGS_SERIES",
    "ABBREVIATIONS",
    "SEASON_EPISODE_PATTERN",
    "QUALITY_PATTERN_SERIES",
    "SOURCE_PATTERN",
    "MKVMERGE_PATH",
    "MKV_FOLDER",
    "OUTPUT_FOLDER",
    "ALLOWED_SUB_LANGS",
    "ALLOWED_AUDIO_LANGS",
    "DEFAULT_AUDIO_LANG",
    "DEFAULT_SUBTITLE_LANG",
    "ORIGINAL_AUDIO_LANG",
    "ORIGINAL_SUBTITLE_LANG",
    "EXTRACT_SUBTITLES",
    "SAVE_EXTRACTED_SUBTITLES"
]
