#!/usr/bin/env python3
"""
Output options component for MKV Cleaner Desktop Application
"""

from gui.utils import get_icon
from styles import UIHelpers
import tkinter as tk
from tkinter import ttk
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
components_dir = os.path.dirname(current_dir)
gui_dir = os.path.dirname(components_dir)
desktop_dir = os.path.dirname(gui_dir)
sys.path.insert(0, desktop_dir)
sys.path.insert(0, gui_dir)

# Import image utilities


class OutputOptionsComponent:
    """Component for creating the output options section"""

    def __init__(self, parent, colors, controller, output_vars):
        self.parent = parent
        self.colors = colors
        self.controller = controller
        self.output_vars = output_vars

    def create(self):
        """Create the output options section"""

        output_frame = ttk.LabelFrame(self.parent, text="  Output Options  ",
                                      style='Modern.TLabelframe')
        output_frame.grid(row=3, column=0, sticky='ew', pady=(0, 20))
        output_frame.grid_columnconfigure(0, weight=1)

        options_frame = ttk.Frame(output_frame, style='Modern.TFrame')
        options_frame.grid(row=0, column=0, sticky='ew', padx=15, pady=15)

        same_folder_radio = ttk.Radiobutton(
            options_frame, text="Same folder (in 'processed' subfolder)",
            variable=self.output_vars['output_option'], value="same_folder",
            style='Modern.TRadiobutton'
        )
        same_folder_radio.grid(
            row=0, column=0, sticky='w', pady=5, padx=(20, 0))

        downloads_radio = ttk.Radiobutton(
            options_frame, text="Downloads folder (in 'MKV cleaner' subfolder)",
            variable=self.output_vars['output_option'], value="downloads",
            style='Modern.TRadiobutton'
        )
        downloads_radio.grid(row=0, column=1, sticky='w',
                             pady=5, padx=(20, 0))

        custom_radio = ttk.Radiobutton(
            options_frame, text="Custom folder:",
            variable=self.output_vars['output_option'], value="custom",
            style='Modern.TRadiobutton'
        )
        custom_radio.grid(row=2, column=0, sticky='w', pady=5, padx=(20, 0))

        custom_frame = ttk.Frame(options_frame, style='Modern.TFrame')
        custom_frame.grid(row=3, column=0, columnspan=2,
                          sticky='ew', padx=(45, 0), pady=5)
        custom_frame.grid_columnconfigure(0, weight=1)

        custom_entry = ttk.Entry(custom_frame, textvariable=self.output_vars['custom_folder'],
                                 style='Modern.TEntry')
        custom_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))

        browse_custom_btn = UIHelpers.create_button(
            custom_frame, text="Browse", command=self.controller.browse_custom_folder,
            button_type="secondary", colors=self.colors, width=80, height=30
        )

        if browse_custom_btn:
            browse_custom_btn.grid(row=0, column=1)

        return output_frame
