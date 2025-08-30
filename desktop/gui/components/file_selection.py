#!/usr/bin/env python3
"""
File selection component for MKV Cleaner Desktop Application
"""

from styles import UIHelpers
from tkinter import ttk
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
components_dir = os.path.dirname(current_dir)
gui_dir = os.path.dirname(components_dir)
desktop_dir = os.path.dirname(gui_dir)
sys.path.insert(0, desktop_dir)
sys.path.insert(0, gui_dir)


class FileSelectionComponent:
    """Component for creating the file selection section"""

    def __init__(self, parent, colors, controller):
        self.parent = parent
        self.colors = colors
        self.controller = controller

    def create(self):
        """Create the file selection section"""
        file_frame = ttk.LabelFrame(self.parent, text="  📁 File Selection  ",
                                    style='Modern.TLabelframe')
        file_frame.grid(row=2, column=0, sticky='nsew', pady=(0, 20))
        file_frame.grid_columnconfigure(0, weight=1)
        file_frame.grid_rowconfigure(1, weight=1)

        button_frame = self._create_button_frame(file_frame)

        file_tree = self._create_file_list(file_frame)

        return file_frame, file_tree

    def _create_button_frame(self, parent):
        """Create the button frame with action buttons"""
        button_frame = ttk.Frame(parent, style='Modern.TFrame')
        button_frame.grid(row=0, column=0, sticky='ew', padx=15, pady=15)

        button_frame.grid_columnconfigure(2, weight=1)

        browse_files_btn = UIHelpers.create_button(
            button_frame, text="📄 Select Files", command=self.controller.browse_files,
            button_type="primary", colors=self.colors, width=120, height=30
        )
        if browse_files_btn:
            browse_files_btn.grid(row=0, column=0, padx=(0, 10))

        browse_folder_btn = UIHelpers.create_button(
            button_frame, text="📁 Select Folder", command=self.controller.browse_folder,
            button_type="secondary", colors=self.colors, width=120, height=30
        )
        if browse_folder_btn:
            browse_folder_btn.grid(row=0, column=1, padx=(0, 10))

        clear_btn = UIHelpers.create_button(
            button_frame, text="Clear All", command=self.controller.clear_selection,
            button_type="danger", colors=self.colors, width=80, height=30
        )
        if clear_btn:
            clear_btn.grid(row=0, column=3, sticky='e')

        return button_frame

    def _create_file_list(self, parent):
        """Create the file list treeview"""
        list_frame = ttk.Frame(parent, style='Modern.TFrame')
        list_frame.grid(row=1, column=0, sticky='nsew', padx=15, pady=(0, 15))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        columns = ('Name', 'Path', 'Size', 'Series')
        file_tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                 style='Modern.Treeview')

        file_tree.heading('Name', text='File Name')
        file_tree.heading('Path', text='Location')
        file_tree.heading('Size', text='Size')
        file_tree.heading('Series', text='Series Info')

        file_tree.column('Name', width=300)
        file_tree.column('Path', width=350)
        file_tree.column('Size', width=80)
        file_tree.column('Series', width=220)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=file_tree.yview,
                                  style='Modern.Vertical.TScrollbar')
        file_tree.configure(yscrollcommand=scrollbar.set)

        file_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        return file_tree
