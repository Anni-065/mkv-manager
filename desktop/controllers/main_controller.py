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
from typing import Optional, Set, TYPE_CHECKING


if TYPE_CHECKING:
    from ..gui.main_window import MKVCleanerGUI

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

from core.config.user_config import get_user_config_manager
# Import SettingsWindow when needed to avoid circular import
# from gui.settings.settings_window import SettingsWindow

ALLOWED_AUDIO_LANGS: Set[str] = set()
ALLOWED_SUB_LANGS: Set[str] = set()
DEFAULT_AUDIO_LANG: str = "eng"
DEFAULT_SUBTITLE_LANG: str = "eng"
ORIGINAL_AUDIO_LANG: str = "eng"
ORIGINAL_SUBTITLE_LANG: str = "eng"

def load_configuration():
    """Load configuration with user settings taking priority"""
    global ALLOWED_AUDIO_LANGS, ALLOWED_SUB_LANGS, DEFAULT_AUDIO_LANG, DEFAULT_SUBTITLE_LANG, ORIGINAL_AUDIO_LANG, ORIGINAL_SUBTITLE_LANG
    
    try:
        user_config = get_user_config_manager()
        lang_settings = user_config.get_language_settings()
        
        ALLOWED_AUDIO_LANGS = set(lang_settings.get('allowed_audio_langs', ['eng', 'ger', 'jpn', 'kor']))
        ALLOWED_SUB_LANGS = set(lang_settings.get('allowed_sub_langs', ['eng', 'ger', 'kor', 'gre']))
        DEFAULT_AUDIO_LANG = lang_settings.get('default_audio_lang', 'eng')
        DEFAULT_SUBTITLE_LANG = lang_settings.get('default_subtitle_lang', 'eng')
        ORIGINAL_AUDIO_LANG = lang_settings.get('original_audio_lang', 'eng')
        ORIGINAL_SUBTITLE_LANG = lang_settings.get('original_subtitle_lang', 'eng')
        
        print(f"✅ Using user configuration from: {user_config.get_config_file_path()}")
        return True
    except Exception as e:
        print(f"⚠️ Could not load user config, trying fallback: {e}")
        
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
            print("✅ Using static config files")
            return True
        except ImportError:
            print("❌ No configuration files found! Using hardcoded defaults.")
            ALLOWED_AUDIO_LANGS = {"eng", "ger", "jpn", "kor"}
            ALLOWED_SUB_LANGS = {"eng", "ger", "kor", "gre"}
            return False

load_configuration()


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
        """Open the comprehensive settings window"""
        if not self.gui:
            return


        def on_settings_updated():
            """Callback when settings are updated"""
            # Reload configuration
            load_configuration()
            
            # Update internal language config
            self.language_config['allowed_audio_langs'] = set(ALLOWED_AUDIO_LANGS)
            self.language_config['allowed_sub_langs'] = set(ALLOWED_SUB_LANGS)
            self.language_config['default_audio_lang'] = DEFAULT_AUDIO_LANG
            self.language_config['default_subtitle_lang'] = DEFAULT_SUBTITLE_LANG
            self.language_config['original_audio_lang'] = ORIGINAL_AUDIO_LANG
            self.language_config['original_subtitle_lang'] = ORIGINAL_SUBTITLE_LANG
            
            # Refresh the main GUI with updated settings
            self._refresh_gui_after_settings_update()
            
            print("✅ Settings updated successfully")

        # Import here to avoid circular import
        from gui.settings.settings_window import SettingsWindow
        SettingsWindow(
            parent=self.gui.root,
            colors=self.gui.colors,
            callback=on_settings_updated
        )

    def _refresh_gui_after_settings_update(self):
        """Refresh the main GUI after settings have been updated"""
        if not self.gui:
            return
            
        try:
            # Update language variables with new controller settings
            self.gui._init_language_vars(self)
            
            # Update the language settings controller with new language config
            if self.language_settings_controller:
                self.language_settings_controller.language_config = self.language_config
                self.language_settings_controller.update_available_languages()
            
            # Update config display
            self.gui.update_config_display()
            
            print("🔄 GUI: Main interface refreshed after settings update")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not fully refresh GUI after settings update: {e}")
            # Fallback to basic update
            if hasattr(self.gui, 'update_config_display'):
                self.gui.update_config_display()
