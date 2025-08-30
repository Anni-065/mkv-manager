#!/usr/bin/env python3
"""
Configuration manager for MKV Cleaner Desktop Application
Handles reading and writing configuration changes
"""

import os
import sys
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(core_dir)
sys.path.insert(0, root_dir)


class ConfigManager:
    """Manages configuration file updates"""

    def __init__(self):
        self.config_path = os.path.join(
            root_dir, 'core', 'config', 'config.py')

    def update_language_settings(self, audio_langs, sub_langs):
        """Update the language settings in config.py"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            updated_lines = []
            for line in lines:
                if line.strip().startswith('ALLOWED_SUB_LANGS ='):
                    sorted_sub_langs = sorted(sub_langs)
                    lang_str = ', '.join(
                        [f'"{lang}"' for lang in sorted_sub_langs])
                    updated_lines.append(
                        f'ALLOWED_SUB_LANGS = {{{lang_str}}}\n')
                elif line.strip().startswith('ALLOWED_AUDIO_LANGS ='):
                    sorted_audio_langs = sorted(audio_langs)
                    lang_str = ', '.join(
                        [f'"{lang}"' for lang in sorted_audio_langs])
                    updated_lines.append(
                        f'ALLOWED_AUDIO_LANGS = {{{lang_str}}}\n')
                else:
                    updated_lines.append(line)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)

            return True

        except Exception as e:
            print(f"Error updating config: {e}")
            return False

    def validate_default_languages(self, audio_langs, sub_langs):
        """Validate that default languages are still available after changes"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            audio_match = re.search(
                r'DEFAULT_AUDIO_LANG = ["\']([^"\']+)["\']', content)
            if audio_match:
                default_audio = audio_match.group(1)

                if default_audio not in audio_langs:
                    sorted_audio = sorted(audio_langs)

                    if sorted_audio:
                        content = re.sub(
                            r'DEFAULT_AUDIO_LANG = ["\'][^"\']+["\']',
                            f'DEFAULT_AUDIO_LANG = "{sorted_audio[0]}"',
                            content
                        )

            subtitle_match = re.search(
                r'DEFAULT_SUBTITLE_LANG = ["\']([^"\']+)["\']', content)
            if subtitle_match:
                default_subtitle = subtitle_match.group(1)

                if default_subtitle not in sub_langs:
                    sorted_sub = sorted(sub_langs)

                    if sorted_sub:
                        content = re.sub(
                            r'DEFAULT_SUBTITLE_LANG = ["\'][^"\']+["\']',
                            f'DEFAULT_SUBTITLE_LANG = "{sorted_sub[0]}"',
                            content
                        )

            orig_audio_match = re.search(
                r'ORIGINAL_AUDIO_LANG = ["\']([^"\']+)["\']', content)
            if orig_audio_match:
                orig_audio = orig_audio_match.group(1)

                if orig_audio not in audio_langs:
                    sorted_audio = sorted(audio_langs)

                    if sorted_audio:
                        content = re.sub(
                            r'ORIGINAL_AUDIO_LANG = ["\'][^"\']+["\']',
                            f'ORIGINAL_AUDIO_LANG = "{sorted_audio[0]}"',
                            content
                        )

            orig_subtitle_match = re.search(
                r'ORIGINAL_SUBTITLE_LANG = ["\']([^"\']+)["\']', content)

            if orig_subtitle_match:
                orig_subtitle = orig_subtitle_match.group(1)
                all_langs = audio_langs.union(sub_langs)

                if orig_subtitle not in all_langs:
                    sorted_all = sorted(all_langs)
                    if sorted_all:
                        content = re.sub(
                            r'ORIGINAL_SUBTITLE_LANG = ["\'][^"\']+["\']',
                            f'ORIGINAL_SUBTITLE_LANG = "{sorted_all[0]}"',
                            content
                        )

            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True

        except Exception as e:
            print(f"Error validating default languages: {e}")
            return False
