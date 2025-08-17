"""
Language Settings Controller for MKV Cleaner Desktop GUI
Handles language configuration and settings management
"""

from tkinter import messagebox

try:
    from styles import ICONS
except ImportError:
    ICONS = {
        'success': '✅'
    }


class LanguageSettingsController:
    """Controller for language settings operations"""

    def __init__(self, gui, language_config):
        self.gui = gui
        self.language_config = language_config

    def update_language_settings(self, event=None):
        """Update language settings based on user input"""
        self.language_config['allowed_audio_langs'] = {
            lang_code for lang_code, var in self.gui.audio_lang_vars.items() if var.get()
        }
        self.language_config['allowed_sub_langs'] = {
            lang_code for lang_code, var in self.gui.subtitle_lang_vars.items() if var.get()
        }

        self.language_config['default_audio_lang'] = self.gui.default_audio_var.get(
        ).split(' - ')[0]
        self.language_config['default_subtitle_lang'] = self.gui.default_subtitle_var.get(
        ).split(' - ')[0]
        self.language_config['original_audio_lang'] = self.gui.original_audio_var.get(
        ).split(' - ')[0]
        self.language_config['original_subtitle_lang'] = self.gui.original_subtitle_var.get(
        ).split(' - ')[0]

        self.language_config['extract_subtitles'] = self.gui.extract_subtitles.get(
        )
        self.language_config['save_extracted_subtitles'] = self.gui.save_extracted_subtitles.get(
        )

        self.gui.update_config_display()

    def save_language_settings(self):
        """Save language settings to configuration"""
        try:
            self.gui.update_config_display()

            messagebox.showinfo("Settings Saved",
                                f"{ICONS['success']} Language settings have been updated successfully!")

        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to save language settings: {str(e)}")
