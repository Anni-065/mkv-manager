#!/usr/bin/env python3
"""
Subtitle Languages Tab Component

Handles the subtitle language configuration tab.
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


class SubtitleLanguagesTabComponent(BaseTabComponent, ScrollableTabMixin):
    """
    Tab component for configuring subtitle language settings.
    
    Allows users to set:
    - Available subtitle languages
    - Default subtitle language
    - Original subtitle language
    """
    
    def __init__(self, parent, colors, settings, user_config):
        """Initialize the subtitle languages tab component."""
        super().__init__(parent, colors, settings, user_config)
        
        self.sub_lang_vars = {}
        self.combo_vars = {}
    
    def get_tab_name(self):
        """Return the display name for this tab."""
        return "Subtitle Languages"
    
    def create_content(self):
        """Create subtitle language configuration interface."""
        canvas, scrollable_frame = self.create_scrollable_frame(self.frame)
        
        self.setup_variables()
        self._create_available_languages_section(scrollable_frame)
        self._create_default_languages_section(scrollable_frame)
    
    def setup_variables(self):
        """Setup tkinter variables for form controls."""
        lang_settings = self.settings.get('language_settings', {})
        allowed_sub = lang_settings.get('allowed_sub_langs', [])
        
        for lang_code in LANG_TITLES.keys():
            self.sub_lang_vars[lang_code] = tk.BooleanVar(
                value=lang_code in allowed_sub
            )
        
        self.combo_vars = {
            'default_subtitle': tk.StringVar(
                value=lang_settings.get('default_subtitle_lang', '')
            ),
            'original_subtitle': tk.StringVar(
                value=lang_settings.get('original_subtitle_lang', '')
            )
        }
    
    def _create_available_languages_section(self, parent):
        """Create the available subtitle languages selection section."""
        avail_label = self.create_label(
            parent, "Available Subtitle Languages:", font_size=12, bold=True
        )
        avail_label.pack(anchor='w', pady=(10, 10))
        
        info_text = self.create_info_text(
            parent,
            "Select which subtitle languages should be available for processing. "
            "Only selected languages will be kept in the processed MKV files."
        )
        info_text.pack(anchor='w', pady=(0, 15))
        
        self._create_subtitle_language_selection(parent)
    
    def _create_subtitle_language_selection(self, parent):
        """Create the subtitle languages selection area."""
        sub_frame = ttk.LabelFrame(
            parent, text="Subtitle Languages", 
            padding=10, style='Modern.TLabelframe'
        )
        sub_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self._create_language_checkboxes(sub_frame, self.sub_lang_vars)
    
    def _create_language_checkboxes(self, parent, vars_dict):
        """
        Create checkboxes for subtitle language selection.
        
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
        """Create the default subtitle languages selection section."""
        defaults_label = self.create_label(
            parent, "Default Subtitle Languages:", font_size=12, bold=True
        )
        defaults_label.pack(anchor='w', pady=(20, 10))
        
        info_text = self.create_info_text(
            parent,
            "Choose the default and original subtitle languages for processing. "
            "These will be used when no specific language is detected or specified."
        )
        info_text.pack(anchor='w', pady=(0, 15))
        
        defaults_frame = ttk.Frame(parent, style='Modern.TFrame')
        defaults_frame.pack(fill='x', pady=(0, 20))
        
        self._create_default_language_controls(defaults_frame)
    
    def _create_default_language_controls(self, parent):
        """Create the default subtitle language combo boxes."""
        ttk.Label(
            parent, text="Default Subtitle Language:", style='Modern.TLabel'
        ).grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        
        self.default_sub_combo = ttk.Combobox(
            parent, textvariable=self.combo_vars['default_subtitle'],
            state='readonly', width=20, style='Modern.TCombobox'
        )
        self.default_sub_combo.grid(row=0, column=1, sticky='w', pady=5)
        
        ttk.Label(
            parent, text="Original Subtitle Language:", style='Modern.TLabel'
        ).grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        
        self.original_sub_combo = ttk.Combobox(
            parent, textvariable=self.combo_vars['original_subtitle'],
            state='readonly', width=20, style='Modern.TCombobox'
        )
        self.original_sub_combo.grid(row=1, column=1, sticky='w', pady=5)
        
        self._update_language_combos()
    
    def _update_language_combos(self):
        """Update the combo boxes with currently selected languages."""
        selected_sub = [
            code for code, var in self.sub_lang_vars.items() 
            if var.get()
        ]
        self.default_sub_combo['values'] = selected_sub
        self.original_sub_combo['values'] = selected_sub
        
        self._validate_combo_selections(selected_sub)
    
    def _validate_combo_selections(self, selected_sub):
        """
        Validate and update combo box selections.
        
        Args:
            selected_sub: List of selected subtitle language codes
        """
        if (self.combo_vars['default_subtitle'].get() not in selected_sub 
            and selected_sub):
            self.combo_vars['default_subtitle'].set(selected_sub[0])
            
        if (self.combo_vars['original_subtitle'].get() not in selected_sub 
            and selected_sub):
            self.combo_vars['original_subtitle'].set(selected_sub[0])
    
    def validate_settings(self):
        """
        Validate the current subtitle language settings.
        
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        selected_sub = [
            code for code, var in self.sub_lang_vars.items() if var.get()
        ]
        if not selected_sub:
            return False, "At least one subtitle language must be selected."
        
        return True, None
    
    def get_settings_data(self):
        """
        Get the current subtitle language settings.
        
        Returns:
            dict: Dictionary containing subtitle language settings
        """
        selected_sub = [
            code for code, var in self.sub_lang_vars.items() if var.get()
        ]
        
        return {
            'language_settings': {
                'allowed_sub_langs': selected_sub,
                'default_subtitle_lang': self.combo_vars['default_subtitle'].get(),
                'original_subtitle_lang': self.combo_vars['original_subtitle'].get()
            }
        }
