#!/usr/bin/env python3
"""
Drag and drop functionality mixin for GUI components
"""

import tkinter as tk
from typing import TYPE_CHECKING, Any, Union, cast

try:
    from tkinterdnd2 import DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_FILES = None
    TkinterDnD = None
    DND_AVAILABLE = False

if TYPE_CHECKING:
    from typing import Protocol

    class Controller(Protocol):
        """Protocol for controller interface"""

        def on_drop(self, event: Any) -> None: ...


class DragDropMixin:
    """Mixin providing drag and drop functionality"""
    root: Union[tk.Tk, Any]
    controller: "Controller"

    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        if DND_AVAILABLE:
            dnd_root = cast(Any, self.root)
            dnd_root.drop_target_register(DND_FILES)
            dnd_root.dnd_bind('<<Drop>>', self.controller.on_drop)

    @staticmethod
    def is_dnd_available():
        """Check if drag and drop is available"""
        return DND_AVAILABLE
