#!/usr/bin/env python3
"""
Drag and drop functionality mixin for GUI components
"""

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


class DragDropMixin:
    """Mixin providing drag and drop functionality"""

    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        if DND_AVAILABLE:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.controller.on_drop)

    @staticmethod
    def is_dnd_available():
        """Check if drag and drop is available"""
        return DND_AVAILABLE
