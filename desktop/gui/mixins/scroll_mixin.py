#!/usr/bin/env python3
"""
Scrolling functionality mixin for GUI components
"""

import platform
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

    canvas: tk.Canvas
    root: tk.Tk
    canvas_window: int

 
    def bind_mousewheel(self, widget, target_canvas=None):
        """Bind mouse wheel to scrolling (cross-platform)
        
        Args:
            widget: The widget to bind the mousewheel event to (Canvas or Frame)
            target_canvas: The canvas to scroll (if widget is not a canvas)
        """
        system = platform.system()
        
        if hasattr(widget, 'yview_scroll'):
            scroll_target = widget
        elif target_canvas and hasattr(target_canvas, 'yview_scroll'):
            scroll_target = target_canvas
        else:
            scroll_target = getattr(self, 'canvas', None)

            if not scroll_target or not hasattr(scroll_target, 'yview_scroll'):
                print(f"Warning: No scrollable canvas found for {type(widget).__name__}")
                return

        def _on_mousewheel(event):
            if system == 'Windows':
                scroll_target.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif system == 'Darwin':
                scroll_target.yview_scroll(int(-1 * (event.delta)), "units")
            else:
                if event.num == 4:
                    scroll_target.yview_scroll(-1, "units")
                elif event.num == 5:
                    scroll_target.yview_scroll(1, "units")

        if system in ('Windows', 'Darwin'):
            widget.bind("<MouseWheel>", _on_mousewheel)
        else:
            widget.bind("<Button-4>", _on_mousewheel)
            widget.bind("<Button-5>", _on_mousewheel)
        
        if system == 'Linux' and not hasattr(widget, 'yview_scroll'):
            self._bind_mousewheel_to_children(widget, _on_mousewheel)
    
    def _bind_mousewheel_to_children(self, widget, mousewheel_handler):
        """Recursively bind mousewheel to all child widgets (Linux compatibility)"""
        try:
            widget.bind("<Button-4>", mousewheel_handler)
            widget.bind("<Button-5>", mousewheel_handler)
            
            for child in widget.winfo_children():
                self._bind_mousewheel_to_children(child, mousewheel_handler)
        except Exception:
            pass

    def _on_canvas_configure(self, event):
        """Handle canvas resize events to update scrollable frame width"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
