#!/usr/bin/env python3
"""
Pre-commit hook to automatically sanitize personal information before committing.
This hook runs before each commit and temporarily sanitizes files.
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Main pre-commit hook function."""
    print("🔒 Pre-commit: Sanitizing files for commit...")

    repo_root = Path(__file__).parent
    os.chdir(repo_root)

    sanitize_script = repo_root / "sanitize_for_github.py"
    if not sanitize_script.exists():
        print("❌ sanitize_for_github.py not found. Skipping sanitization.")
        return 0

    try:
        sys.path.insert(0, str(repo_root))
        from sanitize_for_github import backup_original_files, sanitize_files

        backup_original_files()
        sanitize_files()

        result = subprocess.run(['git', 'add', '.'],
                                capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Files sanitized and staged for commit")
            return 0
        else:
            print(f"❌ Error staging sanitized files: {result.stderr}")
            return 1

    except Exception as e:
        print(f"❌ Error during sanitization: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
