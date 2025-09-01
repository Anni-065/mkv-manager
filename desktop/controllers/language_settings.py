"""
Language Settings Controller for MKV Cleaner Desktop GUI
Handles language configuration and settings management
"""

from tkinter import messagebox

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

    def update_available_languages(self):
        """Update available language options in the GUI after settings change"""
        try:
            if hasattr(self.gui, '_init_language_vars'):
                main_controller = getattr(self.gui, 'controller', None)
                self.gui._init_language_vars(main_controller)
            if hasattr(self.gui, 'update_config_display'):
                self.gui.update_config_display()
                
            if hasattr(self.gui, 'language_component') and self.gui.language_component:
                self._refresh_language_component()
                
        except Exception as e:
            print(f"Warning: Could not update GUI language options: {e}")
            
    def _refresh_language_component(self):
        """Refresh the language component with updated variables"""
        try:
            language_vars = {
                'audio_lang_vars': self.gui.audio_lang_vars,
                'subtitle_lang_vars': self.gui.subtitle_lang_vars,
                'default_audio_var': self.gui.default_audio_var,
                'default_subtitle_var': self.gui.default_subtitle_var,
                'original_audio_var': self.gui.original_audio_var,
                'original_subtitle_var': self.gui.original_subtitle_var,
                'extract_subtitles': self.gui.extract_subtitles,
                'save_extracted_subtitles': self.gui.save_extracted_subtitles
            }
            
            if hasattr(self.gui.language_component, 'vars'):
                self.gui.language_component.vars = language_vars
                
            if hasattr(self.gui.language_component, 'language_settings_inner'):
                for child in self.gui.language_component.language_settings_inner.winfo_children():
                    child.destroy()
                self.gui.language_component._create_language_content()
                            
        except Exception as e:
            print(f"Warning: Could not refresh language component: {e}")