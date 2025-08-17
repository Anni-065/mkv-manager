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

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

try:
    from core.config import *
    print("✅ Using personal config.py")
except ImportError:
    try:
        from core.config_example import *
        print("⚠️ Using config_example.py - Consider creating a personal config.py")
    except ImportError:
        print("❌ No configuration file found!")
        sys.exit(1)


class MKVCleanerController:
    """Main controller class that orchestrates all business logic for the MKV Cleaner GUI"""

    def __init__(self, gui=None):
        self.gui = gui
        self.selected_files = []

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

        self.file_selection_controller = None
        self.output_folder_controller = None
        self.processing_controller = None
        self.language_settings_controller = None

        if gui is not None:
            self.set_gui(gui)

    def set_gui(self, gui):
        """Set the GUI reference and initialize sub-controllers"""
        self.gui = gui

        # Initialize sub-controllers
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
        if self.selected_files:
            self.gui.process_button.config(
                state='normal', bg=self.gui.colors['success'], fg='white', cursor='hand2')
        else:
            self.gui.process_button.config(
                state='disabled', bg=self.gui.colors['border_light'], fg=self.gui.colors['text_muted'], cursor='arrow')

    def browse_files(self):
        """Browse for individual MKV files"""
        return self.file_selection_controller.browse_files()

    def browse_folder(self):
        """Browse for a folder containing MKV files"""
        return self.file_selection_controller.browse_folder()

    def browse_custom_folder(self):
        """Browse for custom output folder"""
        return self.output_folder_controller.browse_custom_folder()

    def on_drop(self, event):
        """Handle drag and drop events"""
        return self.file_selection_controller.on_drop(event)

    def clear_selection(self):
        """Clear all selected files"""
        return self.file_selection_controller.clear_selection()

    def process_files(self):
        """Process all selected files"""
        return self.processing_controller.process_files()

    def update_language_settings(self, event=None):
        """Update language settings based on user input"""
        return self.language_settings_controller.update_language_settings(event)

    def save_language_settings(self):
        """Save language settings to configuration"""
        return self.language_settings_controller.save_language_settings()
