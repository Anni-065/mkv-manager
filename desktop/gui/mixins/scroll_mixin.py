#!/usr/bin/env python3
"""
Scrolling functionality mixin for GUI components
"""

import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union


class ScrollMixin:
    """Mixin providing scrolling functionality

    This mixin expects the following attributes to be available:
    - canvas: tk.Canvas - The canvas widget for scrolling
    - root: tk.Tk - The root window widget
    - canvas_window: int - The canvas window ID created with create_window()
    """

    # Type annotations for expected attributes (will be provided by mixing class)
    canvas: tk.Canvas
    root: tk.Tk
    canvas_window: int

    def bind_mousewheel(self):
        """Bind mouse wheel to scrolling"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind("<MouseWheel>", _on_mousewheel)

        def bind_to_mousewheel(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_to_mousewheel(child)

        self.root.after(100, lambda: bind_to_mousewheel(self.root))

    def _on_canvas_configure(self, event):
        """Handle canvas resize events to update scrollable frame width"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
