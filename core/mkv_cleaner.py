import os
import subprocess
import json
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


def get_track_info(file_path):
    file_path = os.path.normpath(file_path)
    cmd = [MKVMERGE_PATH, "-J", file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    try:
        data = json.loads(result.stdout)
        tracks = []

        for track in data.get("tracks", []):
            tracks.append({
                "id": track["id"],
                "type": track["type"],
                "lang": track["properties"].get("language", "und"),
                "forced": track["properties"].get("forced_track", False),
                "hearing_impaired": track["properties"].get("hearing_impaired_flag", False),
                "track_name": track["properties"].get("track_name", "")
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


def filter_and_remux(file_path):
    source_dir = os.path.dirname(file_path)

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
            if lang in ALLOWED_AUDIO_LANGS:
                audio_tracks.append(str(tid))
                is_def = (lang == DEFAULT_AUDIO_LANG)
                is_original = (lang == ORIGINAL_AUDIO_LANG)
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
            is_forced_original = forced and lang == ORIGINAL_SUBTITLE_LANG
            is_allowed_lang = lang in ALLOWED_SUB_LANGS

            if is_allowed_lang or is_forced_original:
                collected_subtitles.append({
                    "id": tid,
                    "lang": lang,
                    "forced": forced,
                    "hearing_impaired": hearing_impaired,
                    "track_name": track_name,
                    "title": title
                })
            else:
                change_log.append(f"Removed subtitle track {tid} [{title}]")

    deduplicated_subtitles = deduplicate_subtitles(collected_subtitles)

    for sub in deduplicated_subtitles:
        tid = sub["id"]
        lang = sub["lang"]
        forced = sub["forced"]
        hearing_impaired = sub["hearing_impaired"]
        track_name = sub["track_name"]
        title = sub["title"]

        subtitle_tracks.append(str(tid))
        is_default_sub = (lang == DEFAULT_SUBTITLE_LANG and not forced)
        is_original_sub = (lang == ORIGINAL_SUBTITLE_LANG)

        # Always use the standardized title from LANG_TITLES
        base_title = LANG_TITLES.get(lang, lang)

        # Build the final track title with appropriate suffixes
        if forced and hearing_impaired:
            track_title = f"{base_title} (Forced SDH)"
        elif forced:
            track_title = f"{base_title} (Forced)"
        elif hearing_impaired:
            track_title = f"{base_title} (SDH)"
        else:
            track_title = base_title

        cmd += ["--default-track",
                f"{tid}:{'yes' if is_default_sub else 'no'}"]
        cmd += ["--original-flag",
                f"{tid}:{'yes' if is_original_sub else 'no'}"]
        cmd += ["--track-name", f"{tid}:{track_title}"]

        if forced:
            cmd += ["--forced-track", f"{tid}:yes"]
        if hearing_impaired:
            cmd += ["--hearing-impaired-flag", f"{tid}:yes"]

        if is_default_sub:
            change_log.append(
                f"Set subtitle {tid} [{track_title}] as default")
        else:
            change_log.append(
                f"Keep subtitle track {tid} [{track_title}]")
        if is_original_sub:
            change_log.append(
                f"Set subtitle {tid} [{track_title}] as original")
        if forced:
            change_log.append(
                f"Preserved forced subtitle {tid} [{track_title}]")
        if hearing_impaired:
            change_log.append(
                f"Preserved SDH subtitle {tid} [{track_title}]")

        if track_name and '[' in track_name:
            original_source = track_name
            change_log.append(f"Deduplicated from source: {original_source}")

    if video_tracks:
        cmd += ["--video-tracks", ",".join(video_tracks)]
    if audio_tracks:
        cmd += ["--audio-tracks", ",".join(audio_tracks)]
    if subtitle_tracks:
        cmd += ["--subtitle-tracks", ",".join(subtitle_tracks)]

    cmd.append(file_path)

    print(f"\nProcessing: {file_path}")
    print(f"Command: {' '.join(cmd)}")

    subprocess.run(cmd, check=True)

    print(f"Saved: {output_file}")

    # Create log file in the same output folder
    log_file = os.path.join(output_folder, "mkv_process_log.txt")
    log_entry(os.path.basename(file_path), change_log, log_file)


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
            continue

        normal_tracks = [t for t in tracks if not t["forced"]]
        forced_tracks = [t for t in tracks if t["forced"]]

        sources = {}
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

        if best_source and best_source in sources:
            result.extend(sources[best_source]["normal"])
            result.extend(sources[best_source]["forced"])
        else:
            if normal_tracks:
                result.append(normal_tracks[0])
            if forced_tracks:
                result.append(forced_tracks[0])

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
