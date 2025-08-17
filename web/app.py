from core.constants import LANG_TITLES
import shutil
from datetime import datetime
import threading
import subprocess
import re
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sys
import os
import importlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

mkv_cleaner = importlib.import_module('core.mkv_cleaner')
extract_series_info = mkv_cleaner.extract_series_info
get_track_info = mkv_cleaner.get_track_info
filter_and_remux = mkv_cleaner.filter_and_remux

# Import language titles from constants

try:
    from core.config import *
    print("✅ Web interface using config.py")
except ImportError:
    try:
        from core.config_example import *
        print("⚠️ Web interface using config_example.py - Consider creating config.py")
    except ImportError:
        print("❌ No configuration file found!")
        raise ImportError(
            "Please create config.py or ensure config_example.py exists")

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

config = {
    'MKVMERGE_PATH': MKVMERGE_PATH,
    'MKV_FOLDER': MKV_FOLDER,
    'ALLOWED_SUB_LANGS': list(ALLOWED_SUB_LANGS),
    'ALLOWED_AUDIO_LANGS': list(ALLOWED_AUDIO_LANGS),
    'DEFAULT_AUDIO_LANG': DEFAULT_AUDIO_LANG,
    'DEFAULT_SUBTITLE_LANG': DEFAULT_SUBTITLE_LANG,
    'ORIGINAL_AUDIO_LANG': ORIGINAL_AUDIO_LANG,
    'ORIGINAL_SUBTITLE_LANG': ORIGINAL_SUBTITLE_LANG,
    'EXTRACT_SUBTITLES': globals().get('EXTRACT_SUBTITLES', False),
    'SAVE_EXTRACTED_SUBTITLES': globals().get('SAVE_EXTRACTED_SUBTITLES', False),
    'LANG_TITLES': LANG_TITLES,
    'AVAILABLE_AUDIO_LANGS': {lang: LANG_TITLES.get(lang, lang) for lang in ALLOWED_AUDIO_LANGS},
    'AVAILABLE_SUB_LANGS': {lang: LANG_TITLES.get(lang, lang) for lang in ALLOWED_SUB_LANGS},
    'ALL_CONFIGURED_LANGS': {lang: LANG_TITLES.get(lang, lang) for lang in ALLOWED_AUDIO_LANGS.union(ALLOWED_SUB_LANGS)}
}

processing_status = {
    'is_running': False,
    'current_file': '',
    'progress': 0,
    'total_files': 0,
    'log': []
}


def update_mkv_cleaner_config():
    """Update the mkv_cleaner module with current config"""

    mkv_cleaner.MKVMERGE_PATH = config['MKVMERGE_PATH']
    mkv_cleaner.MKV_FOLDER = config['MKV_FOLDER']
    mkv_cleaner.OUTPUT_FOLDER = os.path.join(config['MKV_FOLDER'], "processed")
    mkv_cleaner.ALLOWED_SUB_LANGS = set(config['ALLOWED_SUB_LANGS'])
    mkv_cleaner.ALLOWED_AUDIO_LANGS = set(config['ALLOWED_AUDIO_LANGS'])
    mkv_cleaner.DEFAULT_AUDIO_LANG = config['DEFAULT_AUDIO_LANG']
    mkv_cleaner.DEFAULT_SUBTITLE_LANG = config['DEFAULT_SUBTITLE_LANG']
    mkv_cleaner.ORIGINAL_AUDIO_LANG = config['ORIGINAL_AUDIO_LANG']
    mkv_cleaner.ORIGINAL_SUBTITLE_LANG = config['ORIGINAL_SUBTITLE_LANG']
    mkv_cleaner.LOG_FILE = os.path.join(
        mkv_cleaner.OUTPUT_FOLDER, "mkv_process_log.txt")


@app.route('/')
def index():
    return render_template('index.html', config=config)


