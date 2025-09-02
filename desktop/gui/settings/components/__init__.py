#!/usr/bin/env python3
"""
Settings Components Package

This package contains all the individual components that make up the settings window.
Each component is responsible for a specific section/tab of the settings interface.
"""

from .base_tab import BaseTabComponent
from .scrollable_tab import ScrollableTabMixin
from .paths_tab import PathsTabComponent
from .audio_languages_tab import AudioLanguagesTabComponent
from .subtitle_languages_tab import SubtitleLanguagesTabComponent
from .subtitles_tab import SubtitlesTabComponent

__all__ = [
    'BaseTabComponent',
    'ScrollableTabMixin', 
    'PathsTabComponent',
    'AudioLanguagesTabComponent',
    'SubtitleLanguagesTabComponent',
    'SubtitlesTabComponent'
]
