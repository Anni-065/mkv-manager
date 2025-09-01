#!/usr/bin/env python3
"""
Languages Tab Component

Handles the language configuration tab including available and default languages.
"""

import tkinter as tk
from tkinter import ttk

from .base_tab import BaseTabComponent
from .scrollable_tab import ScrollableTabMixin

# Import language constants
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
sys.path.insert(0, root_dir)

from core.config.constants import LANG_TITLES


class LanguagesTabComponent(BaseTabComponent, ScrollableTabMixin):
    """
    Tab component for configuring language settings.
    
    Allows users to set:
    - Available audio languages
    - Available subtitle languages
    - Default audio language
    - Default subtitle language
    - Original audio language
    - Original subtitle language
    """
    
    def __init__(self, parent, colors, settings, user_config):
        """Initialize the languages tab component."""
        super().__init__(parent, colors, settings, user_config)
        
        # Variables for language checkboxes
        self.audio_lang_vars = {}
        self.sub_lang_vars = {}
        
        # Variables for combo boxes
        self.combo_vars = {}
    
    def get_tab_name(self):
        """Return the display name for this tab."""
        return "Languages"
    
    def create_content(self):
        """Create the language configuration interface."""
        # Create scrollable content
        canvas, scrollable_frame = self.create_scrollable_frame(self.frame)
        
        self.setup_variables()
        self._create_available_languages_section(scrollable_frame)
        self._create_default_languages_section(scrollable_frame)
    
    def setup_variables(self):
        """Setup tkinter variables for form controls."""
        lang_settings = self.settings.get('language_settings', {})
        
        # Setup checkbox variables for available languages
        allowed_audio = lang_settings.get('allowed_audio_langs', [])
        allowed_sub = lang_settings.get('allowed_sub_langs', [])
        
        # Create checkbox variables for all available languages
        for lang_code in LANG_TITLES.keys():
            self.audio_lang_vars[lang_code] = tk.BooleanVar(
                value=lang_code in allowed_audio
            )
            self.sub_lang_vars[lang_code] = tk.BooleanVar(
                value=lang_code in allowed_sub
            )
        
        # Setup combo box variables for defaults
        self.combo_vars = {
            'default_audio': tk.StringVar(
                value=lang_settings.get('default_audio_lang', '')
            ),
            'default_subtitle': tk.StringVar(
                value=lang_settings.get('default_subtitle_lang', '')
            ),
            'original_audio': tk.StringVar(
                value=lang_settings.get('original_audio_lang', '')
            ),
            'original_subtitle': tk.StringVar(
                value=lang_settings.get('original_subtitle_lang', '')
            )
        }
    
    def _create_available_languages_section(self, parent):
        """Create the available languages selection section."""
        # Section title
        avail_label = self.create_label(
            parent, "Available Languages:", font_size=12, bold=True
        )
        avail_label.pack(anchor='w', pady=(10, 10))
        
        # Two-column layout for audio and subtitle languages
        langs_container = ttk.Frame(parent, style='Modern.TFrame')
        langs_container.pack(fill='x', pady=(0, 20))
        
        # Audio languages column
        self._create_audio_language_column(langs_container)
        
        # Subtitle languages column  
        self._create_subtitle_language_column(langs_container)
    
    def _create_audio_language_column(self, parent):
        """Create the audio languages selection column."""
        audio_column = ttk.LabelFrame(
            parent, text="Audio Languages", 
            padding=10, style='Modern.TLabelframe'
        )
        audio_column.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self._create_language_checkboxes(
            audio_column, self.audio_lang_vars, 'audio'
        )
    
    def _create_subtitle_language_column(self, parent):
        """Create the subtitle languages selection column."""
        sub_column = ttk.LabelFrame(
            parent, text="Subtitle Languages",
            padding=10, style='Modern.TLabelframe'
        )
        sub_column.pack(side='right', fill='both', expand=True)
        
        self._create_language_checkboxes(
            sub_column, self.sub_lang_vars, 'subtitle'
        )
    
    def _create_language_checkboxes(self, parent, vars_dict, lang_type):
        """
        Create checkboxes for language selection.
        
        Args:
            parent: Parent widget
            vars_dict: Dictionary of language code -> BooleanVar
            lang_type: Type of language ('audio' or 'subtitle')
        """
        # Simple container frame - no nested scrolling
        container_frame = ttk.Frame(parent, style='Modern.TFrame')
        container_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Sort languages by their display names
        sorted_langs = sorted(LANG_TITLES.items(), key=lambda x: x[1])
        
        for lang_code, lang_name in sorted_langs:
            if lang_code in vars_dict:
                checkbox = ttk.Checkbutton(
                    container_frame,
                    text=f"{lang_name} ({lang_code})",
                    variable=vars_dict[lang_code],
                    command=self._on_language_change,
                    style='Modern.TCheckbutton'
                )
                checkbox.pack(anchor='w', pady=2)
    
    def _create_default_languages_section(self, parent):
        """Create the default languages selection section."""
        # Section title
        defaults_label = self.create_label(
            parent, "Default Languages:", font_size=12, bold=True
        )
        defaults_label.pack(anchor='w', pady=(20, 10))
        
        # Grid layout for default language settings
        defaults_frame = ttk.Frame(parent, style='Modern.TFrame')
        defaults_frame.pack(fill='x', pady=(0, 20))
        
        self._create_default_language_controls(defaults_frame)
    
    def _create_default_language_controls(self, parent):
        """Create the default language combo boxes."""
        # Default audio language
        ttk.Label(
            parent, text="Default Audio Language:", style='Modern.TLabel'
        ).grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        
        self.default_audio_combo = ttk.Combobox(
            parent, textvariable=self.combo_vars['default_audio'],
            state='readonly', width=15, style='Modern.TCombobox'
        )
        self.default_audio_combo.grid(row=0, column=1, sticky='w', pady=5)
        
        # Default subtitle language
        ttk.Label(
            parent, text="Default Subtitle Language:", style='Modern.TLabel'
        ).grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        
        self.default_sub_combo = ttk.Combobox(
            parent, textvariable=self.combo_vars['default_subtitle'],
            state='readonly', width=15, style='Modern.TCombobox'
        )
        self.default_sub_combo.grid(row=1, column=1, sticky='w', pady=5)
        
        # Original audio language
        ttk.Label(
            parent, text="Original Audio Language:", style='Modern.TLabel'
        ).grid(row=0, column=2, sticky='w', padx=(20, 10), pady=5)
        
        self.original_audio_combo = ttk.Combobox(
            parent, textvariable=self.combo_vars['original_audio'],
            state='readonly', width=15, style='Modern.TCombobox'
        )
        self.original_audio_combo.grid(row=0, column=3, sticky='w', pady=5)
        
        # Original subtitle language
        ttk.Label(
            parent, text="Original Subtitle Language:", style='Modern.TLabel'
        ).grid(row=1, column=2, sticky='w', padx=(20, 10), pady=5)
        
        self.original_sub_combo = ttk.Combobox(
            parent, textvariable=self.combo_vars['original_subtitle'],
            state='readonly', width=15, style='Modern.TCombobox'
        )
        self.original_sub_combo.grid(row=1, column=3, sticky='w', pady=5)
        
        # Update combo boxes initially
        self._update_language_combos()
    
    def _on_language_change(self):
        """Called when language selection changes - update combo boxes."""
        self._update_language_combos()
    
    def _update_language_combos(self):
        """Update the combo boxes with currently selected languages."""
        # Get selected audio languages
        selected_audio = [
            code for code, var in self.audio_lang_vars.items() 
            if var.get()
        ]
        self.default_audio_combo['values'] = selected_audio
        self.original_audio_combo['values'] = selected_audio
        
        # Get selected subtitle languages
        selected_sub = [
            code for code, var in self.sub_lang_vars.items() 
            if var.get()
        ]
        self.default_sub_combo['values'] = selected_sub
        self.original_sub_combo['values'] = selected_sub
        
        # Validate current selections
        self._validate_combo_selections(selected_audio, selected_sub)
    
    def _validate_combo_selections(self, selected_audio, selected_sub):
        """
        Validate and update combo box selections.
        
        Args:
            selected_audio: List of selected audio language codes
            selected_sub: List of selected subtitle language codes
        """
        # Validate audio language selections
        if (self.combo_vars['default_audio'].get() not in selected_audio 
            and selected_audio):
            self.combo_vars['default_audio'].set(selected_audio[0])
            
        if (self.combo_vars['original_audio'].get() not in selected_audio 
            and selected_audio):
            self.combo_vars['original_audio'].set(selected_audio[0])
        
        # Validate subtitle language selections
        if (self.combo_vars['default_subtitle'].get() not in selected_sub 
            and selected_sub):
            self.combo_vars['default_subtitle'].set(selected_sub[0])
            
        if (self.combo_vars['original_subtitle'].get() not in selected_sub 
            and selected_sub):
            self.combo_vars['original_subtitle'].set(selected_sub[0])
    
    def validate_settings(self):
        """
        Validate the current language settings.
        
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        # Check that at least one audio language is selected
        selected_audio = [
            code for code, var in self.audio_lang_vars.items() if var.get()
        ]
        if not selected_audio:
            return False, "At least one audio language must be selected."
        
        # Check that at least one subtitle language is selected
        selected_sub = [
            code for code, var in self.sub_lang_vars.items() if var.get()
        ]
        if not selected_sub:
            return False, "At least one subtitle language must be selected."
        
        return True, None
    
    def get_settings_data(self):
        """
        Get the current language settings.
        
        Returns:
            dict: Dictionary containing language settings
        """
        # Collect selected languages
        selected_audio = [
            code for code, var in self.audio_lang_vars.items() if var.get()
        ]
        selected_sub = [
            code for code, var in self.sub_lang_vars.items() if var.get()
        ]
        
        return {
            'language_settings': {
                'allowed_audio_langs': selected_audio,
                'allowed_sub_langs': selected_sub,
                'default_audio_lang': self.combo_vars['default_audio'].get(),
                'default_subtitle_lang': self.combo_vars['default_subtitle'].get(),
                'original_audio_lang': self.combo_vars['original_audio'].get(),
                'original_subtitle_lang': self.combo_vars['original_subtitle'].get()
            }
        }