@app.route('/config', methods=['GET', 'POST'])
def configure():
    if request.method == 'POST':
        config['MKVMERGE_PATH'] = request.form.get(
            'mkvmerge_path', config['MKVMERGE_PATH'])
        config['MKV_FOLDER'] = request.form.get(
            'mkv_folder', config['MKV_FOLDER'])

        flash('Path configuration updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('config.html', config=config)


@app.route('/files')
def list_files():
    """List MKV files in the configured folder or custom path"""
    try:
        custom_path = request.args.get('path')
        folder_path = custom_path if custom_path else config['MKV_FOLDER']

        if not os.path.exists(folder_path):
            error_msg = f"Folder does not exist: {folder_path}"
            return jsonify({'error': error_msg})

        files = []
        for file in os.listdir(folder_path):
            if file.lower().endswith('.mkv'):
                file_path = os.path.join(folder_path, file)
                file_info = {
                    'name': file,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                }

                series_info = extract_series_info(file)
                if series_info[0]:
                    file_info['series_title'] = series_info[0]
                    file_info['season_episode'] = series_info[1]
                else:
                    file_info['series_title'] = 'Unknown'
                    file_info['season_episode'] = 'N/A'

                files.append(file_info)

        return jsonify({'files': files, 'folder_path': folder_path})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/process', methods=['POST'])
def process_files():
    """Start processing MKV files"""
    if processing_status['is_running']:
        return jsonify({'error': 'Processing is already running'})

    request_data = request.get_json() or {}
    custom_path = request_data.get('custom_path')
    source_folder = custom_path if custom_path else config['MKV_FOLDER']

    if not os.path.exists(source_folder):
        return jsonify({'error': f'Source folder does not exist: {source_folder}'})

    processing_status['is_running'] = True
    processing_status['log'] = []
    processing_status['progress'] = 0
    processing_status['current_file'] = ''

    processing_status['log'].append("🚀 Starting processing...")
    if custom_path:
        processing_status['log'].append(
            f"📁 Scanning custom path: {custom_path}")
    else:
        processing_status['log'].append(
            f"📁 Scanning default path: {config['MKV_FOLDER']}")

    update_mkv_cleaner_config()

    def process_thread():
        try:
            processing_status['log'].append("🔍 Searching for MKV files...")
            mkv_files = [f for f in os.listdir(
                source_folder) if f.lower().endswith('.mkv')]
            processing_status['total_files'] = len(mkv_files)

            if len(mkv_files) == 0:
                processing_status['log'].append(
                    "⚠️ No MKV files found in the specified folder")
                return

            processing_status['log'].append(
                f"✅ Found {len(mkv_files)} MKV files to process")

            for i, file in enumerate(mkv_files):
                processing_status['current_file'] = file
                processing_status['progress'] = i

                try:
                    full_path = os.path.normpath(
                        os.path.join(source_folder, file))
                    processing_status['log'].append(f"Processing: {file}")
                    filter_and_remux(full_path, preferences=config)
                    processing_status['log'].append(f"✓ Completed: {file}")
                except Exception as e:
                    processing_status['log'].append(
                        f"✗ Error processing {file}: {str(e)}")

            processing_status['progress'] = len(mkv_files)
            processing_status['current_file'] = ''
            processing_status['log'].append("🎉 All files processed!")

        except Exception as e:
            processing_status['log'].append(f"✗ Fatal error: {str(e)}")
        finally:
            processing_status['is_running'] = False

    thread = threading.Thread(target=process_thread)
    thread.daemon = True
    thread.start()

    return jsonify({'success': True, 'message': 'Processing started'})


@app.route('/status')
def get_status():
    """Get current processing status"""
    return jsonify(processing_status)


@app.route('/stop', methods=['POST'])
def stop_processing():
    """Stop processing (this is a simple implementation)"""
    processing_status['is_running'] = False
    processing_status['log'].append("Processing stopped by user")
    return jsonify({'success': True, 'message': 'Processing stopped'})


@app.route('/browse')
def browse_files():
    """Browse file system for folder selection"""
    path = request.args.get('path', '')

    if not path:
        path = os.path.expanduser('~')

    path = os.path.normpath(path)

    if not os.path.exists(path):
        path = os.path.expanduser('~')

    try:
        items = []

        if path != os.path.dirname(path):
            parent = os.path.dirname(path)
            items.append({
                'name': '.. (Back)',
                'path': parent,
                'type': 'parent',
                'icon': '⬅️'
            })

        for item in os.listdir(path):
            if item.startswith('.'):
                continue

            item_path = os.path.join(path, item)
            try:
                if os.path.isdir(item_path):
                    items.append({
                        'name': item,
                        'path': item_path,
                        'type': 'directory',
                        'icon': '📁'
                    })
                elif item.lower().endswith('.mkv'):
                    items.append({
                        'name': item,
                        'path': item_path,
                        'type': 'mkv',
                        'icon': '🎬'
                    })
            except PermissionError:
                continue

        items.sort(key=lambda x: (
            x['type'] != 'directory', x['type'] != 'parent', x['name'].lower()))

        return jsonify({
            'current_path': path,
            'items': items
        })

    except Exception as e:
        return jsonify({'error': f'Error browsing path: {str(e)}'})


@app.route('/open_explorer', methods=['POST'])
def open_explorer():
    """Open Windows Explorer at the specified path"""
    path = request.json.get('path', '')

    if not path:
        path = config['MKV_FOLDER']

    path = os.path.normpath(path)

    try:
        if not os.path.exists(path):
            return jsonify({'error': 'Path does not exist'})

        result = subprocess.run(
            ['explorer', path], capture_output=True, text=True)

        return jsonify({'success': True, 'message': f'Opened Explorer at: {path}'})

    except Exception as e:
        return jsonify({'error': f'Error opening Explorer: {str(e)}'})


@app.route('/get_drives')
def get_drives():
    """Get available drives on Windows"""
    try:
        drives = []
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            drive_path = f'{letter}:\\'
            if os.path.exists(drive_path):
                try:
                    total, used, free = shutil.disk_usage(drive_path)
                    drives.append({
                        'letter': letter,
                        'path': drive_path,
                        'total': total,
                        'free': free,
                        'used': used
                    })
                except:
                    drives.append({
                        'letter': letter,
                        'path': drive_path,
                        'total': 0,
                        'free': 0,
                        'used': 0
                    })

        return jsonify({'drives': drives})

    except Exception as e:
        return jsonify({'error': f'Error getting drives: {str(e)}'})


@app.route('/get_user_home')
def get_user_home():
    """Get the current user's home directory"""
    try:
        home_path = os.path.expanduser('~')
        return jsonify({'home_path': home_path})
    except Exception as e:
        return jsonify({'error': f'Error getting user home: {str(e)}'})


@app.route('/update_settings', methods=['POST'])
def update_settings():
    """Update language settings from the home page"""
    if request.method == 'POST':
        config['ALLOWED_SUB_LANGS'] = request.form.getlist('allowed_sub_langs')
        config['ALLOWED_AUDIO_LANGS'] = request.form.getlist(
            'allowed_audio_langs')
        config['DEFAULT_AUDIO_LANG'] = request.form.get(
            'default_audio_lang', config['DEFAULT_AUDIO_LANG'])
        config['DEFAULT_SUBTITLE_LANG'] = request.form.get(
            'default_subtitle_lang', config['DEFAULT_SUBTITLE_LANG'])
        config['ORIGINAL_AUDIO_LANG'] = request.form.get(
            'original_audio_lang', config['ORIGINAL_AUDIO_LANG'])
        config['ORIGINAL_SUBTITLE_LANG'] = request.form.get(
            'original_subtitle_lang', config['ORIGINAL_SUBTITLE_LANG'])

        # Handle subtitle processing options
        config['EXTRACT_SUBTITLES'] = 'extract_subtitles' in request.form
        config['SAVE_EXTRACTED_SUBTITLES'] = 'save_extracted_subtitles' in request.form

        # Update the language dictionaries based on new settings
        config['AVAILABLE_AUDIO_LANGS'] = {lang: LANG_TITLES.get(
            lang, lang) for lang in config['ALLOWED_AUDIO_LANGS']}
        config['AVAILABLE_SUB_LANGS'] = {lang: LANG_TITLES.get(
            lang, lang) for lang in config['ALLOWED_SUB_LANGS']}
        config['ALL_CONFIGURED_LANGS'] = {lang: LANG_TITLES.get(lang, lang) for lang in set(
            config['ALLOWED_AUDIO_LANGS'] + config['ALLOWED_SUB_LANGS'])}

        flash('Settings updated successfully!', 'success')
        return redirect(url_for('index'))


@app.route('/process_dropped_files', methods=['POST'])
def process_dropped_files():
    """Process files that were dropped onto the drag & drop zone"""
    if processing_status['is_running']:
        return jsonify({'error': 'Processing is already running'})

    try:
        if 'files' in request.get_json() if request.is_json else False:
            data = request.get_json()
            file_paths = data['files']

            return process_files_from_paths(file_paths)
        else:
            return process_uploaded_files()

    except Exception as e:
        return jsonify({'error': f'Error processing dropped files: {str(e)}'})


def process_files_from_paths(file_paths):
    """Process files from their original file paths (folder browsing)"""
    if not file_paths:
        return jsonify({'error': 'No valid file paths provided'})

    valid_files = []
    for file_path in file_paths:
        if os.path.exists(file_path) and file_path.lower().endswith('.mkv'):
            valid_files.append(file_path)

    if not valid_files:
        return jsonify({'error': 'No valid MKV files found'})

    update_mkv_cleaner_config()

    def process_thread():
        try:
            processing_status['is_running'] = True
            processing_status['log'] = []
            processing_status['progress'] = 0
            processing_status['total_files'] = len(valid_files)

            files_by_directory = {}
            for file_path in valid_files:
                directory = os.path.dirname(file_path)
                if directory not in files_by_directory:
                    files_by_directory[directory] = []
                files_by_directory[directory].append(file_path)

            processing_status['log'].append(
                f"📁 Processing {len(valid_files)} files from {len(files_by_directory)} directories")

            processed_count = 0
            for directory, files_in_dir in files_by_directory.items():
                for file_path in files_in_dir:
                    filename = os.path.basename(file_path)
                    processing_status['current_file'] = filename
                    processing_status['progress'] = processed_count

                    try:
                        processing_status['log'].append(
                            f"Processing: {filename}")

                        # The filter_and_remux function now handles output folder automatically
                        filter_and_remux(file_path, preferences=config)
                        processing_status['log'].append(
                            f"✓ Completed: {filename}")
                    except Exception as e:
                        processing_status['log'].append(
                            f"✗ Error processing {filename}: {str(e)}")

                    processed_count += 1

            processing_status['progress'] = len(valid_files)
            processing_status['current_file'] = ''
            processing_status['log'].append("🎉 All files processed!")

        except Exception as e:
            processing_status['log'].append(f"✗ Fatal error: {str(e)}")
        finally:
            processing_status['is_running'] = False

    thread = threading.Thread(target=process_thread)
    thread.daemon = True
    thread.start()

    return jsonify({'success': True, 'message': 'File processing started'})


def process_uploaded_files():
    """Process files that were actually uploaded (drag & drop)"""
    processing_status['is_running'] = True
    processing_status['log'] = []
    processing_status['progress'] = 0
    processing_status['current_file'] = ''

    processing_status['log'].append("🚀 Starting file upload processing...")
    processing_status['log'].append("📁 Analyzing uploaded files...")

    # Create temporary files for processing
    temp_files = []
    file_names = []

    # Create temp directory for processing
    temp_dir = os.path.join(config['MKV_FOLDER'], 'temp_processing')
    os.makedirs(temp_dir, exist_ok=True)

    # Save files temporarily for processing
    for key in request.files:
        file = request.files[key]
        if file and file.filename.lower().endswith('.mkv'):
            filename = os.path.basename(file.filename)
            temp_file_path = os.path.join(temp_dir, filename)
            file.save(temp_file_path)
            temp_files.append(temp_file_path)
            file_names.append(filename)

    if not temp_files:
        processing_status['is_running'] = False
        return jsonify({'error': 'No valid MKV files were uploaded'})

    # Determine output folder structure
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    mkv_cleaner_path = os.path.join(downloads_path, 'MKV cleaner')

    # Try to detect series name from first file
    series_info = extract_series_info(file_names[0])
    if series_info[0]:  # If we can extract series info
        series_name = series_info[0]
        safe_series_name = re.sub(r'[<>:"/\\|?*]', '', series_name)
        output_folder = os.path.join(mkv_cleaner_path, safe_series_name)
        processing_status['log'].append(f"📁 Detected series: {series_name}")
    else:
        # Use timestamp for mixed files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_folder = os.path.join(
            mkv_cleaner_path, f"processed_{timestamp}")
        processing_status['log'].append(f"� Mixed files detected")

    os.makedirs(output_folder, exist_ok=True)
    processing_status['log'].append(f"📁 Output folder: {output_folder}")

    update_mkv_cleaner_config()

    def process_thread():
        try:
            processing_status['total_files'] = len(temp_files)
            processing_status['log'].append(
                f"🔄️ Processing {len(temp_files)} files")

            for i, temp_file_path in enumerate(temp_files):
                filename = os.path.basename(temp_file_path)
                processing_status['current_file'] = filename
                processing_status['progress'] = i

                try:
                    processing_status['log'].append(f"Processing: {filename}")
                    # Process directly to the Downloads/MKV cleaner/Series Name/ folder
                    filter_and_remux(
                        temp_file_path, output_folder, preferences=config)
                    processing_status['log'].append(f"✓ Completed: {filename}")
                except Exception as e:
                    processing_status['log'].append(
                        f"✗ Error processing {filename}: {str(e)}")

            processing_status['progress'] = len(temp_files)
            processing_status['current_file'] = ''
            processing_status['log'].append("🎉 All files processed!")
            processing_status['log'].append(
                f"📁 Results saved to: {output_folder}")

            # Clean up temporary files
            try:
                import shutil
                shutil.rmtree(temp_dir)
                processing_status['log'].append("🧹 Temporary files cleaned up")
            except Exception as e:
                processing_status['log'].append(
                    f"⚠️ Warning: Could not clean temp files: {str(e)}")

        except Exception as e:
            processing_status['log'].append(f"✗ Fatal error: {str(e)}")
        finally:
            processing_status['is_running'] = False

    thread = threading.Thread(target=process_thread)
    thread.daemon = True
    thread.start()

    return jsonify({'success': True, 'message': 'File processing started'})


if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)

    print("Starting MKV Cleaner Web Interface...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='localhost', port=5000)
