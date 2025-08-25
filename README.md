# MKV Manager

A Python tool for batch processing MKV files with intelligent filename parsing, track filtering, and multiple interfaces.

## Features

- **Intelligent File Management** - Extracts series titles, season/episode numbers, and episode titles from various naming formats. Creates organized subfolders in the specified output path.
- **Language-Based Track Filtering** - Keep or remove audio/subtitle tracks based on configurable language preferences. Preserves video quality while reducing file sizes through track removal.
- **Subtitle Deduplication** - Automatically removes duplicate subtitles while preserving normal+forced pairs from the same source.
- **Subtitle Conversion** - Convert subtitles to .srt to improve compatibility with video players. Optionally extract and save .srt subtitles next to the video files for manual editing.
- **Multiple User Interfaces** - Choose from web UI with drag & drop, desktop GUI with full file control, or command line for automation.
- **Real-time Progress** - Track processing status and view detailed logs during batch operations.

## Quick Start

### 1. Install Dependencies

```bash
# Install MKVToolNix from https://mkvtoolnix.download/
pip install -r requirements.txt
```

### 2. Configure

Copy `core/config_example.py` to `core/config.py` and edit default values, or configure via web interface.

#### Configuration Options

- **Language Preferences** - Set default audio and subtitle languages (e.g., English, German, Japanese)
- **Output Paths** - Choose where processed files are saved
- **Processing Behavior** - Enable/disable subtitle extraction, set filename formats

### 3. Run

**Web Interface:**

```bash
cd web; python app.py
```

Visit http://localhost:5000 to access the drag & drop interface.

**Desktop GUI:**

```bash
cd desktop; start_desktop_gui.bat
```

Provides full file browser and output path control.

**Command Line:**

```bash
python scripts/run_cleaner.py
```

Processes files from configured default folder.

## How to Use

### Web Interface

1. **Configure Settings** - Set audio/subtitle language preferences and file paths
2. **Add Files** - Drag & drop MKV files or browse folders
3. **Review Selection** - Check parsed filenames and track information
4. **Process Files** - Start batch processing with real-time progress updates
5. **Download Results** - Processed files are organized and ready for manual download

### Desktop GUI

1. **Select Input Files** - Browse and select MKV files for processing
2. **Choose Output Location** - Select where processed files should be saved (same folder, Downloads, or custom path)
3. **Configure Languages** - Set preferred audio and subtitle languages
4. **Start Processing** - Monitor progress and view detailed processing logs
5. **Access Results** - Processed files are saved to your chosen location

### Command Line

1. **Run Script** - Execute `python scripts/run_cleaner.py`
2. **Batch Processing** - All MKV files in the configured folder are processed automatically
3. **Check Results** - Processed files appear in "processed" subfolders

## Interfaces

| Interface   | Best For                    | File Control                                   | Setup            |
| ----------- | --------------------------- | ---------------------------------------------- | ---------------- |
| **Web**     | Batch processing, modern UI | Limited (due to browser security restrictions) | None             |
| **Desktop** | Full file path control      | Complete                                       | Tkinter required |
| **Script**  | Automation, scheduled runs  | Same folder only                               | Manual config    |

### Interface-Specific Features

- **Web**: Drag & drop file upload, real-time progress bars, downloadable results, browser-based configuration
- **Desktop**: Native file dialogs, flexible output paths, detailed processing logs, offline operation
- **Script**: Automated batch processing, configurable via files, suitable for scheduled tasks

## Requirements

- Python 3.7+
- [MKVToolNix](https://mkvtoolnix.download/) (mkvmerge)
- Flask (web interface only)

## Building from Source

To create the installer:

1. **Install build dependencies:**

   ```bash
   pip install pyinstaller
   # Download and install NSIS from https://nsis.sourceforge.io/
   ```

2. **Build the installer:**

   ```bash
   # Windows
   packaging\build.bat

   # Cross-platform alternative (not tested)
   python packaging\build.py
   ```

For detailed build instructions, see [`packaging/README.md`](packaging/README.md).
