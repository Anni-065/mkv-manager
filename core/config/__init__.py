"""
Config Module

This module contains configuration constants and settings
for the MKV Manager application.
"""

from .constants import (
    LANG_TITLES, QUALITY_TAGS, QUALITY_PATTERNS, QUALITY_TAGS_SERIES,
    ABBREVIATIONS, SEASON_EPISODE_PATTERN, QUALITY_PATTERN_SERIES, SOURCE_PATTERN
)

# Try to load configuration in order of preference:
# 1. User-specific config (JSON)
# 2. Hardcoded fallback defaults

try:
    # Try user configuration first
    from .user_config import get_user_config_manager
    _user_config = get_user_config_manager()
    _lang_settings = _user_config.get_language_settings()
    _paths = _user_config.get_paths()
    _subtitle_settings = _user_config.get_subtitle_settings()
    
    ALLOWED_AUDIO_LANGS = set(_lang_settings.get('allowed_audio_langs', ['eng', 'ger', 'jpn', 'kor']))
    ALLOWED_SUB_LANGS = set(_lang_settings.get('allowed_sub_langs', ['eng', 'ger', 'kor', 'gre']))
    DEFAULT_AUDIO_LANG = _lang_settings.get('default_audio_lang', 'eng')
    DEFAULT_SUBTITLE_LANG = _lang_settings.get('default_subtitle_lang', 'eng')
    ORIGINAL_AUDIO_LANG = _lang_settings.get('original_audio_lang', 'eng')
    ORIGINAL_SUBTITLE_LANG = _lang_settings.get('original_subtitle_lang', 'eng')
    
    MKVMERGE_PATH = _paths.get('mkvmerge_path', '/usr/bin/mkvmerge')
    MKV_FOLDER = _paths.get('mkv_folder', '/path/to/your/mkv/files')
    OUTPUT_FOLDER = _paths.get('output_folder', '/path/to/output')
    
    EXTRACT_SUBTITLES = _subtitle_settings.get('extract_subtitles', False)
    SAVE_EXTRACTED_SUBTITLES = _subtitle_settings.get('save_extracted_subtitles', False)
    
    print("✅ Using user configuration settings")
    
except Exception as e:
    print(f"⚠️ Could not load user config, using hardcoded defaults: {e}")
    # Hardcoded fallback defaults - no longer relying on defaults.py
    ALLOWED_AUDIO_LANGS = {"eng", "ger", "jpn", "kor"}
    ALLOWED_SUB_LANGS = {"eng", "ger", "kor", "gre"}
    DEFAULT_AUDIO_LANG = "eng"
    DEFAULT_SUBTITLE_LANG = "eng"
    ORIGINAL_AUDIO_LANG = "eng"
    ORIGINAL_SUBTITLE_LANG = "eng"
    MKVMERGE_PATH = "/usr/bin/mkvmerge"
    MKV_FOLDER = "/path/to/your/mkv/files"
    OUTPUT_FOLDER = "/path/to/output"
    EXTRACT_SUBTITLES = False
    SAVE_EXTRACTED_SUBTITLES = False

__all__ = [
    "LANG_TITLES",
    "QUALITY_TAGS",
    "QUALITY_PATTERNS",
    "QUALITY_TAGS_SERIES",
    "ABBREVIATIONS",
    "SEASON_EPISODE_PATTERN",
    "QUALITY_PATTERN_SERIES",
    "SOURCE_PATTERN",
    "MKVMERGE_PATH",
    "MKV_FOLDER",
    "OUTPUT_FOLDER",
    "ALLOWED_SUB_LANGS",
    "ALLOWED_AUDIO_LANGS",
    "DEFAULT_AUDIO_LANG",
    "DEFAULT_SUBTITLE_LANG",
    "ORIGINAL_AUDIO_LANG",
    "ORIGINAL_SUBTITLE_LANG",
    "EXTRACT_SUBTITLES",
    "SAVE_EXTRACTED_SUBTITLES"
]
