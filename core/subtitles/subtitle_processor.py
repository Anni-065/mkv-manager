"""
Subtitle Processing Module

This module handles subtitle deduplication, filtering, and processing
for MKV files, including both systematic processing and conversion workflows.
"""

import os
import re
from ..config.constants import LANG_TITLES, SOURCE_PATTERN
from .subtitle_converter import (
    is_srt_format, convert_subtitle_to_srt
)
from ..utils.text_utils import process_srt_file_line_breaks
from ..utils.subprocess_utils import run_hidden
from ..config import MKVMERGE_PATH


def deduplicate_subtitles(subtitle_tracks):
    """
    Deduplicate subtitle tracks by language, preferring tracks from the best source.
    """
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
            continue

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
                    f"Keeping forced subtitle track {sub['id']} [{lang}] (in {' and '.join(reason)})")
            else:
                print(
                    f"Removing forced subtitle track {sub['id']} [{lang}] (not in allowed audio or subtitle languages)")
        else:
            if lang in allowed_sub_langs:
                allowed_subtitles.append(sub)
                print(
                    f"Keeping non-forced subtitle track {sub['id']} [{lang}] (in allowed subtitle languages)")
            else:
                print(
                    f"Removing non-forced subtitle track {sub['id']} [{lang}] (not in allowed subtitle languages)")

    print(f"Kept {len(allowed_subtitles)} subtitle tracks after filtering")

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
            print(f"Processing subtitle track {tid} [{lang}]...")

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

                result_extract = run_hidden(
                    extract_cmd,
                    capture_output=True,
                    text=True
                )

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
                            f"Already SRT format: {os.path.basename(final_srt)}")
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
                                f"Converted to SRT: {os.path.basename(final_srt)} ({conversion_msg})")
                        else:
                            print(
                                f"ERR: Could not convert to SRT: {conversion_msg}")
                            result["conversion_success"] = False

                        try:
                            os.remove(temp_extracted)
                        except OSError:
                            pass
                else:
                    print(f"ERR: Failed to extract subtitle track {tid}")
                    result["conversion_success"] = False

            except Exception as e:
                print(f"ERR: Error processing subtitle track {tid}: {str(e)}")
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
                f"Added subtitle: {track_title} -> {os.path.basename(result['file_path'])}")
        else:
            original_track_id = result["original_id"]
            print(
                f"Keeping original subtitle track {original_track_id} [{track_title}]")

    original_subtitle_track_ids = []
    original_track_metadata = {}

    for result in final_subtitles:
        if not result["file_path"]:
            original_track_id = result["original_id"]
            original_subtitle_track_ids.append(str(original_track_id))

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

            original_track_metadata[str(original_track_id)] = {
                'language': lang,
                'title': track_title,
                'default': is_default_sub,
                'forced': forced,
                'hearing_impaired': hearing_impaired,
                'original': is_original_sub
            }

    return processed_subtitles, temp_files, saved_subtitle_files, original_subtitle_track_ids, original_track_metadata
