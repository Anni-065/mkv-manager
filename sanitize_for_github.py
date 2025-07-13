#!/usr/bin/env python3
"""
Script to sanitize personal information from MKV Manager files before pushing to GitHub.
This script replaces personal paths and sensitive information with generic placeholders.
"""

import os
import re
import shutil
from pathlib import Path


def get_replacements():
    """Generate replacement patterns dynamically to avoid hardcoding personal paths."""
    import os

    user_home = os.path.expanduser('~')
    user_name = os.path.basename(user_home)

    program_files = os.environ.get('PROGRAMFILES', 'C:\\Program Files')

    return {
        # Dynamic user paths (single backslash) - most common in Python strings
        rf'C:\\Users\\{re.escape(user_name)}\\Documents\\[^\\]+\\mkv-manager': '/path/to/mkv-manager',
        rf'C:\\Users\\{re.escape(user_name)}\\Downloads\\complete\\[^\\]+': '/path/to/mkv/source',
        rf'C:\\Users\\{re.escape(user_name)}\\Downloads\\complete': '/path/to/mkv/source',
        rf'C:\\Users\\{re.escape(user_name)}\\': '/home/user/',
        rf'{re.escape(program_files)}\\MKVToolNix\\mkvmerge\.exe': '/usr/bin/mkvmerge',

        # Dynamic user paths (double backslash for JSON/HTML escaped strings)
        rf'C:\\\\Users\\\\{re.escape(user_name)}\\\\Documents\\\\[^\\\\]+\\\\mkv-manager': '/path/to/mkv-manager',
        rf'C:\\\\Users\\\\{re.escape(user_name)}\\\\Downloads\\\\complete\\\\[^\\\\]+': '/path/to/mkv/source',
        rf'C:\\\\Users\\\\{re.escape(user_name)}\\\\Downloads\\\\complete': '/path/to/mkv/source',
        rf'C:\\\\Users\\\\{re.escape(user_name)}\\\\': '/home/user/',

        # User name replacement (word boundary to avoid partial matches)
        rf'\\b{re.escape(user_name)}\\b': 'user',

        # Secret keys
        r'your_secret_key_here': 'your_secret_key_here',
    }


# Files to process
FILES_TO_SANITIZE = [
    'mkv_cleaner.py',
    'web_interface.py',
    'templates/index.html',
    'templates/config.html',
    'test_quality_detection.py',
    'sanitize_for_github.py',
]


def get_files_to_sanitize():
    """Get list of files to sanitize, including dynamically discovered .md files."""
    import glob

    files = FILES_TO_SANITIZE.copy()

    md_files = glob.glob('*.md')
    for md_file in md_files:
        if md_file not in files:
            files.append(md_file)

    return files


# Files to exclude from GitHub (add to .gitignore)
GITIGNORE_ENTRIES = [
    '# Personal configuration files',
    'config.json',
    'personal_config.py',
    '*.log',
    'processed/',
    'mkv_process_log.txt',
    '',
    '# Backup files',
    'backups/',
    '*.backup',
    '',
    '# Test files',
    'test_*.py',
    '',
    '# Documentation that might contain personal info',
    '# (Individual .md files are sanitized automatically)',
    '',
    '# IDE files',
    '.vscode/',
    '.idea/',
    '__pycache__/',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.Python',
    'env/',
    'venv/',
    '.venv/',
    '.env',
    '',
    '# OS files',
    '.DS_Store',
    'Thumbs.db',
    'desktop.ini',
]


def sanitize_content(content):
    """Apply all replacements to the content."""
    replacements = get_replacements()
    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    return content


def backup_original_files():
    """Create backups of original files before sanitizing."""
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)

    print("📦 Creating backups of original files...")

    for file_path in get_files_to_sanitize():
        if os.path.exists(file_path):
            backup_path = backup_dir / f"{Path(file_path).name}.backup"
            shutil.copy2(file_path, backup_path)
            print(f"  ✓ Backed up {file_path} to {backup_path}")


