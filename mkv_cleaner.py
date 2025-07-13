import os
import subprocess
from datetime import datetime
import re

MKVMERGE_PATH = r"/usr/bin/mkvmerge"
MKV_FOLDER = r"/path/to/mkv/source"
OUTPUT_FOLDER = os.path.join(MKV_FOLDER, "processed")

assert os.path.isfile(
    MKVMERGE_PATH), f"Cannot find mkvmerge at {MKVMERGE_PATH}"

LOG_FILE = os.path.join(OUTPUT_FOLDER, "mkv_process_log.txt")

ALLOWED_SUB_LANGS = {"eng", "ger", "kor", "gre"}
ALLOWED_AUDIO_LANGS = {"kor"}

DEFAULT_AUDIO_LANG = "kor"
DEFAULT_SUBTITLE_LANG = "eng"

ORIGINAL_AUDIO_LANG = "kor"
ORIGINAL_SUBTITLE_LANG = "kor"

LANG_TITLES = {
    "eng": "English",
    "ger": "German",
    "kor": "Korean",
    "jpn": "Japanese",
    "gre": "Greek",
    "und": "",
}

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def get_track_info(file_path):
    import json
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
                "lang": track["properties"].get("language", "und")
            })
        return tracks
    except json.JSONDecodeError:
        print(f"Error parsing JSON from mkvmerge output: {result.stdout}")
        return []


def log_entry(file_name, changes):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.now()}] {file_name}\n")
        for line in changes:
            f.write(f"  - {line}\n")


def extract_series_info(filename):
    base_name = os.path.splitext(filename)[0]

    season_episode_pattern = r'[Ss](\d+)[Ee](\d+)'
    season_episode_match = re.search(season_episode_pattern, base_name)

    if not season_episode_match:
        return None, None, None, None, None

    season_num = int(season_episode_match.group(1))
    episode_num = int(season_episode_match.group(2))
    season_episode_tag = f"S{season_num:02d}E{episode_num:02d}"

    season_start = season_episode_match.start()
    season_end = season_episode_match.end()

    # Extract series title (everything before SxxExx)
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

    # Extract episode title (everything after SxxExx until quality tags)
    episode_title = None
    remainder = base_name[season_end:]

    if remainder:
        # Remove leading delimiter if present
        if remainder.startswith('.') or remainder.startswith(' ') or remainder.startswith('-') or remainder.startswith('_'):
            remainder = remainder[1:]

        # Define quality tags that indicate where episode title ends
        quality_tags = [
            r'1080p', r'720p', r'480p', r'4K', r'UHD', r'HDR', r'WEB-DL', r'BluRay', r'BDRip', r'DVDRip',
            r'x264', r'x265', r'HEVC', r'AAC', r'DTS', r'AC3', r'5\.1', r'2\.0', r'\d+Kbps', r'MSubs',
            r'NF', r'AMZN', r'HULU', r'DSNP', r'HBO', r'PARAMOUNT', r'APPLE', r'PEACOCK', r'SHOWTIME',
            r'STARZ', r'VUDU', r'FANDANGO', r'ROKU', r'TUBI', r'CRACKLE', r'PLUTO', r'FREEVEE', r'REDBOX',
            r'Webrip', r'WebRip', r'WEBRip', r'10bit', r'8bit', r'EAC3', r'DDP5', r'APEX', r'WEB'
        ]

        # Look for patterns that indicate quality/technical info starts
        quality_patterns = [
            # Parentheses with quality info
            r'\([^)]*(?:WEB|1080p|720p|480p|x264|x265|AC3|DTS|AAC)\b[^)]*\)',
            # Brackets with quality info or hex
            r'\[[^]]*(?:WEB|1080p|720p|480p|x264|x265|AC3|DTS|AAC|[A-F0-9]{8})\b[^]]*\]',
            r'(?:^|\s|[._-])(' + '|'.join(quality_tags) +
            r')(?=\s|[._-]|$)',  # Direct quality tags
            r'\b\d{3,4}p\b',  # Resolution patterns like 1080p, 720p
            r'\bx26[45]\b',   # Codec patterns
            r'\b[A-F0-9]{8}\b'  # 8-character hex codes
        ]

        episode_title = remainder
        earliest_match = len(remainder)

        # Find the earliest quality indicator
        for pattern in quality_patterns:
            match = re.search(pattern, remainder, re.IGNORECASE)
            if match:
                earliest_match = min(earliest_match, match.start())

        if earliest_match < len(remainder):
            episode_title = remainder[:earliest_match]
        else:
            episode_title = remainder

        # Clean up episode title
        if episode_title:
            episode_title = episode_title.strip()

            # Convert dots, dashes, underscores to spaces
            episode_title = re.sub(r'[._-]+', ' ', episode_title)

            # Remove extra spaces
            episode_title = re.sub(r'\s+', ' ', episode_title).strip()

        # If episode title is empty or too short, set to None
        if not episode_title or len(episode_title) < 2:
            episode_title = None

    # Clean up series title
    series_title = re.sub(r'[\s\-_]+$', '', series_title)
    series_title = re.sub(r'\.{2,}$', '', series_title)

    if delimiter_used == '.':
        series_title = re.sub(r'(\w{3,})\.$', r'\1', series_title)

    abbreviations = {
        'K.': '###K_DOT###',
        'Dr.': '###DR_DOT###',
        'Mr.': '###MR_DOT###',
        'Mrs.': '###MRS_DOT###',
        'Ms.': '###MS_DOT###',
        'St.': '###ST_DOT###',
        'Jr.': '###JR_DOT###',
        'Sr.': '###SR_DOT###'
    }

    for abbrev, placeholder in abbreviations.items():
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

    for abbrev, placeholder in abbreviations.items():
        series_title = series_title.replace(placeholder, abbrev)

    # Remove remaining quality tags from series title
    quality_tags_series = [
        r'1080p', r'720p', r'480p', r'4K', r'UHD', r'HDR', r'WEB-DL', r'BluRay', r'BDRip', r'DVDRip',
        r'x264', r'x265', r'HEVC', r'AAC', r'DTS', r'AC3', r'5\.1', r'2\.0', r'\d+Kbps', r'MSubs',
        r'NF', r'AMZN', r'HULU', r'DSNP', r'HBO', r'PARAMOUNT', r'APPLE', r'PEACOCK', r'SHOWTIME',
        r'STARZ', r'VUDU', r'FANDANGO', r'ROKU', r'TUBI', r'CRACKLE', r'PLUTO', r'FREEVEE', r'REDBOX',
        r'Episode\s+\d+', r'Ep\s+\d+', r'Part\s+\d+'
    ]

    quality_pattern = r'\s*(' + '|'.join(quality_tags_series) + r').*$'
    series_title = re.sub(quality_pattern, '',
                          series_title, flags=re.IGNORECASE)

    # Remove years from series title (e.g., "2014", "2022")
    series_title = re.sub(r'\b\d{4}\b', '', series_title)

    series_title = re.sub(r'\s*-\s*[A-Z0-9]+$', '', series_title)
    series_title = re.sub(r'\s+', ' ', series_title).strip()

    return series_title, season_episode_tag, season_num, episode_num, episode_title


