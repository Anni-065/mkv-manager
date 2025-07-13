# MKV Manager

A Python-based tool for batch processing MKV files with intelligent filename parsing, track filtering, and a user-friendly web interface.

## Features

- **Intelligent Filename Parsing**: Automatically extracts series titles, season/episode numbers, and episode titles from various filename formats
- **Track Filtering**: Remove or keep specific audio and subtitle tracks based on language preferences
- **Web Interface**: Modern Flask-based web UI for configuration and batch processing
- **Quality Detection**: Recognizes quality indicators (1080p, WEB-DL, etc.) and separates them from episode titles
- **Batch Processing**: Process multiple MKV files with progress tracking and logging

## Requirements

- Python 3.7+
- MKVToolNix (mkvmerge)
- Flask (for web interface)

## Installation

1. Install MKVToolNix:

   - Windows: Download from https://mkvtoolnix.download/
   - Linux: `sudo apt install mkvtoolnix` or equivalent
   - macOS: `brew install mkvtoolnix`

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure the application:
   - Copy `config_example.py` to `config.py`
   - Edit the paths and settings in `config.py` to match your system

## Usage

### Web Interface (Recommended)

1. Start the web interface:

   ```bash
   python web_interface.py
   ```

2. Open your browser and go to: `http://localhost:5000`

3. Configure paths and language settings

4. Process your MKV files through the web interface

### Command Line

1. Ensure you have configured your `config.py` file (see Configuration section above)

2. Run the script:
   ```bash
   python mkv_cleaner.py
   ```

## Configuration

Create your personal `config.py` file by copying the example:

```bash
cp config_example.py config.py
```

Then edit `config.py` with your specific settings:

### Path Configuration

- `MKVMERGE_PATH`: Full path to mkvmerge executable
  - Windows: `r"C:\Program Files\MKVToolNix\mkvmerge.exe"`
  - Linux/macOS: `r"/usr/bin/mkvmerge"`
- `MKV_FOLDER`: Source folder containing MKV files
- `OUTPUT_FOLDER`: Output folder for processed files (automatically set to `MKV_FOLDER/processed`)

### Language Settings

- `ALLOWED_SUB_LANGS`: Subtitle languages to keep (e.g., `{"eng", "ger", "kor"}`)
- `ALLOWED_AUDIO_LANGS`: Audio languages to keep (e.g., `{"kor"}`)
- `DEFAULT_AUDIO_LANG`: Default audio track language
- `DEFAULT_SUBTITLE_LANG`: Default subtitle track language
- `ORIGINAL_AUDIO_LANG`: Original audio language
- `ORIGINAL_SUBTITLE_LANG`: Original subtitle language

### Example Configuration

```python
import os

# Path to mkvmerge executable
MKVMERGE_PATH = r"C:\Program Files\MKVToolNix\mkvmerge.exe"  # Windows
# MKVMERGE_PATH = r"/usr/bin/mkvmerge"  # Linux/macOS

# Source folder containing MKV files
MKV_FOLDER = r"C:\Users\YourName\Downloads\complete"

# Output folder (automatically created)
OUTPUT_FOLDER = os.path.join(MKV_FOLDER, "processed")

# Language settings
ALLOWED_SUB_LANGS = {"eng", "ger", "kor", "gre"}
ALLOWED_AUDIO_LANGS = {"kor"}

DEFAULT_AUDIO_LANG = "kor"
DEFAULT_SUBTITLE_LANG = "eng"

ORIGINAL_AUDIO_LANG = "kor"
ORIGINAL_SUBTITLE_LANG = "kor"
```

**Important**: Your `config.py` file is automatically ignored by Git to protect your personal paths and settings.

## Privacy & Security

This project is designed with privacy in mind:

- **Personal configuration files** (`config.py`) are automatically ignored by Git
- **No personal information** is hardcoded in the source files
- **Clean separation** between your personal settings and the public codebase
- **Example configuration** (`config_example.py`) shows the format without exposing real paths

Your personal paths, usernames, and system-specific settings remain private and are never committed to the repository.

## Filename Parsing Examples

The tool intelligently parses various filename formats:

- `Show.Name.S01E01.Episode.Title.1080p.WEB-DL.mkv` → `Show Name - S01E01 - Episode Title.mkv`
- `Series.S02E05.(WEB-DL.1080p).mkv` → `Series - S02E05 - Episode #2.5.mkv`
- `Another.Show.S01E01.Pilot.BluRay.x264.mkv` → `Another Show - S01E01 - Pilot.mkv`

## Output Format

Processed files are saved with cleaned names:

- With episode title: `Series Name - S01E01 - Episode Title.mkv`
- Without episode title: `Series Name - S01E01 - Episode #1.1.mkv`

## Development

### Running Tests

```bash
python test_quality_detection.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Create your own `config.py` file for testing (copy from `config_example.py`)
5. Test your changes thoroughly
6. Submit a pull request

**Note**: Never commit your personal `config.py` file - it's automatically ignored by Git.

## License

This project is licensed under the MIT License.

## Support

For issues or questions, please open an issue on GitHub.
