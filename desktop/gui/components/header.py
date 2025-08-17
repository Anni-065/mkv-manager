#!/usr/bin/env python3
"""
Header component for MKV Cleaner Desktop Application
"""

from tkinter import ttk


class HeaderComponent:
    """Component for creating the header section"""

    def __init__(self, parent, colors, dnd_available=False):
        self.parent = parent
        self.colors = colors
        self.dnd_available = dnd_available

    def create(self):
        """Create the header section"""
        header_frame = ttk.Frame(self.parent, style='Modern.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ttk.Label(header_frame, text="MKV Cleaner",
                                style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky='w')

        if self.dnd_available:
            drop_label = ttk.Label(header_frame, text="💡 Drag and drop MKV files or folders anywhere in this window",
                                   style='Subtitle.TLabel')
            drop_label.grid(row=1, column=0, sticky='w', pady=(0, 10))

        return header_frame