def sanitize_files():
    """Sanitize all specified files."""
    print("🧹 Sanitizing files for GitHub...")

    for file_path in get_files_to_sanitize():
        if os.path.exists(file_path):
            print(f"  📝 Processing {file_path}...")

            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            sanitized_content = sanitize_content(original_content)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(sanitized_content)

            print(f"  ✓ Sanitized {file_path}")
        else:
            print(f"  ⚠️ File not found: {file_path}")


def create_gitignore():
    """Create or update .gitignore file."""
    print("📝 Creating/updating .gitignore...")

    gitignore_path = Path('.gitignore')

    existing_content = ""
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()

    new_entries = []
    for entry in GITIGNORE_ENTRIES:
        if entry not in existing_content:
            new_entries.append(entry)

    if new_entries:
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            if existing_content and not existing_content.endswith('\n'):
                f.write('\n')
            f.write('\n'.join(new_entries))
        print(
            f"  ✓ Updated .gitignore with {len([e for e in new_entries if e.strip()])} new entries")
    else:
        print("  ✓ .gitignore is already up to date")


def create_example_config():
    """Create example configuration files."""
    print("📋 Creating example configuration files...")

    example_config = '''
# Example configuration - Replace with your actual paths
MKVMERGE_PATH = r"/usr/bin/mkvmerge"  # Path to mkvmerge executable
MKV_FOLDER = r"/path/to/your/mkv/files"  # Source folder containing MKV files
OUTPUT_FOLDER = os.path.join(MKV_FOLDER, "processed")  # Output folder for processed files

# Language settings
ALLOWED_SUB_LANGS = {"eng", "ger", "kor", "gre"}  # Allowed subtitle languages
ALLOWED_AUDIO_LANGS = {"kor"}  # Allowed audio languages

DEFAULT_AUDIO_LANG = "kor"  # Default audio language
DEFAULT_SUBTITLE_LANG = "eng"  # Default subtitle language

ORIGINAL_AUDIO_LANG = "kor"  # Original audio language
ORIGINAL_SUBTITLE_LANG = "kor"  # Original subtitle language
'''

    with open('config_example.py', 'w', encoding='utf-8') as f:
        f.write(example_config.strip())

    print("  ✓ Created config_example.py")


def restore_from_backup():
    """Restore original files from backup."""
    backup_dir = Path('backups')

    if not backup_dir.exists():
        print("❌ No backup directory found!")
        return

    print("🔄 Restoring files from backup...")

    for backup_file in backup_dir.glob('*.backup'):
        original_name = backup_file.stem

        for file_path in get_files_to_sanitize():
            if Path(file_path).name == original_name:
                shutil.copy2(backup_file, file_path)
                print(f"  ✓ Restored {file_path}")
                break


def main():
    """Main function with user interaction."""
    print("🎬 MKV Manager - GitHub Sanitization Script")
    print("=" * 50)

    while True:
        print("\nOptions:")
        print("1. 🧹 Sanitize files for GitHub (creates backups)")
        print("2. 🔄 Restore from backup")
        print("3. 📝 Create .gitignore only")
        print("4. 📋 Create example config only")
        print("5. ❌ Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == '1':
            backup_original_files()
            sanitize_files()
            create_gitignore()
            create_example_config()
            print("\n✅ Files sanitized and ready for GitHub!")
            print("💡 Don't forget to:")
            print("   - Review the changes before committing")
            print("   - Update config_example.py with your actual settings")
            print("   - Test the sanitized code to ensure it still works")

        elif choice == '2':
            restore_from_backup()
            print("\n✅ Files restored from backup!")

        elif choice == '3':
            create_gitignore()
            print("\n✅ .gitignore created/updated!")

        elif choice == '4':
            create_example_config()
            print("\n✅ Example configuration created!")

        elif choice == '5':
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main()
