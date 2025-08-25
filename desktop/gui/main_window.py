#!/usr/bin/env python3
"""
Main window for MKV Cleaner Desktop Application
"""

from .components import (
    HeaderComponent, LanguageSettingsComponent, FileSelectionComponent,
    OutputOptionsComponent, ProcessSectionComponent
)
from .mixins import ScrollMixin, DragDropMixin
from styles import ModernStyleManager, ModernColorScheme
from core.config.constants import LANG_TITLES
from controllers import MKVCleanerController
import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
gui_dir = os.path.dirname(current_dir)
desktop_dir = os.path.dirname(gui_dir)
sys.path.insert(0, desktop_dir)
sys.path.insert(0, gui_dir)


try:
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

try:
    from core.config import *
    print("✅ Using personal config.py")
except ImportError:
    try:
        from core.config import *
        print("⚠️ Using config_example.py - Consider creating a personal config.py")
    except ImportError:
        print("❌ No configuration file found!")
        sys.exit(1)


class MKVCleanerGUI(ScrollMixin, DragDropMixin):
    """Main GUI class for the MKV Cleaner application"""

    def __init__(self):
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()

        self.root.title("MKV Cleaner")
        self.root.geometry("1000x800")

        self.controller = MKVCleanerController(self)

        self.color_scheme = ModernColorScheme()
        self.style_manager = ModernStyleManager(self.color_scheme)
        self.style_manager.setup_all_styles()
        self.colors = self.color_scheme.get_all_colors()
        self.root.configure(bg=self.colors['bg'])

        self._init_variables()

        self.create_interface()
        self.setup_drag_drop()
        self.controller.update_process_button_state()

    def _init_variables(self):
        """Initialize all GUI variables"""

        self.output_option = tk.StringVar(value="same_folder")
        self.custom_folder = tk.StringVar()

        self.extract_subtitles = tk.BooleanVar(
            value=globals().get('EXTRACT_SUBTITLES', False))
        self.save_extracted_subtitles = tk.BooleanVar(
            value=globals().get('SAVE_EXTRACTED_SUBTITLES', False))

        self.audio_lang_vars = {}
        self.subtitle_lang_vars = {}
        self.default_audio_var = tk.StringVar()
        self.default_subtitle_var = tk.StringVar()
        self.original_audio_var = tk.StringVar()
        self.original_subtitle_var = tk.StringVar()

        self._init_language_vars()

    def _init_language_vars(self):
        """Initialize language variables with default values for configured languages only"""

        for lang_code in ALLOWED_AUDIO_LANGS:
            if lang_code in LANG_TITLES:
                var = tk.BooleanVar()
                var.set(True)
                self.audio_lang_vars[lang_code] = var

        for lang_code in ALLOWED_SUB_LANGS:
            if lang_code in LANG_TITLES:
                var = tk.BooleanVar()
                var.set(True)
                self.subtitle_lang_vars[lang_code] = var

        self.default_audio_var.set(
            f"{DEFAULT_AUDIO_LANG} - {LANG_TITLES.get(DEFAULT_AUDIO_LANG, 'Unknown')}")
        self.default_subtitle_var.set(
            f"{DEFAULT_SUBTITLE_LANG} - {LANG_TITLES.get(DEFAULT_SUBTITLE_LANG, 'Unknown')}")
        self.original_audio_var.set(
            f"{ORIGINAL_AUDIO_LANG} - {LANG_TITLES.get(ORIGINAL_AUDIO_LANG, 'Unknown')}")
        self.original_subtitle_var.set(
            f"{ORIGINAL_SUBTITLE_LANG} - {LANG_TITLES.get(ORIGINAL_SUBTITLE_LANG, 'Unknown')}")

    def create_interface(self):
        """Create the main interface"""

        self._setup_scrollable_canvas()

        main_frame = ttk.Frame(self.scrollable_frame, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=(20, 40), pady=20)

        self._create_all_sections(main_frame)

        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        self.bind_mousewheel()

    def _setup_scrollable_canvas(self):
        """Setup the scrollable canvas and frame"""

        self.canvas = tk.Canvas(
            self.root, bg=self.colors['bg'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style='Modern.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind('<Configure>', self._on_canvas_configure)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _create_all_sections(self, parent):
        """Create all GUI sections using components"""

        header_component = HeaderComponent(parent, self.colors, DND_AVAILABLE)
        header_component.create()

        language_vars = {
            'audio_lang_vars': self.audio_lang_vars,
            'subtitle_lang_vars': self.subtitle_lang_vars,
            'default_audio_var': self.default_audio_var,
            'default_subtitle_var': self.default_subtitle_var,
            'original_audio_var': self.original_audio_var,
            'original_subtitle_var': self.original_subtitle_var,
            'extract_subtitles': self.extract_subtitles,
            'save_extracted_subtitles': self.save_extracted_subtitles
        }

        self.language_component = LanguageSettingsComponent(
            parent, self.colors, self.controller, language_vars)
        self.language_component.create()

        file_component = FileSelectionComponent(
            parent, self.colors, self.controller)
        _, self.file_tree = file_component.create()

        output_vars = {
            'output_option': self.output_option,
            'custom_folder': self.custom_folder
        }
        output_component = OutputOptionsComponent(
            parent, self.colors, self.controller, output_vars)
        output_component.create()

        process_component = ProcessSectionComponent(
            parent, self.colors, self.controller)
        _, self.progress_bar, self.progress_label, self.process_button = process_component.create()

    def toggle_language_settings(self):
        """Toggle language settings - delegate to component"""
        if hasattr(self, 'language_component'):
            self.language_component.toggle_language_settings()

    def update_language_settings_visibility(self):
        """Update language settings visibility - delegate to component"""
        if hasattr(self, 'language_component'):
            self.language_component.update_language_settings_visibility()

    def update_config_display(self):
        """Update the configuration display"""
        pass

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MKVCleanerGUI()
    app.run()
