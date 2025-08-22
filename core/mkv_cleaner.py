import os
import subprocess
import json
import shutil
from datetime import datetime
import re
from .constants import (
    LANG_TITLES, QUALITY_TAGS, QUALITY_PATTERNS, QUALITY_TAGS_SERIES,
    ABBREVIATIONS, SEASON_EPISODE_PATTERN, QUALITY_PATTERN_SERIES, SOURCE_PATTERN
)

try:
    from .config import *
    print("✅ Using personal config.py")
except ImportError:
    try:
        from .config_example import *
        print("⚠️ Using config_example.py - Consider creating a personal config.py")
    except ImportError:
        print("❌ No configuration file found!")
        raise ImportError(
            "Please create config.py or ensure config_example.py exists")

assert os.path.isfile(
    MKVMERGE_PATH), f"Cannot find mkvmerge at {MKVMERGE_PATH}"

LOG_FILE = os.path.join(OUTPUT_FOLDER, "mkv_process_log.txt")


def is_forced_subtitle_by_name(track_name):
    """
    Check if a subtitle track should be treated as forced based on its name.
    Returns True if the track name contains indicators of forced subtitles.
    """
    if not track_name:
        return False

    track_name_lower = track_name.lower()
    forced_indicators = ['signs', 'songs', 'forced']

    result = any(
        indicator in track_name_lower for indicator in forced_indicators)

    return result


def get_track_info(file_path):
    file_path = os.path.normpath(file_path)
    cmd = [MKVMERGE_PATH, "-J", file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    try:
        data = json.loads(result.stdout)
        tracks = []

        for track in data.get("tracks", []):
            track_name = track["properties"].get("track_name", "")
            original_forced = track["properties"].get("forced_track", False)

            name_based_forced = is_forced_subtitle_by_name(track_name)
            is_forced = original_forced or name_based_forced

            tracks.append({
                "id": track["id"],
                "type": track["type"],
                "lang": track["properties"].get("language", "und"),
                "forced": is_forced,
                "hearing_impaired": track["properties"].get("hearing_impaired_flag", False),
                "track_name": track_name
            })

        return tracks

    except json.JSONDecodeError:
        print(f"Error parsing JSON from mkvmerge output: {result.stdout}")
        return []


def log_entry(file_name, changes, log_file=None):
    if log_file is None:
        log_file = LOG_FILE

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.now()}] {file_name}\n")
        for line in changes:
            f.write(f"  - {line}\n")


def extract_series_info(filename):
    base_name = os.path.splitext(filename)[0]

    season_episode_match = re.search(SEASON_EPISODE_PATTERN, base_name)

    if not season_episode_match:
        return None, None, None, None, None

    season_num = int(season_episode_match.group(1))
    episode_num = int(season_episode_match.group(2))
    season_episode_tag = f"S{season_num:02d}E{episode_num:02d}"

    season_start = season_episode_match.start()
    season_end = season_episode_match.end()

    full_title = base_name[:season_start]

    if season_start > 0:
        delimiter_char = base_name[season_start - 1]
        series_title = full_title[:-
                                  1] if full_title.endswith(delimiter_char) else full_title

        if delimiter_char == ' ' and len(full_title) >= 2 and full_title[-2] == '.':
            before_dot = full_title[:-2]
            if re.search(r'\b\w{1,2}$', before_dot):
                series_title = full_title[:-1]
                delimiter_used = ' '
            else:
                series_title = full_title[:-2]
                delimiter_used = '.'
        else:
            delimiter_used = delimiter_char
    else:
        delimiter_used = ' '
        series_title = full_title

    episode_title = None
    remainder = base_name[season_end:]

    if remainder:
        if remainder.startswith('.') or remainder.startswith(' ') or remainder.startswith('-') or remainder.startswith('_'):
            remainder = remainder[1:]

        episode_title = remainder
        earliest_match = len(remainder)

        for pattern in QUALITY_PATTERNS:
            match = re.search(pattern, remainder, re.IGNORECASE)
            if match:
                earliest_match = min(earliest_match, match.start())

        if earliest_match < len(remainder):
            episode_title = remainder[:earliest_match]
        else:
            episode_title = remainder

        if episode_title:
            episode_title = episode_title.strip()

            episode_title = re.sub(r'[._-]+', ' ', episode_title)
            episode_title = re.sub(r'\s+', ' ', episode_title).strip()

        if not episode_title or len(episode_title) < 2:
            episode_title = None

    series_title = re.sub(r'[\s\-_]+$', '', series_title)
    series_title = re.sub(r'\.{2,}$', '', series_title)

    if delimiter_used == '.':
        series_title = re.sub(r'(\w{3,})\.$', r'\1', series_title)

    for abbrev, placeholder in ABBREVIATIONS.items():
        series_title = series_title.replace(abbrev, placeholder)

    if delimiter_used == '.':
        series_title = re.sub(r'\.{2,}', ' ', series_title)
        series_title = re.sub(r'(\w{2,})\.(\w{2,})', r'\1 \2', series_title)
        series_title = re.sub(r'\.(?=\s)', ' ', series_title)
        series_title = re.sub(r'(?<=\w)\.(?=\w)', ' ', series_title)

    if delimiter_used == '-':
        series_title = re.sub(r'[\-]+', ' ', series_title)

    if delimiter_used == '_':
        series_title = re.sub(r'[_]+', ' ', series_title)

    for abbrev, placeholder in ABBREVIATIONS.items():
        series_title = series_title.replace(placeholder, abbrev)

    series_title = re.sub(QUALITY_PATTERN_SERIES, '',
                          series_title, flags=re.IGNORECASE)

    series_title = re.sub(r'\b\d{4}\b', '', series_title)

    series_title = re.sub(r'\s*-\s*[A-Z0-9]+$', '', series_title)
    series_title = re.sub(r'\s+', ' ', series_title).strip()

    return series_title, season_episode_tag, season_num, episode_num, episode_title


