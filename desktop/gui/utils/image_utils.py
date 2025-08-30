"""
Image utility module for loading and managing GUI images with color inversion support.
"""
import os
import tkinter as tk
from tkinter import PhotoImage
from typing import Dict, Optional, Any

try:
    from PIL import Image, ImageTk, ImageOps
    PIL_AVAILABLE = True
except ImportError:
    # Dummy imports to satisfy type checker when PIL is not available
    Image = None  # type: ignore
    ImageTk = None  # type: ignore
    ImageOps = None  # type: ignore
    PIL_AVAILABLE = False
    print("PIL/Pillow not available. Color inversion will use fallback method.")


class ImageManager:
    """Manages loading and caching of images for the GUI with color inversion support."""

    def __init__(self):
        self._image_cache: Dict[str, Any] = {}
        self._assets_path = os.path.join(
            os.path.dirname(__file__), '..', 'assets')

    def get_image(self, image_name: str, size: Optional[tuple] = None,
                  invert_colors: bool = False) -> Optional[Any]:
        """
        Load and return an image from the assets folder with optional color inversion.

        Args:
            image_name: Name of the image file (e.g., 'folder.png')
            size: Optional tuple (width, height) to resize the image
            invert_colors: Whether to invert the colors (for light/dark themes)

        Returns:
            PhotoImage object or None if image not found
        """
        cache_key = f"{image_name}_{size}_{invert_colors}"

        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        if invert_colors:
            inverted_name = self._get_inverted_variant_name(image_name)
            inverted_path = os.path.join(self._assets_path, inverted_name)
            if os.path.exists(inverted_path):
                try:
                    image = PhotoImage(file=inverted_path)
                    self._image_cache[cache_key] = image
                    return image
                except Exception as e:
                    print(f"Error loading manual variant {inverted_path}: {e}")

        image_path = os.path.join(self._assets_path, image_name)

        if not os.path.exists(image_path):
            print(f"Warning: Image not found: {image_path}")
            return None

        try:
            if invert_colors and PIL_AVAILABLE:
                image = self._load_and_invert_image(image_path, size)
            else:
                image = PhotoImage(file=image_path)

                if size:
                    pass

            self._image_cache[cache_key] = image
            return image

        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None

    def _get_inverted_variant_name(self, image_name: str) -> str:
        """Generate the expected filename for inverted variant."""
        name, ext = os.path.splitext(image_name)
        return f"{name}_white{ext}"

    def _load_and_invert_image(self, image_path: str, size: Optional[tuple] = None) -> Any:
        """Load image using PIL and apply color inversion."""
        if not PIL_AVAILABLE or Image is None or ImageTk is None or ImageOps is None:
            raise ImportError("PIL is required for color inversion")

        pil_image = Image.open(image_path).convert("RGBA")

        if size:
            pil_image = pil_image.resize(size, Image.Resampling.LANCZOS)

        rgb_image = pil_image.convert("RGB")
        inverted_rgb = ImageOps.invert(rgb_image)

        if pil_image.mode == "RGBA":
            r, g, b, a = pil_image.split()
            inverted_r, inverted_g, inverted_b = inverted_rgb.split()
            inverted_image = Image.merge(
                "RGBA", (inverted_r, inverted_g, inverted_b, a))
        else:
            inverted_image = inverted_rgb

        return ImageTk.PhotoImage(inverted_image)

    def get_icon_image(self, icon_type: str, is_light: bool = False) -> Optional[Any]:
        """
        Get a standard icon image for buttons with optional color inversion.

        Args:
            icon_type: Type of icon ('folder', 'file', 'settings', etc.)
            is_light: Whether to use light/inverted colors (True for dark backgrounds)

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

        return self.get_image(icon_mapping[icon_type], invert_colors=is_light)


image_manager = ImageManager()


def get_icon(icon_type: str, is_light: bool = False) -> Optional[Any]:
    """
    Convenience function to get an icon image with optional color inversion.

    Args:
        icon_type: Type of icon ('folder', 'file', 'settings', etc.)
        is_light: Whether to use light/inverted colors (True for dark backgrounds)
    """
    return image_manager.get_icon_image(icon_type, is_light)


def get_image(image_name: str, size: Optional[tuple] = None,
              invert_colors: bool = False) -> Optional[Any]:
    """
    Convenience function to get any image with optional color inversion.

    Args:
        image_name: Name of the image file
        size: Optional size tuple
        invert_colors: Whether to invert colors
    """
    return image_manager.get_image(image_name, size, invert_colors)