def filter_and_remux(file_path):
    base_name = os.path.splitext(os.path.basename(file_path))[0]

    series_title, season_episode_tag, season_num, episode_num, episode_title = extract_series_info(
        os.path.basename(file_path))

    if series_title and season_episode_tag:
        if episode_title:
            # Use actual episode title
            output_name = f"{series_title} - {season_episode_tag} - {episode_title}.mkv"
            title_for_mkv = f"{series_title} - {season_episode_tag} - {episode_title}"
        else:
            # Fallback to episode number format
            output_name = f"{series_title} - {season_episode_tag} - Episode #{season_num}.{episode_num}.mkv"
            title_for_mkv = f"{series_title} - {season_episode_tag} - Episode #{season_num}.{episode_num}"
    else:
        output_name = base_name + "_cleaned.mkv"
        title_for_mkv = base_name + "_cleaned"

    output_file = os.path.join(OUTPUT_FOLDER, output_name)
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
            if lang in ALLOWED_SUB_LANGS:
                subtitle_tracks.append(str(tid))
                is_default_sub = (lang == DEFAULT_SUBTITLE_LANG)
                is_original_sub = (lang == ORIGINAL_SUBTITLE_LANG)
                cmd += ["--default-track",
                        f"{tid}:{'yes' if is_default_sub else 'no'}"]
                cmd += ["--original-flag",
                        f"{tid}:{'yes' if is_original_sub else 'no'}"]
                cmd += ["--track-name", f"{tid}:{title}"]
                if is_default_sub:
                    change_log.append(
                        f"Set subtitle {tid} [{title}] as default")
                else:
                    change_log.append(f"Keep subtitle track {tid} [{title}]")
                if is_original_sub:
                    change_log.append(
                        f"Set subtitle {tid} [{title}] as original")
            else:
                change_log.append(f"Removed subtitle track {tid} [{title}]")

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
    log_entry(os.path.basename(file_path), change_log)


for file in os.listdir(MKV_FOLDER):
    if file.lower().endswith(".mkv"):
        full_path = os.path.normpath(os.path.join(MKV_FOLDER, file))
        print(f"Processing file: {full_path}")
        filter_and_remux(full_path)
