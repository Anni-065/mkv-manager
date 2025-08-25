"""
Subtitles Module

This module contains functionality for processing and converting subtitles,
including deduplication and format conversion.
"""

from .subtitle_processor import deduplicate_subtitles, process_subtitles_systematically
from .subtitle_converter import convert_subtitle_to_srt, is_srt_format
from .subtitle_extractor import extract_and_convert_subtitles

__all__ = [
    "deduplicate_subtitles",
    "process_subtitles_systematically",
    "convert_subtitle_to_srt",
    "is_srt_format",
    "extract_and_convert_subtitles"
]
