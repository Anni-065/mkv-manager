#!/usr/bin/env python3
"""
GUI components for the main window of the MKV Cleaner Desktop Application
"""

from .header import HeaderComponent
from .language_settings import LanguageSettingsComponent
from .file_selection import FileSelectionComponent
from .output_options import OutputOptionsComponent
from .process_section import ProcessSectionComponent

__all__ = [
    'HeaderComponent',
    'LanguageSettingsComponent',
    'FileSelectionComponent',
    'OutputOptionsComponent',
    'ProcessSectionComponent'
]