"""
MKV Manager Core Module

This module contains the core functionality for processing MKV files,
including track filtering, subtitle deduplication, and file remuxing.
"""

from .mkv_cleaner import filter_and_remux, get_track_info, extract_series_info, deduplicate_subtitles
from .constants import LANG_TITLES, QUALITY_TAGS, QUALITY_PATTERNS

__version__ = "1.0.0"
__all__ = [
    "filter_and_remux",
    "get_track_info",
    "extract_series_info",
    "deduplicate_subtitles",
    "LANG_TITLES",
    "QUALITY_TAGS",
    "QUALITY_PATTERNS"
]
