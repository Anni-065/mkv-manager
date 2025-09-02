#!/usr/bin/env python3
"""
Scrollable Tab Mixin

Provides scrolling functionality for tab components that need it.
"""

import tkinter as tk
from tkinter import ttk
import platform
from typing import Dict, Any, Optional


class ScrollableTabMixin:
    """
    Mixin class that provides scrolling functionality for tab components.
    
    This mixin can be used with any tab component that needs scrollable content.
    It handles cross-platform mouse wheel scrolling and provides a clean API
    for creating scrollable frames.
    
    Requirements:
        Classes using this mixin should have:
        - colors: Dict containing at least 'bg' key for background color
        - frame: Optional tkinter Frame for delayed scrolling setup
    """
    
    colors: Dict[str, str]
    frame: Optional[tk.Widget]
    
    def create_scrollable_frame(self, parent):
        """
        Create scrollable frame with cross-platform mouse wheel support.
        
        Args:
            parent: The parent widget to contain the scrollable frame
            
        Returns:
            tuple: (canvas, scrollable_frame) where:
                - canvas: The tk.Canvas widget
                - scrollable_frame: The ttk.Frame that can be scrolled
        """
       
        bg_color = getattr(self, 'colors', {}).get('bg', '#ffffff')
        canvas = tk.Canvas(parent, bg=bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Modern.TFrame')

        def update_scroll_region():
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind(
            "<Configure>", 
            lambda e: canvas.after_idle(update_scroll_region)
        )

        canvas_window = canvas.create_window(
            (0, 0), window=scrollable_frame, anchor="nw"
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind('<Configure>', on_canvas_configure)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._setup_mousewheel_scrolling(canvas, scrollable_frame)

        return canvas, scrollable_frame
    
    def _setup_mousewheel_scrolling(self, canvas, scrollable_frame):
        """
        Set up cross-platform mouse wheel scrolling.
        
        Args:
            canvas: The canvas widget to scroll
            scrollable_frame: The frame containing the scrollable content
        """
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def on_mousewheel_linux(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        if platform.system() in ('Windows', 'Darwin'):
            canvas.bind("<MouseWheel>", on_mousewheel)
            scrollable_frame.bind("<MouseWheel>", on_mousewheel)
        else:  # Linux
            canvas.bind("<Button-4>", on_mousewheel_linux)
            canvas.bind("<Button-5>", on_mousewheel_linux)
            scrollable_frame.bind("<Button-4>", on_mousewheel_linux)
            scrollable_frame.bind("<Button-5>", on_mousewheel_linux)

        canvas.after(100, lambda: self._bind_children_mousewheel(
            scrollable_frame, on_mousewheel_linux
        ))
    
    def _bind_children_mousewheel(self, widget, scroll_command):
        """
        Recursively bind mouse wheel events to all child widgets (Linux).
        
        Args:
            widget: The widget to bind events for
            scroll_command: The scroll command to bind
        """
        if platform.system() not in ('Windows', 'Darwin'):
            widget.bind("<Button-4>", scroll_command)
            widget.bind("<Button-5>", scroll_command)
            
            for child in widget.winfo_children():
                self._bind_children_mousewheel(child, scroll_command)
    
    def setup_delayed_scrolling(self, delay_ms=100):
        """
        Setup scrolling for widgets that are created after initial setup.
        
        This is useful when widgets are dynamically created and need
        scrolling support added after the fact.
        
        Args:
            delay_ms: Delay in milliseconds before setting up scrolling
        """
        if frame := getattr(self, 'frame', None):
            frame.after(delay_ms, self._setup_delayed_child_scrolling)
    
    def _setup_delayed_child_scrolling(self):
        """Set up scrolling for dynamically created child widgets."""
        def on_mousewheel_linux(event):
            widget = event.widget

            while widget and not isinstance(widget, tk.Canvas):
                widget = widget.master
                
            if widget and isinstance(widget, tk.Canvas):
                if event.num == 4:
                    widget.yview_scroll(-1, "units")
                elif event.num == 5:
                    widget.yview_scroll(1, "units")
        
        if frame := getattr(self, 'frame', None):
            self._bind_children_mousewheel(frame, on_mousewheel_linux)
