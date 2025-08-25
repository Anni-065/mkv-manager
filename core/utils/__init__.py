"""
Utils Module

This module contains utility functions for various tasks including
subprocess execution and text processing.
"""

from .subprocess_utils import run_hidden, popen_hidden, get_subprocess_kwargs
from .text_utils import break_long_subtitle_lines, process_srt_file_line_breaks

__all__ = [
    "run_hidden",
    "popen_hidden",
    "get_subprocess_kwargs",
    "break_long_subtitle_lines",
    "process_srt_file_line_breaks"
]