def process_subtitles_systematically(file_path, output_folder, collected_subtitles, extract_subtitles, allowed_audio_langs, allowed_sub_langs, default_subtitle_lang, original_subtitle_lang, save_extracted_subtitles=False):
    """
    Process subtitles systematically according to following approach:
    1. Scan available subtitle tracks
    2. Remove non-forced tracks that are not in ALLOWED_SUB_LANGS
    3. Remove forced subtitles that are not in ALLOWED_AUDIO_LANGS or ALLOWED_SUB_LANGS
    4. Deduplicate by language, preferring SRT format
    5. Set appropriate flags and names
    """

    processed_subtitles = []
    temp_files = []
    saved_subtitle_files = []

    print(f"📋 Found {len(collected_subtitles)} subtitle tracks")

    allowed_subtitles = []

    for sub in collected_subtitles:
        lang = sub["lang"]
        forced = sub["forced"]

        if forced:
            if lang in allowed_audio_langs or lang in allowed_sub_langs:
                allowed_subtitles.append(sub)
                reason = []
                if lang in allowed_audio_langs:
                    reason.append("allowed audio languages")
                if lang in allowed_sub_langs:
                    reason.append("allowed subtitle languages")
                print(
                    f"✅ Keeping forced subtitle track {sub['id']} [{lang}] (in {' and '.join(reason)})")
            else:
                print(
                    f"🗑️ Removing forced subtitle track {sub['id']} [{lang}] (not in allowed audio or subtitle languages)")
        else:
            if lang in allowed_sub_langs:
                allowed_subtitles.append(sub)
                print(
                    f"✅ Keeping non-forced subtitle track {sub['id']} [{lang}] (in allowed subtitle languages)")
            else:
                print(
                    f"🗑️ Removing non-forced subtitle track {sub['id']} [{lang}] (not in allowed subtitle languages)")

    print(f"✅ Kept {len(allowed_subtitles)} subtitle tracks after filtering")

    conversion_results = []

    for sub in allowed_subtitles:
        tid = sub["id"]
        lang = sub["lang"]
        forced = sub["forced"]
        hearing_impaired = sub["hearing_impaired"]

        result = {
            "original_id": tid,
            "lang": lang,
            "forced": forced,
            "hearing_impaired": hearing_impaired,
            "is_srt": False,
            "file_path": None,
            "conversion_success": False
        }

        if extract_subtitles:
            print(f"🔄 Processing subtitle track {tid} [{lang}]...")

            suffix = ""
            if forced:
                suffix += ".forced"
            if hearing_impaired:
                suffix += ".sdh"

            base_name = os.path.splitext(os.path.basename(file_path))[0]
            temp_extracted = os.path.join(
                output_folder, f"{base_name}.{lang}{suffix}.temp")
            final_srt = os.path.join(
                output_folder, f"{base_name}.{lang}{suffix}.srt")

            try:
                mkvextract_path = MKVMERGE_PATH.replace(
                    "mkvmerge", "mkvextract")
                extract_cmd = [mkvextract_path, "tracks",
                               file_path, f"{tid}:{temp_extracted}"]
                result_extract = subprocess.run(
                    extract_cmd, capture_output=True, text=True)

                if result_extract.returncode == 0 and os.path.exists(temp_extracted):
                    if is_srt_format(temp_extracted):
                        os.rename(temp_extracted, final_srt)
                        result["is_srt"] = True
                        result["file_path"] = final_srt
                        result["conversion_success"] = True

                        if save_extracted_subtitles:
                            saved_subtitle_files.append(final_srt)
                        else:
                            temp_files.append(final_srt)

                        process_srt_file_line_breaks(final_srt)

                        print(
                            f"✅ Already SRT format: {os.path.basename(final_srt)}")
                    else:
                        conversion_success, conversion_msg = convert_subtitle_to_srt(
                            temp_extracted, final_srt)

                        if conversion_success and os.path.exists(final_srt):
                            result["is_srt"] = True
                            result["file_path"] = final_srt
                            result["conversion_success"] = True

                            if save_extracted_subtitles:
                                saved_subtitle_files.append(final_srt)
                            else:
                                temp_files.append(final_srt)

                            process_srt_file_line_breaks(final_srt)

                            print(
                                f"✅ Converted to SRT: {os.path.basename(final_srt)} ({conversion_msg})")
                        else:
                            print(
                                f"⚠️ Could not convert to SRT: {conversion_msg}")
                            result["conversion_success"] = False

                        try:
                            os.remove(temp_extracted)
                        except OSError:
                            pass
                else:
                    print(f"⚠️ Failed to extract subtitle track {tid}")
                    result["conversion_success"] = False

            except Exception as e:
                print(f"⚠️ Error processing subtitle track {tid}: {str(e)}")
                result["conversion_success"] = False
        else:
            result["conversion_success"] = True

        conversion_results.append(result)

    filtered_results = conversion_results

    lang_groups = {}
    for result in filtered_results:
        lang = result["lang"]
        if lang not in lang_groups:
            lang_groups[lang] = []
        lang_groups[lang].append(result)

    final_subtitles = []

    for lang, results in lang_groups.items():
        if len(results) == 1:
            final_subtitles.extend(results)
        else:
            normal_results = [r for r in results if not r["forced"]]
            forced_results = [r for r in results if r["forced"]]

            def prefer_srt(group):
                if not group:
                    return []
                srt_results = [r for r in group if r["is_srt"]]
                if srt_results:
                    return [srt_results[0]]
                else:
                    return [group[0]]

            final_subtitles.extend(prefer_srt(normal_results))
            final_subtitles.extend(prefer_srt(forced_results))

    for result in final_subtitles:
        lang = result["lang"]
        forced = result["forced"]
        hearing_impaired = result["hearing_impaired"]

        base_title = LANG_TITLES.get(lang, lang)
        if forced and hearing_impaired:
            track_title = f"{base_title} (Forced SDH)"
        elif forced:
            track_title = f"{base_title} (Forced)"
        elif hearing_impaired:
            track_title = f"{base_title} (SDH)"
        else:
            track_title = base_title

        is_default_sub = (lang == default_subtitle_lang and not forced)
        is_original_sub = (lang == original_subtitle_lang)

        metadata = []
        if lang and lang.strip():
            metadata.extend(["--language", f"0:{lang}"])
        metadata.extend(["--track-name", f"0:{track_title}"])
        metadata.extend(
            ["--default-track", f"0:{'yes' if is_default_sub else 'no'}"])
        metadata.extend(
            ["--original-flag", f"0:{'yes' if is_original_sub else 'no'}"])

        if forced:
            metadata.extend(["--forced-track", "0:yes"])
        if hearing_impaired:
            metadata.extend(["--hearing-impaired-flag", "0:yes"])

        if result["file_path"]:
            processed_subtitles.append((result["file_path"], metadata))
            print(
                f"📝 Added subtitle: {track_title} -> {os.path.basename(result['file_path'])}")
        else:
            # When not extracting, we need to keep the original track
            # Add the original track ID to a list of tracks to keep
            original_track_id = result["original_id"]
            print(
                f"📝 Keeping original subtitle track {original_track_id} [{track_title}]")

    # Create lists for original track handling
    original_subtitle_track_ids = []
    original_track_metadata = {}

    for result in final_subtitles:
        if not result["file_path"]:  # No extracted file means keep original
            original_track_id = result["original_id"]
            original_subtitle_track_ids.append(str(original_track_id))

            # Build metadata for the original track
            lang = result["lang"]
            forced = result["forced"]
            hearing_impaired = result["hearing_impaired"]

            base_title = LANG_TITLES.get(lang, lang)
            if forced and hearing_impaired:
                track_title = f"{base_title} (Forced SDH)"
            elif forced:
                track_title = f"{base_title} (Forced)"
            elif hearing_impaired:
                track_title = f"{base_title} (SDH)"
            else:
                track_title = base_title

            is_default_sub = (lang == default_subtitle_lang and not forced)
            is_original_sub = (lang == original_subtitle_lang)

            # Store metadata for this track ID
            original_track_metadata[str(original_track_id)] = {
                'language': lang,
                'title': track_title,
                'default': is_default_sub,
                'forced': forced,
                'hearing_impaired': hearing_impaired,
                'original': is_original_sub
            }

    return processed_subtitles, temp_files, saved_subtitle_files, original_subtitle_track_ids, original_track_metadata


