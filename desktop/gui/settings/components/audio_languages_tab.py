#!/usr/bin/env python3
"""
Audio Languages Tab Component

Handles the audio language configuration tab.
"""

import tkinter as tk
from tkinter import ttk

from .base_tab import BaseTabComponent
from .scrollable_tab import ScrollableTabMixin

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
sys.path.insert(0, root_dir)

from core.config.constants import LANG_TITLES


class AudioLanguagesTabComponent(BaseTabComponent, ScrollableTabMixin):
    """
    Tab component for configuring audio language settings.
    
    Allows users to set:
    - Available audio languages
    - Default audio language
    - Original audio language
    """
    
    def __init__(self, parent, colors, settings, user_config):
        """Initialize the audio languages tab component."""
        super().__init__(parent, colors, settings, user_config)
        
        self.audio_lang_vars = {}
        self.combo_vars = {}
    
    def get_tab_name(self):
        """Return the display name for this tab."""
        return "Audio Languages"
    
    def create_content(self):
        """Create the audio language configuration interface."""
        canvas, scrollable_frame = self.create_scrollable_frame(self.frame)
        
        self.setup_variables()
        self._create_available_languages_section(scrollable_frame)
        self._create_default_languages_section(scrollable_frame)
    
    def setup_variables(self):
        """Setup tkinter variables for form controls."""
        lang_settings = self.settings.get('language_settings', {})
        allowed_audio = lang_settings.get('allowed_audio_langs', [])
        
        for lang_code in LANG_TITLES.keys():
            self.audio_lang_vars[lang_code] = tk.BooleanVar(
                value=lang_code in allowed_audio
            )
        
        self.combo_vars = {
            'default_audio': tk.StringVar(
                value=lang_settings.get('default_audio_lang', '')
            ),
            'original_audio': tk.StringVar(
                value=lang_settings.get('original_audio_lang', '')
            )
        }
    
    def _create_available_languages_section(self, parent):
        """Create the available audio languages selection section."""
        avail_label = self.create_label(
            parent, "Available Audio Languages:", font_size=12, bold=True
        )
        avail_label.pack(anchor='w', pady=(10, 10))
        
        info_text = self.create_info_text(
            parent,
            "Select which audio languages should be available for processing. "
            "Only selected languages will be kept in the processed MKV files."
        )
        info_text.pack(anchor='w', pady=(0, 15))
        
        self._create_audio_language_selection(parent)
    
    def _create_audio_language_selection(self, parent):
        """Create the audio languages selection area."""
        audio_frame = ttk.LabelFrame(
            parent, text="Audio Languages", 
            padding=10, style='Modern.TLabelframe'
        )
        audio_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self._create_language_checkboxes(audio_frame, self.audio_lang_vars)
    
    def _create_language_checkboxes(self, parent, vars_dict):
        """
        Create checkboxes for audio language selection.
        
        Args:
            parent: Parent widget
            vars_dict: Dictionary of language code -> BooleanVar
        """
        container_frame = ttk.Frame(parent, style='Modern.TFrame')
        container_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        sorted_langs = sorted(LANG_TITLES.items(), key=lambda x: x[1])
        
        row = 0
        col = 0
        for lang_code, lang_name in sorted_langs:
            if lang_code in vars_dict:
                checkbox = ttk.Checkbutton(
                    container_frame,
                    text=f"{lang_name} ({lang_code})",
                    variable=vars_dict[lang_code],
                    command=self._update_language_combos,
                    style='Modern.TCheckbutton'
                )
                checkbox.grid(row=row, column=col, sticky='w', pady=2, padx=5)
                
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
    
    def _create_default_languages_section(self, parent):
        """Create the default audio languages selection section."""
        defaults_label = self.create_label(
            parent, "Default Audio Languages:", font_size=12, bold=True
        )
        defaults_label.pack(anchor='w', pady=(20, 10))
        
        info_text = self.create_info_text(
            parent,
            "Choose the default and original audio languages for processing. "
            "These will be used when no specific language is detected or specified."
        )
        info_text.pack(anchor='w', pady=(0, 15))
        
        defaults_frame = ttk.Frame(parent, style='Modern.TFrame')
        defaults_frame.pack(fill='x', pady=(0, 20))
        
        self._create_default_language_controls(defaults_frame)
    
    def _create_default_language_controls(self, parent):
        """Create the default audio language combo boxes."""
        ttk.Label(
            parent, text="Default Audio Language:", style='Modern.TLabel'
        ).grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        
        self.default_audio_combo = ttk.Combobox(
            parent, textvariable=self.combo_vars['default_audio'],
            state='readonly', width=20, style='Modern.TCombobox'
        )
        self.default_audio_combo.grid(row=0, column=1, sticky='w', pady=5)
        
        ttk.Label(
            parent, text="Original Audio Language:", style='Modern.TLabel'
        ).grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        
        self.original_audio_combo = ttk.Combobox(
            parent, textvariable=self.combo_vars['original_audio'],
            state='readonly', width=20, style='Modern.TCombobox'
        )
        self.original_audio_combo.grid(row=1, column=1, sticky='w', pady=5)
        
        self._update_language_combos()
    
    def _update_language_combos(self):
        """Update combo boxes with currently selected languages."""
        selected_audio = [
            code for code, var in self.audio_lang_vars.items() 
            if var.get()
        ]
        self.default_audio_combo['values'] = selected_audio
        self.original_audio_combo['values'] = selected_audio
        
        self._validate_combo_selections(selected_audio)
    
    def _validate_combo_selections(self, selected_audio):
        """
        Validate and update combo box selections.
        
        Args:
            selected_audio: List of selected audio language codes
        """
        if (self.combo_vars['default_audio'].get() not in selected_audio 
            and selected_audio):
            self.combo_vars['default_audio'].set(selected_audio[0])
            
        if (self.combo_vars['original_audio'].get() not in selected_audio 
            and selected_audio):
            self.combo_vars['original_audio'].set(selected_audio[0])
    
    def validate_settings(self):
        """
        Validate current audio language settings.
        
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        selected_audio = [
            code for code, var in self.audio_lang_vars.items() if var.get()
        ]
        if not selected_audio:
            return False, "At least one audio language must be selected."
        
        return True, None
    
    def get_settings_data(self):
        """
        Get current audio language settings.
        
        Returns:
            dict: Dictionary containing audio language settings
        """
        selected_audio = [
            code for code, var in self.audio_lang_vars.items() if var.get()
        ]
        
        return {
            'language_settings': {
                'allowed_audio_langs': selected_audio,
                'default_audio_lang': self.combo_vars['default_audio'].get(),
                'original_audio_lang': self.combo_vars['original_audio'].get()
            }
        }
