#!/usr/bin/env python3
"""
Language settings component for MKV Cleaner Desktop Application
"""

from styles import UIHelpers
import tkinter as tk
from tkinter import ttk
import os
import sys

from core.config import ALLOWED_AUDIO_LANGS, ALLOWED_SUB_LANGS
from core.config.constants import LANG_TITLES

current_dir = os.path.dirname(os.path.abspath(__file__))
components_dir = os.path.dirname(current_dir)
gui_dir = os.path.dirname(components_dir)
desktop_dir = os.path.dirname(gui_dir)
sys.path.insert(0, desktop_dir)
sys.path.insert(0, gui_dir)


class LanguageSettingsComponent:
    """Component for creating the language settings section"""

    def __init__(self, parent, colors, controller, vars_dict):
        self.parent = parent
        self.colors = colors
        self.controller = controller
        self.vars = vars_dict

        self.language_settings_expanded = tk.BooleanVar(value=False)

    def create(self):
        """Create the language settings section"""
        lang_container = ttk.Frame(self.parent, style='Modern.TFrame')
        lang_container.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        lang_container.grid_columnconfigure(0, weight=1)

        self.language_settings_header = ttk.LabelFrame(lang_container, text="  🌐 Language Settings     ▶   ",
                                                       style='Modern.TLabelframe')
        self.language_settings_header.grid(row=0, column=0, sticky='ew')
        self.language_settings_header.grid_columnconfigure(0, weight=1)

        header_padding = ttk.Frame(
            self.language_settings_header, style='Modern.TFrame')
        header_padding.grid(row=0, column=0, sticky='ew', padx=5, pady=20)

        self.language_settings_header.bind(
            "<Button-1>", lambda e: self.toggle_language_settings())

        self.language_settings_content = ttk.LabelFrame(lang_container, text="",
                                                        style='Modern.TLabelframe')
        self.language_settings_content.grid(row=0, column=0, sticky='ew')
        self.language_settings_content.grid_columnconfigure(0, weight=1)
        self.language_settings_content.grid_columnconfigure(1, weight=1)

        self.language_settings_content.bind(
            "<Button-1>", lambda e: self.toggle_language_settings())

        self._create_language_content()
        self.update_language_settings_visibility()

        return lang_container

    def _create_language_content(self):
        """Create the language settings content"""

        self.language_settings_inner = ttk.Frame(
            self.language_settings_content, style='Modern.TFrame')
        self.language_settings_inner.grid(
            row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        self.language_settings_inner.grid_columnconfigure(0, weight=1)
        self.language_settings_inner.grid_columnconfigure(1, weight=1)

        audio_frame = self._create_audio_section()

        subtitle_frame = self._create_subtitle_section()

        save_btn = UIHelpers.create_button(
            self.language_settings_inner, text="💾 Save Settings", command=self.controller.save_language_settings,
            button_type="success", colors=self.colors, width=120, height=35
        )
        save_btn.grid(row=1, column=0, columnspan=2, pady=(10, 15))

    def _create_audio_section(self):
        """Create the audio language section"""

        audio_frame = ttk.Frame(
            self.language_settings_inner, style='Modern.TFrame')
        audio_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        audio_label = ttk.Label(audio_frame, text="🎵 Audio Languages",
                                style='SectionHeader.TLabel')
        audio_label.grid(row=0, column=0, sticky='w', pady=(0, 10))

        audio_check_frame = ttk.Frame(audio_frame, style='Modern.TFrame')
        audio_check_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))

        row = 0
        col = 0

        for lang_code in ALLOWED_AUDIO_LANGS:
            if lang_code in self.vars['audio_lang_vars'] and lang_code in LANG_TITLES:
                lang_name = LANG_TITLES[lang_code]
                checkbox = ttk.Checkbutton(
                    audio_check_frame,
                    text=f"{lang_code} - {lang_name}",
                    variable=self.vars['audio_lang_vars'][lang_code],
                    command=self.controller.update_language_settings,
                    style='Modern.TCheckbutton'
                )
                checkbox.grid(row=row, column=col, sticky='w',
                              padx=(0, 20), pady=2)
                col += 1
                if col > 2:
                    col = 0
                    row += 1

        self._create_audio_combos(audio_frame)

        return audio_frame

    def _create_audio_combos(self, audio_frame):
        """Create audio comboboxes"""

        default_audio_label = ttk.Label(audio_frame, text="Default Audio:",
                                        style='Modern.TLabel')
        default_audio_label.grid(row=2, column=0, sticky='w', pady=(10, 5))

        default_audio_combo = ttk.Combobox(
            audio_frame, textvariable=self.vars['default_audio_var'],
            values=[
                f"{code} - {LANG_TITLES[code]}" for code in ALLOWED_AUDIO_LANGS if code in LANG_TITLES],
            state='readonly', style='Modern.TCombobox'
        )
        default_audio_combo.grid(row=3, column=0, sticky='ew', pady=(0, 10))
        default_audio_combo.bind(
            '<<ComboboxSelected>>', self.controller.update_language_settings)

        original_audio_label = ttk.Label(audio_frame, text="Original Audio:",
                                         style='Modern.TLabel')
        original_audio_label.grid(row=4, column=0, sticky='w', pady=(0, 5))

        original_audio_combo = ttk.Combobox(
            audio_frame, textvariable=self.vars['original_audio_var'],
            values=[
                f"{code} - {LANG_TITLES[code]}" for code in ALLOWED_AUDIO_LANGS if code in LANG_TITLES],
            state='readonly', style='Modern.TCombobox'
        )
        original_audio_combo.grid(row=5, column=0, sticky='ew')
        original_audio_combo.bind(
            '<<ComboboxSelected>>', self.controller.update_language_settings)

    def _create_subtitle_section(self):
        """Create the subtitle language section"""

        subtitle_frame = ttk.Frame(
            self.language_settings_inner, style='Modern.TFrame')
        subtitle_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)

        subtitle_label = ttk.Label(subtitle_frame, text="📝 Subtitle Languages",
                                   style='SectionHeader.TLabel')
        subtitle_label.grid(row=0, column=0, sticky='w', pady=(0, 10))

        subtitle_check_frame = ttk.Frame(subtitle_frame, style='Modern.TFrame')
        subtitle_check_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))

        row = 0
        col = 0

        for lang_code in ALLOWED_SUB_LANGS:
            if lang_code in self.vars['subtitle_lang_vars'] and lang_code in LANG_TITLES:
                lang_name = LANG_TITLES[lang_code]
                checkbox = ttk.Checkbutton(
                    subtitle_check_frame,
                    text=f"{lang_code} - {lang_name}",
                    variable=self.vars['subtitle_lang_vars'][lang_code],
                    command=self.controller.update_language_settings,
                    style='Modern.TCheckbutton'
                )
                checkbox.grid(row=row, column=col, sticky='w',
                              padx=(0, 20), pady=2)
                col += 1
                if col > 2:
                    col = 0
                    row += 1

        self._create_subtitle_combos(subtitle_frame)
        self._create_subtitle_processing(subtitle_frame)

        return subtitle_frame

    def _create_subtitle_combos(self, subtitle_frame):
        """Create subtitle comboboxes"""

        default_subtitle_label = ttk.Label(subtitle_frame, text="Default Subtitle:",
                                           style='Modern.TLabel')
        default_subtitle_label.grid(row=2, column=0, sticky='w', pady=(10, 5))

        default_subtitle_combo = ttk.Combobox(
            subtitle_frame, textvariable=self.vars['default_subtitle_var'],
            values=[
                f"{code} - {LANG_TITLES[code]}" for code in ALLOWED_SUB_LANGS if code in LANG_TITLES],
            state='readonly', style='Modern.TCombobox'
        )
        default_subtitle_combo.grid(row=3, column=0, sticky='ew', pady=(0, 10))
        default_subtitle_combo.bind(
            '<<ComboboxSelected>>', self.controller.update_language_settings)

        original_subtitle_label = ttk.Label(subtitle_frame, text="Original Subtitle:",
                                            style='Modern.TLabel')
        original_subtitle_label.grid(row=4, column=0, sticky='w', pady=(0, 5))

        all_configured_langs = list(
            ALLOWED_AUDIO_LANGS.union(ALLOWED_SUB_LANGS))
        original_subtitle_combo = ttk.Combobox(
            subtitle_frame, textvariable=self.vars['original_subtitle_var'],
            values=[
                f"{code} - {LANG_TITLES[code]}" for code in all_configured_langs if code in LANG_TITLES],
            state='readonly', style='Modern.TCombobox'
        )
        original_subtitle_combo.grid(row=5, column=0, sticky='ew')
        original_subtitle_combo.bind(
            '<<ComboboxSelected>>', self.controller.update_language_settings)

    def _create_subtitle_processing(self, subtitle_frame):
        """Create subtitle processing options"""
        subtitle_processing_label = ttk.Label(subtitle_frame, text="🔄 Subtitle Processing:",
                                              style='SectionHeader.TLabel')
        subtitle_processing_label.grid(
            row=6, column=0, sticky='w', pady=(15, 5))

        extract_subtitles_check = ttk.Checkbutton(
            subtitle_frame,
            text="Convert subtitles to SRT format",
            variable=self.vars['extract_subtitles'],
            command=self.controller.update_language_settings,
            style='Modern.TCheckbutton'
        )
        extract_subtitles_check.grid(row=7, column=0, sticky='w', pady=(0, 5))

        save_extracted_check = ttk.Checkbutton(
            subtitle_frame,
            text="Save extracted SRT files next to processed MKV",
            variable=self.vars['save_extracted_subtitles'],
            command=self.controller.update_language_settings,
            style='Modern.TCheckbutton'
        )
        save_extracted_check.grid(row=8, column=0, sticky='w', pady=(0, 10))

    def toggle_language_settings(self):
        """Toggle the language settings visibility"""

        current_state = self.language_settings_expanded.get()
        self.language_settings_expanded.set(not current_state)
        self.update_language_settings_visibility()

    def update_language_settings_visibility(self):
        """Update the language settings visibility"""

        if hasattr(self, 'language_settings_content'):
            if self.language_settings_expanded.get():
                self.language_settings_header.grid_remove()
                self.language_settings_content.config(
                    text="  🌐 Language Settings     ▼   ")
                self.language_settings_content.grid()
            else:
                self.language_settings_content.grid_remove()
                self.language_settings_header.config(
                    text="  🌐 Language Settings     ▶   ")
                self.language_settings_header.grid()