def process_subtitles_with_conversion(file_path, output_folder, deduplicated_subtitles, convert_to_srt=False, default_subtitle_lang=None, original_subtitle_lang=None):
    """Process subtitles and optionally convert them to SRT, returning mkvmerge command parts"""
    subtitle_cmd_parts = []
    subtitle_tracks = []
    temp_files = []

    if not deduplicated_subtitles:
        return subtitle_cmd_parts, subtitle_tracks, temp_files

    for sub in deduplicated_subtitles:
        tid = sub["id"]
        lang = sub["lang"]
        forced = sub["forced"]
        hearing_impaired = sub["hearing_impaired"]
        track_name = sub["track_name"]
        title = sub["title"]

        name_based_forced = is_forced_subtitle_by_name(track_name)
        actual_forced = forced or name_based_forced

        if name_based_forced and not forced:
            print(
                f"🏷️ Additional forced detection by name in conversion: '{track_name}' (Track {tid})")

        base_title = LANG_TITLES.get(lang, lang)
        if actual_forced and hearing_impaired:
            track_title = f"{base_title} (Forced SDH)"
        elif actual_forced:
            track_title = f"{base_title} (Forced)"
        elif hearing_impaired:
            track_title = f"{base_title} (SDH)"
        else:
            track_title = base_title

        if convert_to_srt:
            print(
                f"🔄 Converting subtitle track {tid} [{track_title}] to SRT...")

            suffix = ""
            if actual_forced:
                suffix += ".forced"
            if hearing_impaired:
                suffix += ".sdh"

            base_name = os.path.splitext(os.path.basename(file_path))[0]
            temp_extracted = os.path.join(
                output_folder, f"{base_name}.{lang}{suffix}.temp")
            temp_srt = os.path.join(
                output_folder, f"{base_name}.{lang}{suffix}.srt")

            try:
                mkvextract_path = MKVMERGE_PATH.replace(
                    "mkvmerge", "mkvextract")
                extract_cmd = [mkvextract_path, "tracks",
                               file_path, f"{tid}:{temp_extracted}"]
                result = subprocess.run(
                    extract_cmd, capture_output=True, text=True)

                if result.returncode == 0 and os.path.exists(temp_extracted):
                    file_size = os.path.getsize(temp_extracted)
                    print(
                        f"📄 Extracted subtitle file: {os.path.basename(temp_extracted)} ({file_size} bytes)")

                    if is_srt_format(temp_extracted):
                        os.rename(temp_extracted, temp_srt)
                        conversion_success = True
                        conversion_msg = "Already in SRT format"

                    else:
                        try:
                            with open(temp_extracted, 'rb') as f:
                                first_bytes = f.read(100)

                            if first_bytes.startswith(b'PG') or b'\x50\x47' in first_bytes[:10]:
                                format_detected = "HDMV PGS (bitmap subtitles - cannot convert to SRT)"
                                print(f"🔍 Detected format: {format_detected}")
                                print(
                                    f"⚠️ PGS subtitles are image-based and cannot be converted to text format")
                                conversion_success = False
                                conversion_msg = "PGS subtitles are bitmap images, not text"

                            else:
                                with open(temp_extracted, 'r', encoding='utf-8', errors='ignore') as f:
                                    first_lines = f.read(1000)

                                if any(pattern in first_lines for pattern in [' m ', ' b ', ' l ', ' c ', ' z ', 'M ', 'L ', 'C ', 'Z ']):
                                    format_detected = "Vector graphics (cannot convert to SRT)"
                                    print(
                                        f"🔍 Detected format: {format_detected}")
                                    print(
                                        f"⚠️ Vector graphics subtitles contain image data and cannot be converted to text format")
                                    conversion_success = False
                                    conversion_msg = "Vector graphics subtitles are image-based, not text"

                                elif '[Script Info]' in first_lines or 'Dialogue:' in first_lines:
                                    format_detected = "ASS/SSA"

                                    has_text_content = False
                                    with open(temp_extracted, 'r', encoding='utf-8', errors='ignore') as f:
                                        for line in f:
                                            if line.startswith('Dialogue:'):
                                                parts = line.split(',', 9)
                                                if len(parts) >= 10:
                                                    text = parts[9].strip()
                                                    text = re.sub(
                                                        r'\{[^}]*\}', '', text)
                                                    text = text.replace('\\N', '\n').replace(
                                                        '\\n', '\n').strip()

                                                    if text and not any(pattern in text for pattern in [' m ', ' b ', ' l ', ' c ', ' z ', 'M ', 'L ', 'C ', 'Z ']):
                                                        if len(set(text.replace('\n', '').replace(' ', ''))) > 1:
                                                            if len(text.replace('\n', '').replace(' ', '')) > 2:
                                                                has_text_content = True
                                                                break

                                    if not has_text_content:
                                        format_detected = "ASS/SSA (vector graphics only - cannot convert to SRT)"
                                        print(
                                            f"🔍 Detected format: {format_detected}")
                                        print(
                                            f"⚠️ This ASS file contains only vector graphics and cannot be converted to text format")
                                        conversion_success = False
                                        conversion_msg = "ASS file contains only vector graphics, not text"

                                    else:
                                        print(
                                            f"🔍 Detected format: {format_detected}")

                                        conversion_success, conversion_msg = convert_subtitle_to_srt(
                                            temp_extracted, temp_srt)

                                elif ('<tt ' in first_lines or '<p ' in first_lines) and 'begin=' in first_lines:
                                    format_detected = "TTML/XML"
                                    print(
                                        f"🔍 Detected format: {format_detected}")

                                    conversion_success, conversion_msg = convert_subtitle_to_srt(
                                        temp_extracted, temp_srt)

                                elif '<?xml' in first_lines and '<p' in first_lines:
                                    format_detected = "TTML/XML (variant)"
                                    print(
                                        f"🔍 Detected format: {format_detected}")

                                    conversion_success, conversion_msg = convert_subtitle_to_srt(
                                        temp_extracted, temp_srt)

                                elif '<' in first_lines and '>' in first_lines:
                                    format_detected = "XML-based (unknown format)"
                                    print(
                                        f"🔍 Detected format: {format_detected}")

                                    conversion_success, conversion_msg = convert_subtitle_to_srt(
                                        temp_extracted, temp_srt)

                                else:
                                    format_detected = "Unknown text format"
                                    print(
                                        f"🔍 Detected format: {format_detected}")

                                    conversion_success, conversion_msg = convert_subtitle_to_srt(
                                        temp_extracted, temp_srt)

                        except Exception as e:
                            format_detected = "Unknown"
                            print(f"🔍 Detected format: {format_detected}")
                            conversion_success, conversion_msg = convert_subtitle_to_srt(
                                temp_extracted, temp_srt)

                        try:
                            os.remove(temp_extracted)
                        except OSError:
                            pass

                    if conversion_success and os.path.exists(temp_srt):
                        temp_files.append(temp_srt)

                        is_default_sub = (
                            lang == default_subtitle_lang and not actual_forced)
                        is_original_sub = (lang == original_subtitle_lang)

                        subtitle_cmd_parts.extend([
                            "--language", f"0:{lang}",
                            "--track-name", f"0:{track_title}",
                            "--default-track", f"0:{'yes' if is_default_sub else 'no'}",
                            "--original-flag", f"0:{'yes' if is_original_sub else 'no'}"
                        ])

                        if actual_forced:
                            subtitle_cmd_parts.extend(
                                ["--forced-track", "0:yes"])
                        if hearing_impaired:
                            subtitle_cmd_parts.extend(
                                ["--hearing-impaired-flag", "0:yes"])

                        subtitle_cmd_parts.append(temp_srt)

                        print(
                            f"✅ Converted subtitle track {tid} to SRT: {os.path.basename(temp_srt)} ({conversion_msg})")
                        continue

                    else:
                        print(
                            f"⚠️ Failed to convert subtitle track {tid} to SRT: {conversion_msg}")
                        print(
                            f"🔄 Falling back to original subtitle track {tid}")

                else:
                    print(
                        f"⚠️ Failed to extract subtitle track {tid}: {result.stderr}")
                    print(f"🔄 Falling back to original subtitle track {tid}")

            except Exception as e:
                print(f"⚠️ Error processing subtitle track {tid}: {str(e)}")
                print(f"🔄 Falling back to original subtitle track {tid}")

                for temp_file in [temp_extracted, temp_srt]:
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)

                    except OSError:
                        pass

        subtitle_tracks.append(str(tid))

    return subtitle_cmd_parts, subtitle_tracks, temp_files


