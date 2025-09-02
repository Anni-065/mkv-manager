#!/usr/bin/env python3
"""
Subtitles Tab Component

Handles the subtitle settings configuration tab.
"""

import tkinter as tk
from tkinter import ttk

from .base_tab import BaseTabComponent
from .scrollable_tab import ScrollableTabMixin


class SubtitlesTabComponent(BaseTabComponent, ScrollableTabMixin):
    """
    Tab component for configuring subtitle settings.
    
    Allows users to set:
    - Whether to extract subtitles during processing
    - Whether to save extracted SRT files
    """
    
    def get_tab_name(self):
        """Return the display name for this tab."""
        return "Subtitle Options"
    
    def create_content(self):
        """Create the subtitle settings interface."""
        # Create scrollable content
        canvas, scrollable_frame = self.create_scrollable_frame(self.frame)
        
        self.setup_variables()
        self._create_extraction_section(scrollable_frame)
        self._create_info_section(scrollable_frame)
    
    def setup_variables(self):
        """Setup tkinter variables for form controls."""
        subtitle_settings = self.settings.get('subtitle_settings', {})
        
        self.variables = {
            'extract_subtitles': tk.BooleanVar(
                value=subtitle_settings.get('extract_subtitles', False)
            ),
            'save_extracted_subtitles': tk.BooleanVar(
                value=subtitle_settings.get('save_extracted_subtitles', False)
            )
        }
    
    def _create_extraction_section(self, parent):
        """Create the subtitle extraction options section."""
        extraction_label = self.create_label(
            parent, "Subtitle Extraction:", font_size=12, bold=True
        )
        extraction_label.pack(anchor='w', pady=(20, 10))
        
        extract_check = ttk.Checkbutton(
            parent,
            text="Extract subtitles to SRT format during processing",
            variable=self.variables['extract_subtitles'],
            style='Modern.TCheckbutton'
        )
        extract_check.pack(anchor='w', pady=5)
        
        save_check = ttk.Checkbutton(
            parent,
            text="Save extracted SRT files next to processed MKV files",
            variable=self.variables['save_extracted_subtitles'],
            style='Modern.TCheckbutton'
        )
        save_check.pack(anchor='w', pady=5)
    
    def _create_info_section(self, parent):
        """Create the informational text section."""
        info_text = self.create_info_text(
            parent,
            "These settings control how subtitles are handled during MKV processing. "
            "Extracting subtitles can be useful for backup or compatibility with other players."
        )
        info_text.pack(anchor='w', pady=(20, 10))
    
    def validate_settings(self):
        """
        Validate the current subtitle settings.
        
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        return True, None
    
    def get_settings_data(self):
        """
        Get the current subtitle settings.
        
        Returns:
            dict: Dictionary containing subtitle settings
        """
        return {
            'subtitle_settings': {
                'extract_subtitles': self.variables['extract_subtitles'].get(),
                'save_extracted_subtitles': self.variables['save_extracted_subtitles'].get()
            }
        }
