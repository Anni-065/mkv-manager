"""
Output Folder Controller for MKV Cleaner Desktop GUI
Handles output folder selection and path logic
"""

import os
import re
from tkinter import filedialog, messagebox

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

try:
    from core.mkv_cleaner import extract_series_info
except ImportError:
    def extract_series_info(filename):
        return ("Unknown", "Unknown")


class OutputFolderController:
    """Controller for output folder operations"""

    def __init__(self, gui):
        self.gui = gui

    def browse_custom_folder(self):
        """Browse for custom output folder"""
        folder_path = filedialog.askdirectory(
            title="Select custom output folder"
        )

        if folder_path:
            self.gui.custom_folder.set(folder_path)

    def get_output_folder(self, file_path):
        """Determine output folder based on selected option"""
        option = self.gui.output_option.get()

        if option == "same_folder":
            source_dir = os.path.dirname(file_path)
            return os.path.join(source_dir, "processed")

        elif option == "downloads":
            downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
            mkv_cleaner_path = os.path.join(downloads_path, 'MKV cleaner')

            series_info = extract_series_info(os.path.basename(file_path))
            if series_info[0]:
                safe_series_name = re.sub(r'[<>:"/\\|?*]', '', series_info[0])
                return os.path.join(mkv_cleaner_path, safe_series_name)
            else:
                return os.path.join(mkv_cleaner_path, "processed")

        elif option == "custom":
            custom_path = self.gui.custom_folder.get()
            if custom_path:
                return custom_path
            else:
                messagebox.showerror(
                    "Error", "Please select a custom output folder.")
                return None

        return None
