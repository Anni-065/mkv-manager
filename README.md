# MKV Manager

A modular Python tool for batch processing MKV files with intelligent filename parsing, track filtering, and a modern Flask web interface.

## Features

- **🎯 Intelligent Filename Parsing** - Extracts series titles, season/episode numbers, and episode titles from various formats
- **🔄 Track Filtering** - Keep or remove audio/subtitle tracks based on language preferences
- **🧹 Subtitle Deduplication** - Automatically removes duplicate subtitles, preferring same-source normal+forced pairs
- **🌐 Modern Web Interface** - Flask-based UI with drag & drop support and real-time progress
- **⚙️ Web Configuration** - Configure paths and language settings directly in the browser
- **📦 Modular Architecture** - Core logic separated from web interface for better maintainability
- **🗂️ Smart Organization** - Creates "processed" folders next to originals automatically

## Quick Start

### 1. Install Dependencies

```bash
# Install MKVToolNix
Windows: Download from https://mkvtoolnix.download/
# Linux: sudo apt install mkvtoolnix
# macOS: brew install mkvtoolnix

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure

- Copy `core/config_example.py` to `core/config.py` and edit paths
- _Or_ configure everything through the web interface

### 3. Run

**Web Interface (Recommended):**

```bash
cd web/
python app.py
```

**Standalone Script:**

```bash
python scripts/run_cleaner.py
```

**Core Module:**

```python
from core.mkv_cleaner import filter_and_remux
filter_and_remux("path/to/video.mkv")
```

## How It Works

### Processing Workflow

1. **File Discovery** - Add files via drag & drop or folder browsing
2. **Filename Parsing** - Extract series info and clean quality tags
3. **Track Filtering** - Keep only specified audio/subtitle languages
4. **Smart Organization** - Save processed files in "processed" subfolders

### File Organization

```
/Your/Series/Folder/
├── Series.S01E01.Messy.Filename.1080p.WEB-DL.mkv (original)
└── processed/
    └── Series - S01E01 - Messy Filename.mkv (cleaned)
```

### Filename Examples

- `Show.Name.S01E01.Episode.Title.1080p.WEB-DL.mkv` → `Show Name - S01E01 - Episode Title.mkv`
- `Series.S02E05.(WEB-DL.1080p).mkv` → `Series - S02E05 - Episode #2.5.mkv`

## Configuration

### Web Configuration (Recommended)

1. Start the web interface: `cd web/ && python app.py`
2. Click "⚙️ Edit Paths" to configure mkvmerge path and default folder
3. Use the main page to set language preferences

### Manual Configuration

Copy `core/config_example.py` to `core/config.py` and edit the key settings:

- `MKVMERGE_PATH` - Path to mkvmerge executable
- `MKV_FOLDER` - Default folder for browsing
- `ALLOWED_SUB_LANGS` / `ALLOWED_AUDIO_LANGS` - Language preferences

## Testing

```bash
# Run individual tests (from project root)
python -m tests.test_simplified_titles
python -m tests.test_subtitle_deduplication
python -m tests.test_quality_detection
```

## Project Structure

```
mkv-manager/
├── core/                    # Core processing logic (standalone)
├── web/                     # Flask web interface
├── tests/                   # Test suite
├── scripts/                 # Utility scripts
└── requirements.txt
```

## License

MIT License - Local processing only, no data sent to external servers.

## Requirements

- Python 3.7+
- [MKVToolNix](https://mkvtoolnix.download/) (mkvmerge)
- Flask (for web interface)
