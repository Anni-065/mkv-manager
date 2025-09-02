#!/usr/bin/env python3
"""
Process section component for MKV Cleaner Desktop Application
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


class ProcessSectionComponent:
    """Component for creating the process section"""

    def __init__(self, parent, colors, controller):
        self.parent = parent
        self.colors = colors
        self.controller = controller

    def create(self):
        """Create the process section"""
        process_frame = ttk.Frame(self.parent, style='Modern.TFrame')
        process_frame.grid(row=4, column=0, sticky='ew')
        process_frame.grid_columnconfigure(0, weight=1)

        try:
            progress_bar = UIHelpers.create_progress_bar(
                process_frame, 
                colors=self.colors,
                height=14
            )
            progress_bar.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        except:
            progress_bar = ttk.Progressbar(
                process_frame, mode='determinate',
                style='Modern.Horizontal.TProgressbar',
                maximum=100
            )
            progress_bar.grid(row=0, column=0, sticky='ew', pady=(0, 10))

        progress_label = ttk.Label(
            process_frame, text="Ready to process files",
            style='Modern.TLabel'
        )
        progress_label.grid(row=1, column=0, pady=(0, 15))

        process_button = UIHelpers.create_button(
            process_frame, text="Start Processing", command=self.controller.process_files,
            button_type="primary", colors=self.colors, width=200, height=45
        )
        if process_button:
            process_button.grid(row=2, column=0, pady=(0, 10))

        return process_frame, progress_bar, progress_label, process_button