def filter_and_remux(file_path, output_folder=None, preferences=None, extract_subtitles=False):
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

    print(f"DEBUG: Using audio languages: {allowed_audio_langs}")
    print(f"DEBUG: Using subtitle languages: {allowed_sub_langs}")

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
                f"⚠️ Could not use specified output folder, using default: {output_folder}")
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
                f"⚠️ Could not create output folder in {source_dir}, using default: {output_folder}")
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
    collected_subtitles = []

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
                print(
                    f"DEBUG: Removing audio track {tid} [{title}] because '{lang}' not in {allowed_audio_langs}")
                change_log.append(f"Removed audio track {tid} [{title}]")

        elif ttype == "subtitles":
            is_forced_original = forced and lang == original_subtitle_lang
            is_allowed_lang = lang in allowed_sub_langs
            is_forced_for_audio = forced and lang in allowed_audio_langs

            # Debug output for subtitle track collection
            print(
                f"DEBUG: Subtitle track {tid}: lang='{lang}', forced={forced}, track_name='{track_name}'")
            print(
                f"DEBUG: is_allowed_lang={is_allowed_lang}, is_forced_original={is_forced_original}, is_forced_for_audio={is_forced_for_audio}")
            print(
                f"DEBUG: allowed_sub_langs={allowed_sub_langs}, allowed_audio_langs={allowed_audio_langs}")

            if is_allowed_lang or is_forced_original or is_forced_for_audio:
                collected_subtitles.append({
                    "id": tid,
                    "lang": lang,
                    "forced": forced,
                    "hearing_impaired": hearing_impaired,
                    "track_name": track_name,
                    "title": title
                })
                print(
                    f"DEBUG: ✅ Collecting subtitle track {tid} [{title}] (track_name: '{track_name}')")
            else:
                print(
                    f"DEBUG: ❌ Skipping subtitle track {tid} [{title}] (track_name: '{track_name}')")
                change_log.append(f"Removed subtitle track {tid} [{title}]")

    deduplicated_subtitles = deduplicate_subtitles(collected_subtitles)

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
    print(f"Command: {' '.join(cmd)}")

    subprocess.run(cmd, check=True)

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
                print(f"💾 Saved subtitle file: {final_subtitle_name}")

                os.remove(saved_file)

            except Exception as e:
                print(
                    f"⚠️ Error saving subtitle file {os.path.basename(saved_file)}: {str(e)}")

    for temp_file in temp_subtitle_files:
        try:
            os.remove(temp_file)
            print(
                f"🧹 Cleaned up temporary file: {os.path.basename(temp_file)}")
        except OSError:
            pass

    log_file = os.path.join(output_folder, "mkv_process_log.txt")
    log_entry(os.path.basename(file_path), change_log, log_file)


