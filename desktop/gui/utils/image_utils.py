"""
Image utility module for loading and managing GUI images.
"""
import os
import tkinter as tk
from tkinter import PhotoImage
from typing import Dict, Optional


class ImageManager:
    """Manages loading and caching of images for the GUI."""

    def __init__(self):
        self._image_cache: Dict[str, PhotoImage] = {}
        self._assets_path = os.path.join(
            os.path.dirname(__file__), '..', 'assets')

    def get_image(self, image_name: str, size: Optional[tuple] = None) -> Optional[PhotoImage]:
        """
        Load and return an image from the assets folder.

        Args:
            image_name: Name of the image file (e.g., 'folder.png')
            size: Optional tuple (width, height) to resize the image

        Returns:
            PhotoImage object or None if image not found
        """
        cache_key = f"{image_name}_{size}" if size else image_name

        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        image_path = os.path.join(self._assets_path, image_name)

        if not os.path.exists(image_path):
            print(f"Warning: Image not found: {image_path}")
            return None

        try:
            image = PhotoImage(file=image_path)

            if size:
                # DEV
                # Note: For better resizing, consider using PIL/Pillow
                # For now, we'll use the original image and let tkinter handle scaling
                pass

            self._image_cache[cache_key] = image
            return image

        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None

    def get_icon_image(self, icon_type: str) -> Optional[PhotoImage]:
        """
        Get a standard icon image for buttons.

        Args:
            icon_type: Type of icon ('folder', 'file', 'settings', etc.)

        Returns:
            PhotoImage object or None if not found
        """
        icon_mapping = {
            'folder': 'folder.png',
            'file': 'file.png',
            'settings': 'settings.png',
            'search': 'search.png',
            'save': 'save.png',
            'download': 'download.png',
            'globe': 'globe.png',
        }

        if icon_type not in icon_mapping:
            return None

        return self.get_image(icon_mapping[icon_type])


image_manager = ImageManager()


def get_icon(icon_type: str) -> Optional[PhotoImage]:
    """Convenience function to get an icon image."""
    return image_manager.get_icon_image(icon_type)


def get_image(image_name: str, size: Optional[tuple] = None) -> Optional[PhotoImage]:
    """Convenience function to get any image."""
    return image_manager.get_image(image_name, size)
