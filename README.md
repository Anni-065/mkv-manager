# MKV Manager

A Python-based tool for batch processing MKV files with intelligent filename parsing, track filtering, and a modern web interface featuring advanced drag & drop support.

## Features

- **Intelligent Filename Parsing**: Automatically extracts series titles, season/episode numbers, and episode titles from various filename formats
- **Track Filtering**: Remove or keep specific audio and subtitle tracks based on language preferences
- **Modern Web Interface**: Flask-based web UI with responsive design and real-time processing feedback
- **Advanced Drag & Drop**: Full support for files AND folders - drag entire directories directly from your file manager
- **Destination-Based Processing**: Smart workflow that creates "processed" folders next to original files automatically
- **Quality Detection**: Recognizes quality indicators (1080p, WEB-DL, etc.) and separates them from episode titles
- **Real-Time Progress Tracking**: Live progress bars, file counts, and detailed processing logs
- **Flexible File Management**: Browse folders, drag individual files, or drop entire directory structures
- **Language Customization**: Web-based configuration for audio and subtitle language preferences

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
   - **Or configure everything through the web interface** - no manual file editing required!

## Usage

### Web Interface (Recommended)

1. Start the web interface:

   ```bash
   python web_interface.py
   ```

2. Open your browser and go to: `http://localhost:5000`

3. **Configure settings directly in the web interface** - edit paths and language preferences with a user-friendly form

4. Process your MKV files using multiple convenient methods

#### Advanced Drag & Drop Features

The web interface supports multiple ways to add files for processing:

**🗂️ Folder Drag & Drop (Full Support)**

- **Drag entire folders** directly from your file manager onto the drop zone
- **Automatic scanning** of all subdirectories for MKV files
- **Hierarchical display** showing folder structure and contained files
- **No browser limitations** - true folder support using modern web APIs

**📄 Individual File Support**

- **Drag individual files** from any location
- **Multi-select support** - select multiple files and drag them together
- **Mixed content** - combine files and folders in the same drop operation

**🔍 Integrated Folder Browser**

- **Click the drop zone** to open an integrated file browser
- **Navigate your entire system** to find MKV files
- **Folder selection** - choose entire directories with one click
- **Starts from your default destination** for quick access

**⚡ Smart Processing Workflow**

- **Destination-based processing** - creates "processed" folders automatically next to original files
- **No file moving required** - everything stays organized in its original location
- **Progress tracking** - live updates showing current file being processed

#### Processing Your Files

1. **Add files** using any of the drag & drop methods above
2. **Review the file list** - see exactly what will be processed
3. **Configure language settings** if needed (directly in the web interface)
4. **Click "Process Files"** - the button shows "Processing..." while working
5. **Monitor progress** - watch real-time progress bars and detailed logs
6. **Files are processed** in place with "processed" folders created automatically

### Command Line

1. Ensure you have configured your `config.py` file (see Configuration section above)

2. Run the script:
   ```bash
   python mkv_cleaner.py
   ```

## Configuration

### Web-Based Configuration (Recommended)

The easiest way to configure MKV Manager is through the web interface:

1. Start the web interface: `python web_interface.py`
2. Open `http://localhost:5000` in your browser
3. Click "⚙️ Edit Paths" to configure:
   - **Default Destination Folder**: Where processed files will be organized
   - **MKVToolNix Path**: Location of your mkvmerge executable
4. Use the main page to configure language settings:
   - **Allowed Audio/Subtitle Languages**: Which languages to keep in processed files
   - **Default Languages**: Preferred audio and subtitle tracks
   - **Original Languages**: Source language settings

### Manual Configuration (Alternative)

If you prefer manual configuration, create your personal `config.py` file by copying the example:

```bash
cp config_example.py config.py
```

Then edit `config.py` with your specific settings:

### Path Configuration

- `MKVMERGE_PATH`: Full path to mkvmerge executable
  - Windows: `r"C:\Program Files\MKVToolNix\mkvmerge.exe"`
  - Linux/macOS: `r"/usr/bin/mkvmerge"`
- `MKV_FOLDER`: Default destination folder (where processed files will be organized)
- `OUTPUT_FOLDER`: Automatically set to create "processed" folders next to original files

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

# Default destination folder (where the web interface will start browsing)
MKV_FOLDER = r"C:\Users\YourName\Downloads\complete"

# Output is automatically managed - processed files are created next to originals
OUTPUT_FOLDER = os.path.join(MKV_FOLDER, "processed")

