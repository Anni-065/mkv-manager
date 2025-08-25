"""
CLI Entry Point

Main script for command-line usage of the MKV manager.
"""

import os
from .processing.mkv_processor import filter_and_remux

try:
    from .config.config import MKV_FOLDER
except ImportError:
    from .config.config_example import MKV_FOLDER


def main():
    """Main function to process all MKV files in the configured folder."""
    for file in os.listdir(MKV_FOLDER):
        if file.lower().endswith(".mkv"):
            full_path = os.path.normpath(os.path.join(MKV_FOLDER, file))
            print(f"Processing file: {full_path}")
            filter_and_remux(full_path)


if __name__ == "__main__":
    main()
