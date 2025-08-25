"""
File Selection Controller for MKV Cleaner Desktop GUI
Handles file browsing, folder browsing, drag & drop, and file list management
"""

import os
from tkinter import filedialog, messagebox
from pathlib import Path

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

try:
    from core import extract_series_info
except ImportError:
    def extract_series_info(filename):
        return ("Unknown", "Unknown")


class FileSelectionController:
    """Controller for file selection and management operations"""

    def __init__(self, gui, selected_files, update_process_button_callback):
        self.gui = gui
        self.selected_files = selected_files
        self.update_process_button_callback = update_process_button_callback

    def browse_files(self):
        """Browse for individual MKV files"""
        filetypes = [
            ("MKV files", "*.mkv"),
            ("All files", "*.*")
        ]

        filenames = filedialog.askopenfilenames(
            title="Select MKV files to process",
            filetypes=filetypes
        )

        if filenames:
            self.add_files_to_selection(filenames)

    def browse_folder(self):
        """Browse for a folder containing MKV files"""
        folder_path = filedialog.askdirectory(
            title="Select folder containing MKV files"
        )

        if folder_path:
            mkv_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith('.mkv'):
                        mkv_files.append(os.path.join(root, file))

            if mkv_files:
                self.add_files_to_selection(mkv_files)
            else:
                messagebox.showwarning(
                    "No MKV Files", "No MKV files found in the selected folder.")

    def on_drop(self, event):
        """Handle drag and drop events"""
        if not DND_AVAILABLE:
            return

        files = self.gui.root.tk.splitlist(event.data)
        mkv_files = []

        for item in files:
            if os.path.isfile(item):
                if item.lower().endswith('.mkv'):
                    mkv_files.append(item)
            elif os.path.isdir(item):
                for root, dirs, files in os.walk(item):
                    for file in files:
                        if file.lower().endswith('.mkv'):
                            mkv_files.append(os.path.join(root, file))

        if mkv_files:
            self.add_files_to_selection(mkv_files)
        else:
            messagebox.showwarning(
                "No MKV Files", "No MKV files found in the dropped items.")

    def add_files_to_selection(self, filenames):
        """Add files to the selection list"""
        for filename in filenames:
            if filename not in [f['path'] for f in self.selected_files]:
                file_info = {
                    'path': filename,
                    'name': os.path.basename(filename),
                    'size': self.format_file_size(os.path.getsize(filename)),
                    'series_info': self.get_series_info(filename)
                }
                self.selected_files.append(file_info)

                self.gui.file_tree.insert('', 'end', values=(
                    file_info['name'],
                    os.path.dirname(filename),
                    file_info['size'],
                    file_info['series_info']
                ))

        self.update_process_button_callback()

    def clear_selection(self):
        """Clear all selected files"""
        self.selected_files.clear()
        self.gui.file_tree.delete(*self.gui.file_tree.get_children())
        self.update_process_button_callback()

    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    def get_series_info(self, filename):
        """Extract series information from filename"""
        try:
            series_info = extract_series_info(os.path.basename(filename))
            if series_info[0] and series_info[1]:
                return f"{series_info[0]} - {series_info[1]}"
            return "Unknown series"
        except Exception:
            return "Unknown series"