def convert_subtitle_to_srt(subtitle_file, output_srt_file):
    """Convert various subtitle formats to SRT format"""
    try:
        print(f"🔍 Detecting format of {os.path.basename(subtitle_file)}")

        if is_srt_format(subtitle_file):
            try:
                import shutil
                shutil.copy2(subtitle_file, output_srt_file)
                process_srt_file_line_breaks(output_srt_file)

                return True, "Already in SRT format"
            except Exception as e:
                return False, f"Failed to copy SRT file: {str(e)}"

        ffmpeg_path = None
        possible_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
            "ffmpeg.exe",  # Windows
            "ffmpeg"  # Linux/Mac
        ]

        for path in possible_paths:
            try:
                result = subprocess.run([path, "-version"],
                                        capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    ffmpeg_path = path
                    print(f"✅ Found ffmpeg at: {path}")
                    break
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue

        if ffmpeg_path:
            cmd = [ffmpeg_path, "-i", subtitle_file,
                   "-c:s", "srt", output_srt_file, "-y"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                process_srt_file_line_breaks(output_srt_file)
                return True, "Converted using ffmpeg"
            else:
                print(f"⚠️ FFmpeg conversion failed: {result.stderr}")

        # Fallback
        try:
            # TTML/XML
            with open(subtitle_file, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = f.read(1000)

                is_ttml = (
                    '<tt ' in first_lines or
                    '<p ' in first_lines or
                    'xmlns' in first_lines or
                    '<?xml' in first_lines and '<p' in first_lines or
                    'begin=' in first_lines and '<p' in first_lines
                )

                if is_ttml:
                    conversion_success = convert_ttml_to_srt_basic(
                        subtitle_file, output_srt_file)

                    if conversion_success:
                        process_srt_file_line_breaks(output_srt_file)
                        return True, "Converted using basic TTML parser"

                elif '[Script Info]' in first_lines or 'Dialogue:' in first_lines:
                    conversion_success = convert_ass_to_srt_basic(
                        subtitle_file, output_srt_file)

                    if conversion_success:
                        process_srt_file_line_breaks(output_srt_file)
                        return True, "Converted using basic ASS parser"

        except Exception as e:
            print(f"⚠️ Basic conversion failed: {str(e)}")

        return False, "No suitable conversion tool found (FFmpeg recommended)"

    except Exception as e:
        return False, f"Conversion error: {str(e)}"


def convert_ass_to_srt_basic(ass_file, srt_file):
    """Basic ASS/SSA to SRT conversion"""
    try:
        with open(ass_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        lines = []
        seen_entries = set()

        for line in content.split('\n'):
            if line.startswith('Dialogue:'):
                parts = line.split(',', 9)

                if len(parts) >= 10:
                    start_time = parts[1].strip()
                    end_time = parts[2].strip()
                    text = parts[9].strip()

                    start_srt = convert_ass_time_to_srt(start_time)
                    end_srt = convert_ass_time_to_srt(end_time)

                    # Skip vector graphics lines
                    if any(pattern in text for pattern in [' m ', ' b ', ' l ', ' c ', ' z ', 'M ', 'L ', 'C ', 'Z ']):
                        continue

                    # Remove ASS formatting tags
                    text = re.sub(r'\{[^}]*\}', '', text)
                    text = text.replace('\\N', '\n')
                    text = text.replace('\\n', '\n')
                    text = text.strip()

                    if not text:
                        continue

                    text = break_long_subtitle_lines(text)

                    if len(set(text.replace('\n', '').replace(' ', ''))) <= 1:
                        continue
                    if len(text.replace('\n', '').replace(' ', '')) <= 2:
                        continue

                    # Create a unique key to avoid duplicates
                    entry_key = (start_srt, end_srt, text)

                    if entry_key not in seen_entries:
                        lines.append((start_srt, end_srt, text))
                        seen_entries.add(entry_key)

        if not lines:
            return False

        lines.sort(key=lambda x: x[0])

        with open(srt_file, 'w', encoding='utf-8') as f:
            for i, (start, end, text) in enumerate(lines, 1):
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")

        return True

    except Exception as e:
        print(f"⚠️ Basic ASS conversion failed: {str(e)}")
        return False


def convert_ass_time_to_srt(ass_time):
    """Convert ASS time format (0:00:00.00) to SRT format (00:00:00,000)"""
    try:
        # ASS format: "0:00:00.00"
        # SRT format: "00:00:00,000"

        parts = ass_time.split(':')

        if len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds_and_centiseconds = parts[2].split('.')
            seconds = int(seconds_and_centiseconds[0])

            if len(seconds_and_centiseconds) > 1:
                centiseconds = int(seconds_and_centiseconds[1])
                milliseconds = centiseconds * 10
            else:
                milliseconds = 0

            return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    except Exception:
        pass

    return "00:00:00,000"


def convert_ttml_to_srt_basic(ttml_file, srt_file):
    """Basic TTML/XML to SRT conversion using regex parsing"""
    try:
        with open(ttml_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        lines = []

        patterns = [
            r'<p[^>]*begin=["\'](.*?)["\'][^>]*end=["\'](.*?)["\'][^>]*>(.*?)</p>',
            r'<p[^>]*start=["\'](.*?)["\'][^>]*end=["\'](.*?)["\'][^>]*>(.*?)</p>',
            r'<p[^>]*begin=["\'](.*?)["\'][^>]*dur=["\'](.*?)["\'][^>]*>(.*?)</p>',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

            for match in matches:
                if len(match) >= 3:
                    time1, time2, text = match[0], match[1], match[2]

                    start_srt = convert_ttml_time_to_srt(time1.strip())
                    end_srt = convert_ttml_time_to_srt(time2.strip())

                    text = re.sub(r'<[^>]+>', '', text)
                    text = text.replace('&lt;', '<').replace(
                        '&gt;', '>').replace('&amp;', '&')
                    text = text.replace('\n', ' ').strip()
                    text = re.sub(r'\s+', ' ', text)

                    if text:
                        text = break_long_subtitle_lines(text)
                        lines.append((start_srt, end_srt, text))

            if matches:
                break

        if not lines:
            return False

        lines.sort(key=lambda x: x[0])

        with open(srt_file, 'w', encoding='utf-8') as f:
            for i, (start, end, text) in enumerate(lines, 1):
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")

        return True

    except Exception as e:
        print(f"⚠️ Basic TTML conversion failed: {str(e)}")
        return False


def convert_ttml_time_to_srt(ttml_time):
    """Convert TTML time format to SRT format"""
    try:
        # TTML supports multiple time formats:
        # - HH:MM:SS.mmm
        # - HH:MM:SS:frames
        # - seconds (e.g., "12.5s")
        # - milliseconds (e.g., "12500ms")

        if ttml_time.endswith('s'):
            if ttml_time.endswith('ms'):
                ms = int(float(ttml_time[:-2]))
            else:
                ms = int(float(ttml_time[:-1]) * 1000)

            hours = ms // 3600000
            ms %= 3600000
            minutes = ms // 60000
            ms %= 60000
            seconds = ms // 1000
            ms %= 1000

            return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"

        elif ':' in ttml_time:
            # HH:MM:SS.mmm or HH:MM:SS:frames format
            parts = ttml_time.split(':')

            if len(parts) >= 3:
                hours = int(parts[0])
                minutes = int(parts[1])

                seconds_part = parts[2]

                if '.' in seconds_part:
                    # HH:MM:SS.mmm format
                    sec_parts = seconds_part.split('.')
                    seconds = int(sec_parts[0])
                    milliseconds = int(sec_parts[1][:3].ljust(
                        3, '0'))  # Pad to 3 digits
                else:
                    seconds = int(seconds_part)
                    milliseconds = 0

                return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

        return "00:00:00,000"

    except Exception:
        return "00:00:00,000"


def extract_and_convert_subtitles(file_path, output_folder, subtitle_tracks):
    """Extract subtitles from MKV and convert non-SRT formats to SRT"""
    mkvextract_path = MKVMERGE_PATH.replace("mkvmerge", "mkvextract")

    if not os.path.exists(mkvextract_path):
        print(f"⚠️ mkvextract not found at {mkvextract_path}")
        return []

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    converted_subtitles = []

    for track in subtitle_tracks:
        track_id = track["id"]
        lang = track["lang"]
        forced = track.get("forced", False)
        hearing_impaired = track.get("hearing_impaired", False)
        track_name = track.get("track_name", "")

        name_based_forced = is_forced_subtitle_by_name(track_name)
        actual_forced = forced or name_based_forced

        if name_based_forced and not forced:
            print(
                f"🏷️ Additional forced detection by name in extraction: '{track_name}' (Track {track_id})")

        suffix = ""
        if actual_forced:
            suffix += ".forced"
        if hearing_impaired:
            suffix += ".sdh"

        temp_subtitle_file = os.path.join(
            output_folder, f"{base_name}.{lang}{suffix}.temp")
        final_srt_file = os.path.join(
            output_folder, f"{base_name}.{lang}{suffix}.srt")

        try:
            cmd = [mkvextract_path, "tracks", file_path,
                   f"{track_id}:{temp_subtitle_file}"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0 and os.path.exists(temp_subtitle_file):
                if temp_subtitle_file.endswith('.srt') or is_srt_format(temp_subtitle_file):
                    os.rename(temp_subtitle_file, final_srt_file)
                    converted_subtitles.append(final_srt_file)

                    print(f"✅ Extracted SRT subtitle: {final_srt_file}")
                else:
                    success, message = convert_subtitle_to_srt(
                        temp_subtitle_file, final_srt_file)

                    if success:
                        converted_subtitles.append(final_srt_file)
                        print(
                            f"✅ Converted subtitle to SRT: {final_srt_file} ({message})")
                    else:
                        print(
                            f"⚠️ Could not convert subtitle {temp_subtitle_file} to SRT: {message}")

                    try:
                        os.remove(temp_subtitle_file)
                    except OSError:
                        pass
            else:
                print(
                    f"⚠️ Failed to extract subtitle track {track_id}: {result.stderr}")

        except Exception as e:
            print(f"⚠️ Error processing subtitle track {track_id}: {str(e)}")

            for temp_file in [temp_subtitle_file, final_srt_file]:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except OSError:
                    pass

    return converted_subtitles


def is_srt_format(file_path):
    """Check if a subtitle file is in SRT format"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(2000)  # Read first 2000 characters

        srt_pattern = r'^\d+\s*\n\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}'

        has_srt_timecode = '-->' in content and ',' in content
        has_srt_numbering = bool(re.search(r'^\d+\s*$', content, re.MULTILINE))

        return bool(re.search(srt_pattern, content, re.MULTILINE)) or (has_srt_timecode and has_srt_numbering)

    except Exception:
        return False


def deduplicate_subtitles(subtitle_tracks):
    if not subtitle_tracks:
        return subtitle_tracks

    def extract_source(track_name):
        if not track_name:
            return None

        match = re.search(SOURCE_PATTERN, track_name)
        return match.group(1) if match else None

    lang_groups = {}

    for track in subtitle_tracks:
        lang = track["lang"]

        if lang not in lang_groups:
            lang_groups[lang] = []

        lang_groups[lang].append(track)

    result = []

    for lang, tracks in lang_groups.items():

        if len(tracks) <= 1:
            result.extend(tracks)

        normal_tracks = [t for t in tracks if not t["forced"]]
        forced_tracks = [t for t in tracks if t["forced"]]

        sources = {}
        unsourced_tracks = {"normal": [], "forced": []}
        all_tracks = normal_tracks + forced_tracks

        for track in all_tracks:
            source = extract_source(track.get("track_name", ""))

            if source:
                if source not in sources:
                    sources[source] = {"normal": [], "forced": []}

                if track["forced"]:
                    sources[source]["forced"].append(track)
                else:
                    sources[source]["normal"].append(track)

            else:
                if track["forced"]:
                    unsourced_tracks["forced"].append(track)
                else:
                    unsourced_tracks["normal"].append(track)

        best_source = None
        best_score = -1

        for source, tracks_by_type in sources.items():
            has_normal = len(tracks_by_type["normal"]) > 0
            has_forced = len(tracks_by_type["forced"]) > 0

            if has_normal and has_forced:
                score = 100
            elif has_normal:
                score = 50
            elif has_forced:
                score = 25
            else:
                score = 0

            if score > best_score:
                best_score = score
                best_source = source

        print(f"DEBUG: Best source: '{best_source}' with score: {best_score}")

        if best_source and best_source in sources:
            result.extend(sources[best_source]["normal"])
            result.extend(sources[best_source]["forced"])

        if unsourced_tracks["normal"]:
            if not (best_source and sources.get(best_source, {}).get("normal", [])):
                result.extend(unsourced_tracks["normal"])

        if unsourced_tracks["forced"]:
            result.extend(unsourced_tracks["forced"])

    return result


def main():
    """Main function to process all MKV files in the configured folder."""
    for file in os.listdir(MKV_FOLDER):
        if file.lower().endswith(".mkv"):
            full_path = os.path.normpath(os.path.join(MKV_FOLDER, file))
            print(f"Processing file: {full_path}")
            filter_and_remux(full_path)


if __name__ == "__main__":
    main()


def break_long_subtitle_lines(text, max_line_length=45):
    """
    Break long subtitle lines into multiple lines at optimal positions.

    Args:
        text: The subtitle text to process
        max_line_length: Maximum characters per line (default 45)

    Returns:
        Text with line breaks inserted at optimal positions
    """
    if not text or len(text) <= max_line_length:
        return text

    lines = text.split('\n')
    processed_lines = []

    for line in lines:
        if len(line) <= max_line_length:
            processed_lines.append(line)
            continue

        broken_lines = []
        remaining_text = line.strip()

        while len(remaining_text) > max_line_length:
            best_break = find_best_break_point(remaining_text, max_line_length)

            if best_break == -1:
                best_break = find_word_boundary(
                    remaining_text, max_line_length)

            if best_break == -1:
                best_break = max_line_length

            current_line = remaining_text[:best_break].strip()
            if current_line:
                broken_lines.append(current_line)

            remaining_text = remaining_text[best_break:].strip()

        if remaining_text:
            broken_lines.append(remaining_text)

        processed_lines.extend(broken_lines)

    return '\n'.join(processed_lines)


def find_best_break_point(text, max_length):
    """
    Find the best position to break a line, prioritizing natural pauses.

    Args:
        text: Text to analyze
        max_length: Maximum allowed length

    Returns:
        Position to break at, or -1 if no good break point found
    """
    if len(text) <= max_length:
        return -1

    break_chars = [
        # High priority: sentence endings and major pauses
        ('.', 2), ('!', 2), ('?', 2), (';', 2),
        # Medium priority: clause separators
        (',', 1), (':', 1),
        # Lower priority: conjunctions and prepositions
        (' and ', 1), (' or ', 1), (' but ', 1), (' so ', 1),
        (' with ', 1), (' for ', 1), (' to ', 1), (' in ', 1),
        # Lowest priority: any space
        (' ', 0)
    ]

    best_position = -1
    best_priority = -1

    search_text = text[:max_length + 1]

    for char, priority in break_chars:
        pos = search_text.rfind(char)

        while pos != -1:
            break_pos = pos + len(char)

            if (break_pos <= max_length and
                break_pos > best_position and
                break_pos >= 15 and
                    priority >= best_priority):
                best_position = break_pos
                best_priority = priority

            pos = search_text.rfind(char, 0, pos)

    return best_position if best_position > 0 else -1


def find_word_boundary(text, max_length):
    """
    Find the last word boundary within the maximum length.

    Args:
        text: Text to analyze
        max_length: Maximum allowed length

    Returns:
        Position of last word boundary, or -1 if none found
    """
    if len(text) <= max_length:
        return -1

    pos = text.rfind(' ', 0, max_length)
    return pos + 1 if pos != -1 else -1


def process_srt_file_line_breaks(srt_file_path):
    """
    Post-process an SRT file to ensure no lines are too long.

    Args:
        srt_file_path: Path to the SRT file to process
    """
    try:
        with open(srt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # SRT format: number, timecode, text, blank line
        srt_pattern = r'(\d+)\s*\n(\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3})\s*\n(.*?)(?=\n\s*\n|\n\s*\d+\s*\n|\Z)'
        matches = re.findall(srt_pattern, content, re.DOTALL)

        if not matches:
            return

        processed_entries = []

        for number, timecode, text in matches:
            processed_text = break_long_subtitle_lines(text.strip())
            processed_entries.append((number, timecode, processed_text))

        with open(srt_file_path, 'w', encoding='utf-8') as f:
            for i, (number, timecode, text) in enumerate(processed_entries):
                f.write(f"{number}\n")
                f.write(f"{timecode}\n")
                f.write(f"{text}\n")
                if i < len(processed_entries) - 1:
                    f.write("\n")

    except Exception as e:
        print(
            f"⚠️ Error processing SRT line breaks in {srt_file_path}: {str(e)}")
