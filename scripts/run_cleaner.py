#!/usr/bin/env python3
"""
MKV Manager - Standalone Script Runner

This script provides a command-line interface for running the MKV Manager
core functionality without the web interface.
"""

from core.main import main as run_mkv_cleaner
import sys
import os

# Add the parent directory to the Python path so we can import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def main():
    """Main entry point for the standalone script."""
    print("🎬 MKV Manager - Standalone Mode")
    print("=" * 50)

    try:
        run_mkv_cleaner()
        print("\n✅ Processing completed successfully!")
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
