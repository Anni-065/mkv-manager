"""
Main MKV Processing Module

This module contains the main processing logic that orchestrates
all the other modules to filter and remux MKV files.
"""

import os
import shutil
from datetime import datetime
from ..analysis.track_analyzer import get_track_info
from ..analysis.filename_processor import extract_series_info
from ..subtitles.subtitle_processor import (
    deduplicate_subtitles, process_subtitles_systematically
)
from .mkv_operations import run_mkvmerge
from ..config.constants import LANG_TITLES
from ..utils.subprocess_utils import run_hidden

try:
    from ..config.user_config import get_user_config_manager
    # Get default config values
    _user_config = get_user_config_manager()
    _settings = _user_config.get_all_settings()
    _lang_settings = _settings.get('language_settings', {})
    
    ALLOWED_AUDIO_LANGS = set(_lang_settings.get('allowed_audio_langs', ['eng', 'ger', 'jpn', 'kor']))
    ALLOWED_SUB_LANGS = set(_lang_settings.get('allowed_sub_langs', ['eng', 'ger', 'kor', 'gre']))
    DEFAULT_AUDIO_LANG = _lang_settings.get('default_audio_lang', 'eng')
    DEFAULT_SUBTITLE_LANG = _lang_settings.get('default_subtitle_lang', 'eng')
    ORIGINAL_AUDIO_LANG = _lang_settings.get('original_audio_lang', 'eng')
    ORIGINAL_SUBTITLE_LANG = _lang_settings.get('original_subtitle_lang', 'eng')
    
    _subtitle_settings = _settings.get('subtitle_settings', {})
    EXTRACT_SUBTITLES = _subtitle_settings.get('extract_subtitles', False)
    SAVE_EXTRACTED_SUBTITLES = _subtitle_settings.get('save_extracted_subtitles', False)
    
    _paths = _settings.get('paths', {})
    OUTPUT_FOLDER = _paths.get('output_folder', '/tmp')
    MKVMERGE_PATH = _paths.get('mkvmerge_path', 'mkvmerge')
    
except ImportError:
    # Fallback to hardcoded defaults
    ALLOWED_AUDIO_LANGS = {'eng', 'ger', 'jpn', 'kor'}
    ALLOWED_SUB_LANGS = {'eng', 'ger', 'kor', 'gre'}
    DEFAULT_AUDIO_LANG = 'eng'
    DEFAULT_SUBTITLE_LANG = 'eng'
    ORIGINAL_AUDIO_LANG = 'eng'
    ORIGINAL_SUBTITLE_LANG = 'eng'
    EXTRACT_SUBTITLES = False
    SAVE_EXTRACTED_SUBTITLES = False
    OUTPUT_FOLDER = '/tmp'
    MKVMERGE_PATH = 'mkvmerge'


def log_entry(file_name, changes, log_file=None):
    """Log processing changes to a file"""
    if log_file is None:
        log_file = os.path.join(OUTPUT_FOLDER, "mkv_process_log.txt")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.now()}] {file_name}\n")
        for line in changes:
            f.write(f"  - {line}\n")


