"""
MKV Manager Core Module

This module contains the core functionality for processing MKV files,
including track filtering, subtitle deduplication, and file remuxing.
"""

from .processing.mkv_processor import filter_and_remux, log_entry
from .analysis.track_analyzer import get_track_info, is_forced_subtitle_by_name
from .analysis.filename_processor import extract_series_info
from .subtitles.subtitle_processor import deduplicate_subtitles
from .subtitles.subtitle_converter import convert_subtitle_to_srt, is_srt_format
from .subtitles.subtitle_extractor import extract_and_convert_subtitles
from .processing.mkv_operations import run_mkvmerge
from .utils.text_utils import break_long_subtitle_lines
from .config.constants import LANG_TITLES, QUALITY_TAGS, QUALITY_PATTERNS

__version__ = "1.0.0"
__all__ = [
    "filter_and_remux",
    "log_entry",
    "get_track_info",
    "is_forced_subtitle_by_name",
    "extract_series_info",
    "deduplicate_subtitles",
    "convert_subtitle_to_srt",
    "is_srt_format",
    "run_mkvmerge",
    "extract_and_convert_subtitles",
    "break_long_subtitle_lines",
    "LANG_TITLES",
    "QUALITY_TAGS",
    "QUALITY_PATTERNS"
]
