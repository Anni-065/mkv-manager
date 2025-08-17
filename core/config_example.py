import os

# Example configuration - Replace with your actual paths
MKVMERGE_PATH = r"/usr/bin/mkvmerge"  # Path to mkvmerge executable
MKV_FOLDER = r"/path/to/your/mkv/files"  # Source folder containing MKV files
# Output folder for processed files
OUTPUT_FOLDER = os.path.join(MKV_FOLDER, "processed")

# Language settings
ALLOWED_SUB_LANGS = {"eng", "ger", "kor", "gre"}
ALLOWED_AUDIO_LANGS = {"eng", "kor"}

DEFAULT_AUDIO_LANG = "kor"
DEFAULT_SUBTITLE_LANG = "eng"

ORIGINAL_AUDIO_LANG = "kor"
ORIGINAL_SUBTITLE_LANG = "kor"

# Subtitle extraction settings
EXTRACT_SUBTITLES = False  # Convert subtitles to SRT format during processing
SAVE_EXTRACTED_SUBTITLES = False  # Save extracted SRT files next to processed MKV
