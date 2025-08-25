"""
Subtitle Conversion Module

This module handles conversion between different subtitle formats,
with a focus on converting various formats to SRT.
"""

import os
import subprocess
import shutil
import re
from ..utils.subprocess_utils import run_hidden
from ..utils.text_utils import break_long_subtitle_lines, process_srt_file_line_breaks


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


def convert_subtitle_to_srt(subtitle_file, output_srt_file):
    """Convert various subtitle formats to SRT format"""
    try:
        print(f"🔍 Detecting format of {os.path.basename(subtitle_file)}")

        if is_srt_format(subtitle_file):
            try:
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
                result = run_hidden(
                    [path, "-version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    ffmpeg_path = path
                    print(f"✅ Found ffmpeg at: {path}")
                    break
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue

        if ffmpeg_path:
            cmd = [ffmpeg_path, "-i", subtitle_file,
                   "-c:s", "srt", output_srt_file, "-y"]

            result = run_hidden(cmd, capture_output=True, text=True)

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