# Language settings
ALLOWED_SUB_LANGS = {"eng", "ger", "kor", "gre"}
ALLOWED_AUDIO_LANGS = {"kor"}

DEFAULT_AUDIO_LANG = "kor"
DEFAULT_SUBTITLE_LANG = "eng"

ORIGINAL_AUDIO_LANG = "kor"
ORIGINAL_SUBTITLE_LANG = "kor"
```

## How It Works

### Processing Workflow

1. **File Discovery**: Add files through drag & drop, folder browsing, or direct file selection
2. **Automatic Organization**: Processed files are saved in "processed" folders created next to the original files
3. **Intelligent Parsing**: Filenames are automatically cleaned and standardized
4. **Track Filtering**: Audio and subtitle tracks are filtered based on your language preferences
5. **Quality Preservation**: Video quality and encoding are maintained while optimizing file structure

### File Organization

**Before Processing:**

```
/Your/Movie/Folder/
├── Movie.S01E01.Messy.Filename.1080p.WEB-DL.mkv
├── Movie.S01E02.Another.Episode.1080p.WEB-DL.mkv
└── Other files...
```

**After Processing:**

```
/Your/Movie/Folder/
├── Movie.S01E01.Messy.Filename.1080p.WEB-DL.mkv (original untouched)
├── Movie.S01E02.Another.Episode.1080p.WEB-DL.mkv (original untouched)
├── processed/
│   ├── Movie - S01E01 - Messy Filename.mkv (cleaned and filtered)
│   └── Movie - S01E02 - Another Episode.mkv (cleaned and filtered)
└── Other files...
```

**Benefits:**

- ✅ Original files are never modified or moved
- ✅ Processed files are clearly organized in dedicated folders
- ✅ Easy to compare before/after results
- ✅ Safe processing with automatic backup preservation

## Privacy & Security

This project is designed with privacy in mind:

- **Personal configuration files** (`config.py`) are automatically ignored by Git
- **No personal information** is hardcoded in the source files
- **Clean separation** between your personal settings and the public codebase
- **Example configuration** (`config_example.py`) shows the format without exposing real paths
- **Web-based configuration** allows setup without editing code files
- **Local processing only** - no data is sent to external servers

Your personal paths, usernames, and system-specific settings remain private and are never committed to the repository.

## Filename Parsing Examples

The tool intelligently parses various filename formats:

- `Show.Name.S01E01.Episode.Title.1080p.WEB-DL.mkv` → `Show Name - S01E01 - Episode Title.mkv`
- `Series.S02E05.(WEB-DL.1080p).mkv` → `Series - S02E05 - Episode #2.5.mkv`
- `Another.Show.S01E01.Pilot.BluRay.x264.mkv` → `Another Show - S01E01 - Pilot.mkv`

## Output Format

Processed files are saved with cleaned, standardized names in "processed" folders:

- **With episode title**: `Series Name - S01E01 - Episode Title.mkv`
- **Without episode title**: `Series Name - S01E01 - Episode #1.1.mkv`
- **Movie files**: `Movie Title (Year).mkv`

**Track Organization:**

- ✅ Only specified audio languages are kept
- ✅ Only specified subtitle languages are kept
- ✅ Default tracks are properly set
- ✅ Track titles are cleaned and standardized
- ✅ Original video quality is preserved

## Development

### Project Structure

```
mkv-manager/
├── web_interface.py          # Flask web application
├── mkv_cleaner.py           # Core MKV processing logic
├── config_example.py        # Configuration template
├── requirements.txt         # Python dependencies
├── static/
│   ├── app.js              # Main JavaScript with drag & drop
│   ├── file_browser_modal.js # File browser functionality
│   └── styles.css          # Modern responsive styling
├── templates/
│   ├── index.html          # Main interface
│   ├── config.html         # Configuration page
│   └── file_browser_modal.html # Reusable file browser
└── README.md               # This documentation
```

### Key Technologies

- **Backend**: Python 3.7+, Flask, MKVToolNix
- **Frontend**: Modern JavaScript ES6+, HTML5 File System Access API, CSS3 Grid/Flexbox
- **Features**: Real-time WebSocket-like updates, responsive design, drag & drop with full folder support

### Running Tests

```bash
python test_quality_detection.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Create your own `config.py` file for testing (copy from `config_example.py`)
5. Test your changes thoroughly (both web interface and command line)
6. Test drag & drop functionality with various file types and folder structures
7. Submit a pull request

**Note**: Never commit your personal `config.py` file - it's automatically ignored by Git.

## License

This project is licensed under the MIT License.

## Support

For issues or questions, please open an issue on GitHub.
