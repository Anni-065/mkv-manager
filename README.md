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
   - Edit the paths and settings in `config.py`

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

1. Edit the configuration variables in `mkv_cleaner.py`:

   - `MKVMERGE_PATH`: Path to mkvmerge executable
   - `MKV_FOLDER`: Source folder containing MKV files
   - Language settings

2. Run the script:
   ```bash
   python mkv_cleaner.py
   ```

## Configuration

### Language Settings

- `ALLOWED_SUB_LANGS`: Subtitle languages to keep (e.g., `{"eng", "ger", "kor"}`)
- `ALLOWED_AUDIO_LANGS`: Audio languages to keep (e.g., `{"kor"}`)
- `DEFAULT_AUDIO_LANG`: Default audio track language
- `DEFAULT_SUBTITLE_LANG`: Default subtitle track language

### Path Configuration

- `MKVMERGE_PATH`: Path to mkvmerge executable
- `MKV_FOLDER`: Source folder containing MKV files
- `OUTPUT_FOLDER`: Output folder for processed files (defaults to `MKV_FOLDER/processed`)

## Filename Parsing Examples

The tool intelligently parses various filename formats:

- `Show.Name.S01E01.Episode.Title.1080p.WEB-DL.mkv` → `Show Name - S01E01 - Episode Title.mkv`
- `Series.S02E05.(WEB-DL.1080p).mkv` → `Series - S02E05 - Episode #2.5.mkv`
- `Another.Show.S01E01.Pilot.BluRay.x264.mkv` → `Another Show - S01E01 - Pilot.mkv`

## Output Format

Processed files are saved with cleaned names:

- With episode title: `Series Name - S01E01 - Episode Title.mkv`
- Without episode title: `Series Name - S01E01 - Episode #1.1.mkv`

## Git Hooks - Automatic Privacy Protection

This project includes automatic sanitization hooks that protect your personal information when committing to GitHub!

### 🎯 How Git Hooks Work

1. **Before each commit** (pre-commit hook):

   - Automatically backs up your original files
   - Sanitizes all personal information (paths, usernames, etc.)
   - Stages the sanitized files for commit

2. **After each commit** (post-commit hook):
   - Automatically restores your original files
   - Your working directory keeps your personal settings

### 🔧 Setting Up Git Hooks

Install the Git hooks to enable automatic sanitization:

```bash
python setup_git_hooks.py
```

Options available:

- **Install Git hooks**: Set up automatic sanitization
- **Uninstall Git hooks**: Remove automatic sanitization
- **Test hooks**: Verify everything is working
- **Show status**: Check current hook installation

### 📁 What Gets Automatically Sanitized

The hooks automatically replace:

- Your personal paths → Generic paths (`/path/to/mkv-source`)
- Your username → `user`
- Secret keys → Placeholder text
- Personal folder names → Generic names

### 🚀 Using Git with Hooks

Once installed, use Git normally - hooks run automatically:

```bash
# Add files to staging
git add .

# Commit - hooks will run automatically!
git commit -m "Add new feature"

# Push to GitHub - only sanitized files are in the repo
git push origin main
```

### ✅ Benefits of Git Hooks

- **Zero effort**: No need to remember to sanitize files
- **Safe commits**: Never accidentally commit personal information
- **Seamless workflow**: Git works exactly as before
- **Automatic restoration**: Your working files keep personal settings
- **Version control friendly**: Clean, shareable repository

### 🛡️ Safety Features

- **Automatic backups**: Original files are always backed up
- **Error handling**: Hooks gracefully handle errors
- **Restoration**: Files are automatically restored after commits
- **Manual override**: You can still use manual sanitization if needed

### 🔄 Manual Sanitization Control

If you need manual control without hooks:

```bash
# Manually sanitize (creates backups)
python sanitize_for_github.py

# Manually restore from backups
python sanitize_for_github.py
```

### 🧪 Testing Git Hooks

To verify hooks are working:

1. Make a small change to a file
2. Run `git add .` and `git commit -m "test"`
3. Check that files were sanitized during commit
4. Verify files were restored after commit

## Development

### Running Tests

```bash
python test_quality_detection.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. **Install Git hooks** (recommended):
   ```bash
   python setup_git_hooks.py
   ```
   Or manually run sanitization before committing:
   ```bash
   python sanitize_for_github.py
   ```
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues or questions, please open an issue on GitHub.
