"""
Main Controller for MKV Cleaner Desktop GUI
Orchestrates all other controllers and handles the main business logic
"""

from .language_settings import LanguageSettingsController
from .processing import ProcessingController
from .output_folder import OutputFolderController
from .file_selection import FileSelectionController
import os
import sys
from tkinter import ttk, messagebox
from typing import Optional, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from ..gui.main_window import MKVCleanerGUI

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

ALLOWED_AUDIO_LANGS: Set[str] = set()
ALLOWED_SUB_LANGS: Set[str] = set()
DEFAULT_AUDIO_LANG: str = "eng"
DEFAULT_SUBTITLE_LANG: str = "eng"
ORIGINAL_AUDIO_LANG: str = "eng"
ORIGINAL_SUBTITLE_LANG: str = "eng"

try:
    from core.config import (
        ALLOWED_AUDIO_LANGS as _ALLOWED_AUDIO_LANGS,
        ALLOWED_SUB_LANGS as _ALLOWED_SUB_LANGS,
        DEFAULT_AUDIO_LANG as _DEFAULT_AUDIO_LANG,
        DEFAULT_SUBTITLE_LANG as _DEFAULT_SUBTITLE_LANG,
        ORIGINAL_AUDIO_LANG as _ORIGINAL_AUDIO_LANG,
        ORIGINAL_SUBTITLE_LANG as _ORIGINAL_SUBTITLE_LANG
    )
    ALLOWED_AUDIO_LANGS = _ALLOWED_AUDIO_LANGS
    ALLOWED_SUB_LANGS = _ALLOWED_SUB_LANGS
    DEFAULT_AUDIO_LANG = _DEFAULT_AUDIO_LANG
    DEFAULT_SUBTITLE_LANG = _DEFAULT_SUBTITLE_LANG
    ORIGINAL_AUDIO_LANG = _ORIGINAL_AUDIO_LANG
    ORIGINAL_SUBTITLE_LANG = _ORIGINAL_SUBTITLE_LANG
    print("✅ Using personal config.py")
except ImportError:
    try:
        from core.config.config_example import (
            ALLOWED_AUDIO_LANGS as _ALLOWED_AUDIO_LANGS,
            ALLOWED_SUB_LANGS as _ALLOWED_SUB_LANGS,
            DEFAULT_AUDIO_LANG as _DEFAULT_AUDIO_LANG,
            DEFAULT_SUBTITLE_LANG as _DEFAULT_SUBTITLE_LANG,
            ORIGINAL_AUDIO_LANG as _ORIGINAL_AUDIO_LANG,
            ORIGINAL_SUBTITLE_LANG as _ORIGINAL_SUBTITLE_LANG
        )
        ALLOWED_AUDIO_LANGS = _ALLOWED_AUDIO_LANGS
        ALLOWED_SUB_LANGS = _ALLOWED_SUB_LANGS
        DEFAULT_AUDIO_LANG = _DEFAULT_AUDIO_LANG
        DEFAULT_SUBTITLE_LANG = _DEFAULT_SUBTITLE_LANG
        ORIGINAL_AUDIO_LANG = _ORIGINAL_AUDIO_LANG
        ORIGINAL_SUBTITLE_LANG = _ORIGINAL_SUBTITLE_LANG
        print("⚠️ Using config_example.py - Consider creating a personal config.py")
    except ImportError:
        print("❌ No configuration file found! Using defaults.")
        ALLOWED_AUDIO_LANGS = {"eng", "ger", "jpn", "kor"}
        ALLOWED_SUB_LANGS = {"eng", "ger", "kor", "gre"}


