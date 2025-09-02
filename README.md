# MKV Manager

A Python application for batch processing MKV video files with intelligent filename parsing, track filtering, and an desktop interface.

## Features

- **Intelligent File Management** - Automatically extracts series titles, season/episode numbers, and episode titles from various filename formats. Creates organized folder structures based on detected content.
- **Language-Based Track Filtering** - Configurable audio and subtitle track management based on language preferences. Removes unwanted tracks while preserving video quality to reduce file sizes.
- **Advanced Subtitle Processing** - Deduplicates subtitle tracks while preserving normal and forced subtitle pairs. Converts subtitles to SRT format for improved player compatibility.
- **Flexible Output Options** - Process files in-place, save to Downloads folder, or specify custom output directories with automatic folder organization.
- **Desktop GUI Interface** - Modern, user-friendly interface with drag-and-drop support, real-time progress tracking, and comprehensive settings management.
- **Command Line Support** - Automated batch processing capabilities for integration into workflows and scheduled tasks.

## Installation

### Prerequisites

- Python 3.7 or later
- [MKVToolNix](https://mkvtoolnix.download/) - Install mkvmerge command-line tools
#### GUI only:
- Pillow (recommended for full image/icon support in the GUI; the app will still run without it but with degraded image/icon features)
> [!NOTE] 
> The app uses Python's built-in `tkinter` for the desktop interface. If you encounter a "No module named 'tkinter'" error, install or enable Tcl/Tk for your Python distribution (for example via your OS package manager or by reinstalling Python with Tcl/Tk support).

### Setup

1. Clone or download the repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure the application:
   - Adjust default settings via the GUI settings panel

## Usage

### Desktop Application

Launch the graphical interface:
```bash
cd desktop
python main.py
```

The desktop application provides:

- **File Selection** - Browse and select MKV files or drag-and-drop files directly into the interface
- **Output Configuration** - Choose to process files in their original location, save to Downloads folder, or specify a custom output directory
- **Language Settings** - Configure preferred audio and subtitle languages with support for multiple language selections
- **Processing Options** - Enable subtitle extraction, conversion to SRT format, and other processing preferences
- **Real-time Monitoring** - Track processing progress with detailed status updates and logging

### Command Line

For automated batch processing:
```bash
python scripts/run_cleaner.py
```

This processes all MKV files in the configured default directory using saved preferences.

## How It Works

### File Processing Workflow

1. **Filename Analysis** - Automatically detects series information, season/episode numbers, and episode titles from various naming conventions
2. **Track Analysis** - Examines audio and subtitle tracks, identifying languages and track properties
3. **Language Filtering** - Removes or retains tracks based on configured language preferences
4. **Subtitle Processing** - Deduplicates similar subtitles while preserving forced/normal pairs, optionally converts to SRT format
5. **File Organization** - Creates organized folder structures and saves processed files with cleaned filenames

### Configuration Options

The application supports extensive customization through the settings interface:

- **Audio Languages** - Specify which audio languages to keep or remove
- **Subtitle Languages** - Configure subtitle language preferences and handling
- **File Paths** - Set default input/output directories and MKVToolNix installation path
- **Processing Behavior** - Control subtitle extraction, conversion options, and file organization

## Technical Details

### Supported Formats

- **Input**: MKV (Matroska) video files
- **Output**: Processed MKV files with optimized track selection
- **Subtitles**: Supports conversion to SRT format for improved compatibility

## Development and Building

### Project Structure

```
mkv-manager/
├── core/                 # Core processing logic
│   ├── analysis/         # Filename and track analysis
│   ├── config/           # Configuration management
│   ├── processing/       # MKV file operations
│   ├── subtitles/        # Subtitle processing
│   └── utils/            # Utility functions
├── desktop/              # Desktop GUI application
│   ├── controllers/      # Business logic controllers
│   ├── gui/              # User interface components
│   └── styles/           # UI styling and themes
├── scripts/              # Command-line scripts
└── packaging/            # Build and distribution tools
```

### Building from Source

To create a standalone executable:

#### Linux/macOS

1. Simple build using provided script:
   ```bash
   cd packaging
   python build_linux.py
   ```
   
   This script will:
   - Install PyInstaller if needed
   - Build a standalone executable
   - Create a desktop entry (Linux only)
   - Clean up build artifacts

#### Windows

1. Install build dependencies:
   ```bash
   pip install pyinstaller
   # Install NSIS from https://nsis.sourceforge.io/
   ```

2. Build installer:
   ```bash
   cd packaging
   python build.py
   ```

For detailed build instructions, see [`packaging/README.md`](packaging/README.md).

## License

This project is licensed under the terms specified in the LICENSE.txt file.
