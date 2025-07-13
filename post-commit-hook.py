#!/usr/bin/env python3
"""
Post-commit hook to automatically restore original files after committing.
This hook runs after each successful commit and restores the original files.
"""

import os
import sys
from pathlib import Path


def main():
    """Main post-commit hook function."""
    print("🔓 Post-commit: Restoring original files...")

    repo_root = Path(__file__).parent
    os.chdir(repo_root)

    sanitize_script = repo_root / "sanitize_for_github.py"
    if not sanitize_script.exists():
        print("❌ sanitize_for_github.py not found. Cannot restore files.")
        return 0

    try:
        sys.path.insert(0, str(repo_root))
        from sanitize_for_github import restore_from_backup

        restore_from_backup()

        print("✅ Original files restored")
        print("💡 Your working directory now contains your personal settings again")
        return 0

    except Exception as e:
        print(f"❌ Error during restoration: {str(e)}")
        print("💡 You may need to manually restore from backups/ folder")
        return 1


if __name__ == "__main__":
    sys.exit(main())