class MKVCleanerController:
    """Main controller class that orchestrates all business logic for the MKV Cleaner GUI"""

    def __init__(self, gui: Optional['MKVCleanerGUI'] = None):
        self.gui = gui
        self.selected_files: list = []

        self.language_config = {
            'allowed_audio_langs': set(ALLOWED_AUDIO_LANGS),
            'allowed_sub_langs': set(ALLOWED_SUB_LANGS),
            'default_audio_lang': DEFAULT_AUDIO_LANG,
            'default_subtitle_lang': DEFAULT_SUBTITLE_LANG,
            'original_audio_lang': ORIGINAL_AUDIO_LANG,
            'original_subtitle_lang': ORIGINAL_SUBTITLE_LANG,
            'extract_subtitles': globals().get('EXTRACT_SUBTITLES', False),
            'save_extracted_subtitles': globals().get('SAVE_EXTRACTED_SUBTITLES', False)
        }

        self.file_selection_controller: Optional[FileSelectionController] = None
        self.output_folder_controller: Optional[OutputFolderController] = None
        self.processing_controller: Optional[ProcessingController] = None
        self.language_settings_controller: Optional[LanguageSettingsController] = None

        if gui is not None:
            self.set_gui(gui)

    def set_gui(self, gui: 'MKVCleanerGUI'):
        """Set the GUI reference and initialize sub-controllers"""
        self.gui = gui

        self.file_selection_controller = FileSelectionController(
            gui, self.selected_files, self.update_process_button_state
        )
        self.output_folder_controller = OutputFolderController(gui)
        self.processing_controller = ProcessingController(
            gui, self.selected_files, self.language_config,
            self.output_folder_controller, self.file_selection_controller
        )
        self.language_settings_controller = LanguageSettingsController(
            gui, self.language_config
        )

    def update_process_button_state(self):
        """Update the process button state based on selected files"""
        if self.gui and hasattr(self.gui, 'process_button') and self.gui.process_button:
            if self.selected_files:
                if hasattr(self.gui.process_button, 'config'):
                    self.gui.process_button.config(  # type: ignore
                        state='normal',
                        bg=self.gui.colors['success'],
                        fg='white',
                        cursor='hand2'
                    )
            else:
                if hasattr(self.gui.process_button, 'config'):
                    self.gui.process_button.config(  # type: ignore
                        state='disabled',
                        bg=self.gui.colors['border_light'],
                        fg=self.gui.colors['text_muted'],
                        cursor='arrow'
                    )

    def browse_files(self):
        """Browse for individual MKV files"""
        if self.file_selection_controller:
            return self.file_selection_controller.browse_files()
        return None

    def browse_folder(self):
        """Browse for a folder containing MKV files"""
        if self.file_selection_controller:
            return self.file_selection_controller.browse_folder()
        return None

    def browse_custom_folder(self):
        """Browse for custom output folder"""
        if self.output_folder_controller:
            return self.output_folder_controller.browse_custom_folder()
        return None

    def on_drop(self, event):
        """Handle drag and drop events"""
        if self.file_selection_controller:
            return self.file_selection_controller.on_drop(event)
        return None

    def clear_selection(self):
        """Clear all selected files"""
        if self.file_selection_controller:
            return self.file_selection_controller.clear_selection()
        return None

    def process_files(self):
        """Process all selected files"""
        if self.processing_controller:
            return self.processing_controller.process_files()
        return None

    def update_language_settings(self, event=None):
        """Update language settings based on user input"""
        if self.language_settings_controller:
            return self.language_settings_controller.update_language_settings(event)
        return None

    def save_language_settings(self):
        """Save language settings to configuration"""
        if self.language_settings_controller:
            return self.language_settings_controller.save_language_settings()
        return None

    def open_language_manager(self):
        """Open the language manager window"""
        if not self.gui:
            return

        from gui.components.language_manager import LanguageManagerWindow
        from core.config.config_manager import ConfigManager

        def on_languages_updated(new_audio_langs, new_sub_langs):
            """Callback when languages are updated in the manager"""
            config_manager = ConfigManager()
            success = config_manager.update_language_settings(
                new_audio_langs, new_sub_langs)

            if success:
                print("✅ Configuration file updated successfully")

                config_manager.validate_default_languages(
                    new_audio_langs, new_sub_langs)

                self.language_config['allowed_audio_langs'] = new_audio_langs
                self.language_config['allowed_sub_langs'] = new_sub_langs

                print(
                    f"✅ Controller config updated: Audio={len(new_audio_langs)}, Sub={len(new_sub_langs)}")

                if self.gui and hasattr(self.gui, 'create_interface') and hasattr(self.gui, 'scrollable_frame'):
                    for widget in self.gui.scrollable_frame.winfo_children():
                        widget.destroy()

                    if hasattr(self.gui, '_init_language_vars'):
                        self.gui._init_language_vars(self)
                    main_frame = ttk.Frame(
                        self.gui.scrollable_frame, style='Modern.TFrame')
                    main_frame.pack(fill='both', expand=True,
                                    padx=(20, 40), pady=20)

                    if hasattr(self.gui, '_create_all_sections'):
                        self.gui._create_all_sections(main_frame)

                    main_frame.grid_rowconfigure(2, weight=1)
                    main_frame.grid_columnconfigure(0, weight=1)

                    if hasattr(self.gui, 'canvas') and hasattr(self.gui, 'scrollable_frame'):
                        self.gui.canvas.update_idletasks()
                        self.gui.canvas.configure(
                            scrollregion=self.gui.canvas.bbox("all"))

                    print("🔄 Refreshing GUI interface...")
                    parent_window = self.gui.root if (
                        self.gui and hasattr(self.gui, 'root')) else None
                    messagebox.showinfo(
                        "Settings Updated",
                        f"Language settings have been updated successfully!\n\nAudio Languages: {len(new_audio_langs)} selected\nSubtitle Languages: {len(new_sub_langs)} selected\n\nChanges are now visible in the main window.",
                        parent=parent_window  # type: ignore
                    )
            else:
                print("❌ Configuration file update failed")
                parent_window = self.gui.root if (
                    self.gui and hasattr(self.gui, 'root')) else None
                messagebox.showerror(
                    "Update Failed",
                    "Failed to update language settings. Please check file permissions.",
                    parent=parent_window  # type: ignore
                )

        if hasattr(self.gui, 'root') and hasattr(self.gui, 'colors'):
            LanguageManagerWindow(
                self.gui.root,
                self.gui.colors,
                self.language_config['allowed_audio_langs'],
                self.language_config['allowed_sub_langs'],
                on_languages_updated
            )
