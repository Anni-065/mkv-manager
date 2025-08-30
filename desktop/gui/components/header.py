#!/usr/bin/env python3
"""
Header component for MKV Cleaner Desktop Application
"""

from gui.utils import get_icon
from tkinter import ttk
from styles import UIHelpers
import os
import sys

# Add path for importing utils
current_dir = os.path.dirname(os.path.abspath(__file__))
components_dir = os.path.dirname(current_dir)
gui_dir = os.path.dirname(components_dir)
sys.path.insert(0, gui_dir)

# Import image utilities


class HeaderComponent:
    """Component for creating the header section"""

    def __init__(self, parent, colors, controller=None, dnd_available=False):
        self.parent = parent
        self.colors = colors
        self.controller = controller
        self.dnd_available = dnd_available

    def create(self):
        """Create the header section"""
        header_frame = ttk.Frame(self.parent, style='Modern.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(
            1, weight=0)

        title_section = ttk.Frame(header_frame, style='Modern.TFrame')
        title_section.grid(row=0, column=0, sticky='w')

        title_label = ttk.Label(title_section, text="MKV Cleaner",
                                style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky='w')

        if self.dnd_available:
            drop_label = ttk.Label(title_section, text="💡 Drag and drop MKV files or folders anywhere in this window",
                                   style='Subtitle.TLabel')
            drop_label.grid(row=1, column=0, sticky='w', pady=(0, 10))

        if self.controller:
            settings_frame = ttk.Frame(header_frame, style='Modern.TFrame')
            settings_frame.grid(row=0, column=1, sticky='ne', padx=(10, 0))

            # Get settings icon
            settings_icon = get_icon('settings')

            # Use icon button type for settings button (icon only, no background)
            settings_btn = UIHelpers.create_image_button(
                settings_frame, text="", command=self.controller.open_language_manager,
                button_type="icon", colors=self.colors, image=settings_icon,
                width=35, height=35
            )

            if settings_btn:
                settings_btn.grid(row=0, column=0)

        return header_frame
