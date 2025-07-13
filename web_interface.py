from mkv_cleaner import extract_series_info, get_track_info, filter_and_remux
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import subprocess
import threading
from datetime import datetime
import shutil

try:
    from config import *
    print("✅ Web interface using config.py")
except ImportError:
    try:
        from config_example import *
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
    'ORIGINAL_SUBTITLE_LANG': ORIGINAL_SUBTITLE_LANG
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
    import mkv_cleaner
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
    os.makedirs(mkv_cleaner.OUTPUT_FOLDER, exist_ok=True)


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
        # Check for custom path parameter
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

    # Get custom path from request if provided
    request_data = request.get_json() or {}
    custom_path = request_data.get('custom_path')
    source_folder = custom_path if custom_path else config['MKV_FOLDER']

    # Validate the source folder exists
    if not os.path.exists(source_folder):
        return jsonify({'error': f'Source folder does not exist: {source_folder}'})

    update_mkv_cleaner_config()

    def process_thread():
        try:
            processing_status['is_running'] = True
            processing_status['log'] = []
            processing_status['progress'] = 0

            # Log which folder is being processed
            if custom_path:
                processing_status['log'].append(
                    f"📁 Using custom path: {custom_path}")
            else:
                processing_status['log'].append(
                    f"📁 Using default path: {config['MKV_FOLDER']}")

            mkv_files = [f for f in os.listdir(
                source_folder) if f.lower().endswith('.mkv')]
            processing_status['total_files'] = len(mkv_files)

            if len(mkv_files) == 0:
                processing_status['log'].append(
                    "⚠️ No MKV files found in the specified folder")
                return

            for i, file in enumerate(mkv_files):
                processing_status['current_file'] = file
                processing_status['progress'] = i

                try:
                    full_path = os.path.normpath(
                        os.path.join(source_folder, file))
                    processing_status['log'].append(f"Processing: {file}")
                    filter_and_remux(full_path)
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
                'name': '.. (Parent Directory)',
                'path': parent,
                'type': 'parent',
                'icon': '📁'
            })

        for item in os.listdir(path):
            # Skip hidden folders/files that start with a dot
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
                    # Try to get some basic info about the drive
                    total, used, free = shutil.disk_usage(drive_path)
                    drives.append({
                        'letter': letter,
                        'path': drive_path,
                        'total': total,
                        'free': free,
                        'used': used
                    })
                except:
                    # If we can't get disk usage, just add the drive
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
        # Update language configuration
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

        flash('Language settings updated successfully!', 'success')
        return redirect(url_for('index'))


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)

    print("Starting MKV Cleaner Web Interface...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='localhost', port=5000)
