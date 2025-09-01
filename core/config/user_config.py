#!/usr/bin/env python3
"""
User Configuration Manager for MKV Cleaner Desktop Application
Handles user-specific settings in a JSON format stored in the user's home directory
"""

import os
import json
import sys

from pathlib import Path

DEFAULT_ALLOWED_AUDIO_LANGS = {"eng"}
DEFAULT_ALLOWED_SUB_LANGS = {"eng"}
DEFAULT_AUDIO_LANG = "eng"
DEFAULT_SUBTITLE_LANG = "eng"
DEFAULT_ORIGINAL_AUDIO_LANG = "eng"
DEFAULT_ORIGINAL_SUBTITLE_LANG = "eng"

def find_mkvmerge():
    """Intelligently locate mkvmerge executable across different OS"""
    import subprocess
    import shutil
    
    try:
        if sys.platform == "win32":
            result = subprocess.run(['where', 'mkvmerge'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                path = result.stdout.strip().split('\n')[0]  # Take first result
                if os.path.exists(path):
                    return path
        else:
            result = subprocess.run(['which', 'mkvmerge'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                path = result.stdout.strip()
                if os.path.exists(path):
                    return path
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Fallback: check common installation paths
    if sys.platform == "win32":
        possible_paths = [
            r"C:\Program Files\MKVToolNix\mkvmerge.exe",
            r"C:\Program Files (x86)\MKVToolNix\mkvmerge.exe",
            r"C:\MKVToolNix\mkvmerge.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\MKVToolNix\mkvmerge.exe"),
        ]
    elif sys.platform == "darwin":
        # macOS paths
        possible_paths = [
            "/usr/local/bin/mkvmerge",
            "/opt/homebrew/bin/mkvmerge",
            "/usr/bin/mkvmerge",
            "/Applications/MKVToolNix.app/Contents/MacOS/mkvmerge",
            "/opt/local/bin/mkvmerge",  # MacPorts
            os.path.expanduser("~/Applications/MKVToolNix.app/Contents/MacOS/mkvmerge"),
        ]
    else:
        possible_paths = [
            "/usr/bin/mkvmerge",
            "/usr/local/bin/mkvmerge",
            "/snap/bin/mkvmerge",  # Snap package
            "/opt/mkvtoolnix/bin/mkvmerge",
            os.path.expanduser("~/.local/bin/mkvmerge"),
            "/usr/local/mkvtoolnix/bin/mkvmerge",
        ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    
    try:
        which_result = shutil.which("mkvmerge")
        if which_result:
            return which_result
    except Exception:
        pass
    
    return "mkvmerge" if sys.platform != "win32" else "mkvmerge.exe"

def verify_mkvmerge(mkvmerge_path):
    """Verify that mkvmerge is working and get version info"""
    import subprocess
    
    try:
        result = subprocess.run([mkvmerge_path, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.strip().split('\n')[0]
            return True, version_line
        else:
            return False, f"mkvmerge returned error code {result.returncode}"
    except subprocess.TimeoutExpired:
        return False, "mkvmerge timed out"
    except FileNotFoundError:
        return False, "mkvmerge executable not found"
    except Exception as e:
        return False, f"Error running mkvmerge: {str(e)}"

DEFAULT_MKVMERGE_PATH = find_mkvmerge()
DEFAULT_MKV_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads", "MKV-Manager")
DEFAULT_OUTPUT_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads", "MKV-Manager", "processed")
DEFAULT_EXTRACT_SUBTITLES = False
DEFAULT_SAVE_EXTRACTED_SUBTITLES = False

current_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(core_dir)
sys.path.insert(0, root_dir)



class UserConfigManager:
    """Manages user-specific configuration in JSON format"""

    def __init__(self):
        self.app_name = "mkv-manager"
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "user_settings.json"
        self._ensure_config_dir()
        self._load_or_create_config()

    def _get_config_dir(self):
        """Get the appropriate config directory for the current platform"""
        if sys.platform == "win32":
            # Windows: Use APPDATA
            config_base = Path(os.environ.get('APPDATA', os.path.expanduser('~')))
        elif sys.platform == "darwin":
            # macOS: Use ~/Library/Application Support
            config_base = Path.home() / "Library" / "Application Support"
        else:
            # Linux/Unix: Use XDG_CONFIG_HOME or ~/.config
            config_base = Path(os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')))
        return config_base / self.app_name

    def _ensure_config_dir(self):
        """Ensure the config directory exists"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create config directory {self.config_dir}: {e}")
            self.config_dir = Path.cwd() / f".{self.app_name}"
            self.config_file = self.config_dir / "user_settings.json"
            self.config_dir.mkdir(parents=True, exist_ok=True)

    def _get_default_config(self):
        """Get default configuration using built-in defaults"""
        return {
            "language_settings": {
                "allowed_audio_langs": list(DEFAULT_ALLOWED_AUDIO_LANGS),
                "allowed_sub_langs": list(DEFAULT_ALLOWED_SUB_LANGS),
                "default_audio_lang": DEFAULT_AUDIO_LANG,
                "default_subtitle_lang": DEFAULT_SUBTITLE_LANG,
                "original_audio_lang": DEFAULT_ORIGINAL_AUDIO_LANG,
                "original_subtitle_lang": DEFAULT_ORIGINAL_SUBTITLE_LANG
            },
            "paths": {
                "mkvmerge_path": DEFAULT_MKVMERGE_PATH,
                "mkv_folder": DEFAULT_MKV_FOLDER,
                "output_folder": DEFAULT_OUTPUT_FOLDER
            },
            "subtitle_settings": {
                "extract_subtitles": DEFAULT_EXTRACT_SUBTITLES,
                "save_extracted_subtitles": DEFAULT_SAVE_EXTRACTED_SUBTITLES
            }
        }

    def _load_or_create_config(self):
        """Load existing config or create new one with defaults"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                default_config = self._get_default_config()
                self._merge_configs(default_config, self.config)
            else:
                self.config = self._get_default_config()
                self._save_config()
        except Exception as e:
            print(f"Warning: Could not load user config: {e}")
            self.config = self._get_default_config()

    def _merge_configs(self, default, user):
        """Merge user config with default config to ensure all keys exist"""
        for key, value in default.items():
            if key not in user:
                user[key] = value
            elif isinstance(value, dict) and isinstance(user[key], dict):
                self._merge_configs(value, user[key])

    def _save_config(self):
        """Save current config to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving user config: {e}")
            return False

    def update_language_settings(self, audio_langs, sub_langs):
        """Update language settings"""
        try:
            self.config["language_settings"]["allowed_audio_langs"] = sorted(list(audio_langs))
            self.config["language_settings"]["allowed_sub_langs"] = sorted(list(sub_langs))
            
            if self.config["language_settings"]["default_audio_lang"] not in audio_langs:
                if audio_langs:
                    self.config["language_settings"]["default_audio_lang"] = sorted(list(audio_langs))[0]
            
            if self.config["language_settings"]["default_subtitle_lang"] not in sub_langs:
                if sub_langs:
                    self.config["language_settings"]["default_subtitle_lang"] = sorted(list(sub_langs))[0]
            
            return self._save_config()
        except Exception as e:
            print(f"Error updating language settings: {e}")
            return False

    def get_language_settings(self):
        """Get current language settings"""
        return self.config.get("language_settings", {})

    def get_paths(self):
        """Get current path settings"""
        return self.config.get("paths", {})

    def get_subtitle_settings(self):
        """Get current subtitle settings"""
        return self.config.get("subtitle_settings", {})

    def get_all_settings(self):
        """Get all settings as a single dict"""
        return self.config.copy()

    def update_all_settings(self, new_config):
        """Update all settings from a dict"""
        try:
            expected_keys = {"language_settings", "paths", "subtitle_settings"}
            if not all(key in new_config for key in expected_keys):
                return False
                
            self.config.update(new_config)
            return self._save_config()
        except Exception as e:
            print(f"Error updating all settings: {e}")
            return False

    def get_config_file_path(self):
        """Get the path to the user config file"""
        return str(self.config_file)

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        try:
            self.config = self._get_default_config()
            return self._save_config()
        except Exception as e:
            print(f"Error resetting config: {e}")
            return False

    def refresh_mkvmerge_path(self):
        """Re-detect and update the mkvmerge path"""
        try:
            new_path = find_mkvmerge()
            self.config["paths"]["mkvmerge_path"] = new_path
            success = self._save_config()
            if success:
                print(f"🔍 Updated mkvmerge path to: {new_path}")
            return success, new_path
        except Exception as e:
            print(f"Error refreshing mkvmerge path: {e}")
            return False, None


# Create a global instance
_user_config_manager = None

def get_user_config_manager():
    """Get the global user config manager instance"""
    global _user_config_manager
    if _user_config_manager is None:
        _user_config_manager = UserConfigManager()
    return _user_config_manager
