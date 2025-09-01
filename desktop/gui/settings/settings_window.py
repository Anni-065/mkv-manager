#!/usr/bin/env python3
"""
Refactored Settings Window for MKV Manager Desktop Application

This is a modular, maintainable version of the settings window that uses
component-based architecture following industry best practices.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from typing import Dict, Any, Optional, Callable, Tuple

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
gui_dir = os.path.dirname(os.path.dirname(current_dir))
desktop_dir = os.path.dirname(gui_dir)
root_dir = os.path.dirname(desktop_dir)
sys.path.insert(0, root_dir)
sys.path.insert(0, desktop_dir)
sys.path.insert(0, gui_dir)

from styles import UIHelpers
from core.config.user_config import get_user_config_manager

from .components import (
    PathsTabComponent,
    LanguagesTabComponent, 
    SubtitlesTabComponent
)


class SettingsWindow:
    """
    Orchestrates the different tab components and handles
    the overall window management, validation, and saving logic.
    """
    
    def __init__(self, parent, colors: Dict[str, str], callback: Optional[Callable] = None):
        """
        Initialize settings window.
        
        Args:
            parent: Parent tkinter widget
            colors: Dictionary containing color scheme
            callback: Optional callback function called after saving settings
        """
        self.parent = parent
        self.colors = colors
        self.callback = callback
        self.user_config = get_user_config_manager()
        
        # Load current settings
        self.settings = self.user_config.get_all_settings()
        
        # Initialize tab components
        self.tab_components = []
        
        self._create_window()
        self._create_interface()
        
    def _create_window(self):
        """Create and configure the main window."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("MKV Manager - Settings")
        self.window.geometry("900x700")
        self.window.configure(bg=self.colors['bg'])
        self.window.transient(self.parent)
        
        self._center_window()
        
        # Set modal after a short delay
        self.window.after(1, self.window.grab_set)
    
    def _center_window(self):
        """Center the window on the parent."""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.window.winfo_screenheight() // 2) - (700 // 2)
        self.window.geometry(f"900x700+{x}+{y}")
    
    def _create_interface(self):
        """Create the main interface."""
        self._create_header()
        self._create_content_area()
        self._create_buttons()
    
    def _create_header(self):
        """Create the header section."""
        header_frame = ttk.Frame(self.window, style='Modern.TFrame')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        title_label = ttk.Label(
            header_frame,
            text="Settings",
            font=('Segoe UI', 16, 'bold'),
            style='Title.TLabel'
        )
        title_label.pack(side='left')
        
        info_label = ttk.Label(
            header_frame,
            text="Configure your MKV Manager preferences",
            font=('Segoe UI', 10),
            style='Subtitle.TLabel'
        )
        info_label.pack(side='left', padx=(20, 0))
    
    def _create_content_area(self):
        """Create the main content area with tabs."""
        content_frame = ttk.Frame(self.window, style='Modern.TFrame')
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.notebook = ttk.Notebook(content_frame, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True)
        
        self._create_tab_components()
    
    def _create_tab_components(self):
        """Create and initialize all tab components."""
        tab_classes = [
            PathsTabComponent,
            LanguagesTabComponent,
            SubtitlesTabComponent
        ]
        
        for tab_class in tab_classes:
            component = tab_class(
                parent=self.notebook,
                colors=self.colors,
                settings=self.settings,
                user_config=self.user_config
            )
            
            component.create_content()
            component.add_to_notebook(self.notebook)
            self.tab_components.append(component)
    
    def _create_buttons(self):
        """Create the button section."""
        buttons_frame = ttk.Frame(self.window, style='Modern.TFrame')
        buttons_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Left side - Reset to defaults
        try:
            reset_btn = UIHelpers.create_image_button(
                buttons_frame, text="Reset to Defaults",
                command=self._reset_to_defaults,
                button_type="secondary", colors=self.colors, icon_type="settings",
                width=150, height=35
            )
            if reset_btn:
                reset_btn.pack(side='left')
            else:
                reset_btn = ttk.Button(
                    buttons_frame, text="Reset to Defaults",
                    command=self._reset_to_defaults, style='Modern.TButton'
                )
                reset_btn.pack(side='left')
        except Exception:
            reset_btn = ttk.Button(
                buttons_frame, text="Reset to Defaults",
                command=self._reset_to_defaults, style='Modern.TButton'
            )
            reset_btn.pack(side='left')
        
        ttk.Frame(buttons_frame, style='Modern.TFrame').pack(
            side='left', expand=True
        )
        
        try:        
            save_btn = UIHelpers.create_image_button(
                buttons_frame, text="Save Settings",
                command=self._save_settings,
                button_type="success", colors=self.colors, icon_type="save",
                width=150, height=35
            )
            if save_btn:
                save_btn.pack(side='right')
            else:
                save_btn = ttk.Button(
                    buttons_frame, text="Save Settings",
                    command=self._save_settings, style='Modern.TButton'
                )
                save_btn.pack(side='right')
        except Exception:
            save_btn = ttk.Button(
                buttons_frame, text="Save Settings",
                command=self._save_settings, style='Modern.TButton'
            )
            save_btn.pack(side='right')
    
    def _validate_all_settings(self):
        """
        Validate settings from all tab components.
        
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        for component in self.tab_components:
            is_valid, error_msg = component.validate_settings()
            if not is_valid:
                tab_name = component.get_tab_name()
                return False, f"{tab_name}: {error_msg}"
        
        return True, None
    
    def _collect_all_settings(self):
        """
        Collect settings from all tab components.
        
        Returns:
            dict: Combined settings dictionary
        """
        combined_settings = {}
        
        for component in self.tab_components:
            component_settings = component.get_settings_data()
            # Merge dictionaries
            for key, value in component_settings.items():
                combined_settings[key] = value
        
        return combined_settings
    
    def _save_settings(self):
        """Save all settings to user config."""
        try:
            # Validate all settings first
            is_valid, error_msg = self._validate_all_settings()
            if not is_valid:
                messagebox.showerror("Validation Error", error_msg)
                return
            
            # Collect settings from all components
            new_settings = self._collect_all_settings()
            
            # Additional validation for paths if they exist
            if not self._validate_paths_with_user_confirmation(new_settings):
                return
            
            # Save to config
            if self.user_config.update_all_settings(new_settings):
                messagebox.showinfo("Success", "Settings saved successfully!")
                
                # Call callback if provided
                if self.callback:
                    self.callback()
                
                self.window.destroy()
            else:
                messagebox.showerror(
                    "Error", "Failed to save settings. Please try again."
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def _validate_paths_with_user_confirmation(self, settings):
        """
        Validate paths and ask user for confirmation if paths don't exist.
        
        Args:
            settings: Settings dictionary to validate
            
        Returns:
            bool: True if validation passes or user confirms, False otherwise
        """
        paths_settings = settings.get('paths', {})
        mkvmerge_path = paths_settings.get('mkvmerge_path', '').strip()
        
        # Check MKVMerge path specifically
        if mkvmerge_path and not os.path.exists(mkvmerge_path):
            result = messagebox.askyesno(
                "Warning",
                f"MKVMerge path '{mkvmerge_path}' does not exist. "
                "Save anyway?"
            )
            if not result:
                return False
        
        return True
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        result = messagebox.askyesno(
            "Confirm Reset",
            "Are you sure you want to reset all settings to defaults? "
            "This cannot be undone."
        )
        
        if result:
            try:
                if self.user_config.reset_to_defaults():
                    messagebox.showinfo("Success", "Settings reset to defaults!")
                    self.window.destroy()
                else:
                    messagebox.showerror("Error", "Failed to reset settings.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {str(e)}")
    