def filter_and_remux(file_path, output_folder=None, preferences=None, extract_subtitles=False, progress_callback=None):
    """
    Main function to filter and remux MKV files.

    Args:
        file_path: Path to the input MKV file
        output_folder: Output directory (optional)
        preferences: Configuration preferences dict (optional)
        extract_subtitles: Whether to extract subtitles (optional)
        progress_callback: Callback function for progress updates (optional)
    """
    source_dir = os.path.dirname(file_path)

    if preferences:
        allowed_audio_langs = set(preferences.get(
            'ALLOWED_AUDIO_LANGS', ALLOWED_AUDIO_LANGS))
        allowed_sub_langs = set(preferences.get(
            'ALLOWED_SUB_LANGS', ALLOWED_SUB_LANGS))
        default_audio_lang = preferences.get(
            'DEFAULT_AUDIO_LANG', DEFAULT_AUDIO_LANG)
        default_subtitle_lang = preferences.get(
            'DEFAULT_SUBTITLE_LANG', DEFAULT_SUBTITLE_LANG)
        original_audio_lang = preferences.get(
            'ORIGINAL_AUDIO_LANG', ORIGINAL_AUDIO_LANG)
        original_subtitle_lang = preferences.get(
            'ORIGINAL_SUBTITLE_LANG', ORIGINAL_SUBTITLE_LANG)
        extract_subtitles = preferences.get(
            'EXTRACT_SUBTITLES', extract_subtitles)
    else:
        allowed_audio_langs = ALLOWED_AUDIO_LANGS
        allowed_sub_langs = ALLOWED_SUB_LANGS
        default_audio_lang = DEFAULT_AUDIO_LANG
        default_subtitle_lang = DEFAULT_SUBTITLE_LANG
        original_audio_lang = ORIGINAL_AUDIO_LANG
        original_subtitle_lang = ORIGINAL_SUBTITLE_LANG

    if output_folder:
        try:
            os.makedirs(output_folder, exist_ok=True)
            test_file = os.path.join(output_folder, "test_write.tmp")

            with open(test_file, 'w') as f:
                f.write("test")

            os.remove(test_file)

        except (OSError, PermissionError) as e:
            output_folder = OUTPUT_FOLDER
            os.makedirs(output_folder, exist_ok=True)
            print(
                f"INFO: Could not use specified output folder, using default: {output_folder}")
            print(f"   Reason: {str(e)}")

    else:
        try:
            output_folder = os.path.join(source_dir, "processed")
            os.makedirs(output_folder, exist_ok=True)
            test_file = os.path.join(output_folder, "test_write.tmp")

            with open(test_file, 'w') as f:
                f.write("test")

            os.remove(test_file)

        except (OSError, PermissionError) as e:
            output_folder = OUTPUT_FOLDER
            os.makedirs(output_folder, exist_ok=True)

            print(
                f"INFO: Could not create output folder in {source_dir}, using default: {output_folder}")
            print(f"   Reason: {str(e)}")

    base_name = os.path.splitext(os.path.basename(file_path))[0]

    series_title, season_episode_tag, season_num, episode_num, episode_title = extract_series_info(
        os.path.basename(file_path))

    if series_title and season_episode_tag:
        if episode_title:
            output_name = f"{series_title} - {season_episode_tag} - {episode_title}.mkv"
            title_for_mkv = f"{series_title} - {season_episode_tag} - {episode_title}"

        else:
            output_name = f"{series_title} - {season_episode_tag} - Episode #{season_num}.{episode_num}.mkv"
            title_for_mkv = f"{series_title} - {season_episode_tag} - Episode #{season_num}.{episode_num}"

    else:
        output_name = base_name + "_cleaned.mkv"
        title_for_mkv = base_name + "_cleaned"

    output_file = os.path.join(output_folder, output_name)

    tracks = get_track_info(file_path)

    cmd = [MKVMERGE_PATH, "-o", output_file, "--title", title_for_mkv]
    change_log = []

    change_log.append(f"Renamed to: {output_name}")
    change_log.append(f"MKV title: {title_for_mkv}")

    if episode_title:
        change_log.append(f"Episode title extracted: {episode_title}")

    video_tracks = []
    audio_tracks = []
    subtitle_tracks = []

    for t in tracks:
        tid = t["id"]
        ttype = t["type"]
        lang = t["lang"]
        forced = t.get("forced", False)
        hearing_impaired = t.get("hearing_impaired", False)
        track_name = t.get("track_name", "")
        title = LANG_TITLES.get(lang, lang)

        if ttype == "video":
            video_tracks.append(str(tid))
            cmd += ["--language", f"{tid}:und"]
            cmd += ["--track-name", f"{tid}:"]
            change_log.append(
                f"Keep video track {tid} (no linguistic content)")

        elif ttype == "audio":
            if lang in allowed_audio_langs:
                audio_tracks.append(str(tid))
                is_def = (lang == default_audio_lang)
                is_original = (lang == original_audio_lang)
                cmd += ["--default-track",
                        f"{tid}:{'yes' if is_def else 'no'}"]
                cmd += ["--original-flag",
                        f"{tid}:{'yes' if is_original else 'no'}"]
                cmd += ["--track-name", f"{tid}:{title}"]

                if is_def:
                    change_log.append(f"Set audio {tid} [{title}] as default")
                else:
                    change_log.append(f"Keep audio {tid} [{title}]")

                if is_original:
                    change_log.append(f"Set audio {tid} [{title}] as original")
            else:
                change_log.append(f"Removed audio track {tid} [{title}]")

        elif ttype == "subtitles":
            is_forced_original = forced and lang == original_subtitle_lang
            is_allowed_lang = lang in allowed_sub_langs
            is_forced_for_audio = forced and lang in allowed_audio_langs

            if is_allowed_lang or is_forced_original or is_forced_for_audio:
                subtitle_tracks.append({
                    "id": tid,
                    "lang": lang,
                    "forced": forced,
                    "hearing_impaired": hearing_impaired,
                    "track_name": track_name,
                    "title": title
                })
            else:
                change_log.append(f"Removed subtitle track {tid} [{title}]")

    deduplicated_subtitles = deduplicate_subtitles(subtitle_tracks)

    save_extracted_subtitles = preferences.get(
        'SAVE_EXTRACTED_SUBTITLES', False) if preferences else False

    processed_subtitles, temp_subtitle_files, saved_subtitle_files, original_subtitle_track_ids, original_track_metadata = process_subtitles_systematically(
        file_path, output_folder, deduplicated_subtitles, extract_subtitles,
        allowed_audio_langs, allowed_sub_langs, default_subtitle_lang, original_subtitle_lang, save_extracted_subtitles)

    if video_tracks:
        cmd += ["--video-tracks", ",".join(video_tracks)]
    if audio_tracks:
        cmd += ["--audio-tracks", ",".join(audio_tracks)]

    if original_subtitle_track_ids:
        cmd += ["--subtitle-tracks", ",".join(original_subtitle_track_ids)]

        for track_id in original_subtitle_track_ids:
            if track_id in original_track_metadata:
                metadata = original_track_metadata[track_id]

                if metadata.get('language'):
                    cmd.extend(
                        ["--language", f"{track_id}:{metadata['language']}"])

                if metadata.get('title'):
                    cmd.extend(
                        ["--track-name", f"{track_id}:{metadata['title']}"])

                if metadata.get('default'):
                    cmd.extend(["--default-track", f"{track_id}:yes"])
                else:
                    cmd.extend(["--default-track", f"{track_id}:no"])

                if metadata.get('original'):
                    cmd.extend(["--original-flag", f"{track_id}:yes"])
                else:
                    cmd.extend(["--original-flag", f"{track_id}:no"])

                if metadata.get('forced'):
                    cmd.extend(["--forced-track", f"{track_id}:yes"])

                if metadata.get('hearing_impaired'):
                    cmd.extend(["--hearing-impaired-flag", f"{track_id}:yes"])

        print(
            f"📝 Keeping original subtitle tracks: {', '.join(original_subtitle_track_ids)}")

    elif processed_subtitles:
        cmd += ["--no-subtitles"]
        print("📝 Excluding all original subtitle tracks (using processed files)")

    else:
        cmd += ["--no-subtitles"]
        print("📝 No subtitle tracks to include")

    cmd.append(file_path)

    for subtitle_file, subtitle_metadata in processed_subtitles:
        cmd.extend(subtitle_metadata)
        cmd.append(subtitle_file)

    if processed_subtitles:
        change_log.append(
            f"Processed {len(processed_subtitles)} subtitle(s) with proper formatting and flags")

    print(f"\nProcessing: {file_path}")

    if progress_callback:
        run_mkvmerge(cmd, progress_callback)
    else:
        run_hidden(cmd, check=True)

    print(f"Saved: {output_file}")

    if saved_subtitle_files:
        output_dir = os.path.dirname(output_file)
        for saved_file in saved_subtitle_files:
            try:
                output_base = os.path.splitext(
                    os.path.basename(output_file))[0]
                saved_base = os.path.splitext(os.path.basename(saved_file))[0]

                parts = saved_base.split('.')

                if len(parts) >= 2:
                    lang_suffix = '.'.join(parts[1:])
                    final_subtitle_name = f"{output_base}.{lang_suffix}.srt"

                else:
                    final_subtitle_name = f"{output_base}.srt"

                final_subtitle_path = os.path.join(
                    output_dir, final_subtitle_name)

                shutil.copy2(saved_file, final_subtitle_path)

                os.remove(saved_file)

            except Exception as e:
                print(
                    f"ERR: Error saving subtitle file {os.path.basename(saved_file)}: {str(e)}")

    for temp_file in temp_subtitle_files:
        try:
            os.remove(temp_file)
        except OSError:
            pass

    log_file = os.path.join(output_folder, "mkv_process_log.txt")
    log_entry(os.path.basename(file_path), change_log, log_file)
