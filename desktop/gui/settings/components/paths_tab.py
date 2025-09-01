#!/usr/bin/env python3
"""
Paths Tab Component

Handles the paths and executables configuration tab.
"""

import tkinter as tk
from tkinter import ttk, filedialog
import os
from typing import Tuple, Optional, Dict

from .base_tab import BaseTabComponent
from .scrollable_tab import ScrollableTabMixin


class PathsTabComponent(BaseTabComponent, ScrollableTabMixin):
    """
    Tab component for configuring application paths and executables.
    
    Allows users to set:
    - MKVMerge executable path
    - Default MKV input folder
    - Default output folder
    """
    
    def get_tab_name(self) -> str:
        """Return the display name for this tab."""
        return "Paths & Executables"
    
    def create_content(self):
        """Create the paths configuration interface."""
        # Create scrollable content
        canvas, scrollable_frame = self.create_scrollable_frame(self.frame)
        
        self.setup_variables()
        self._create_mkvmerge_section(scrollable_frame)
        self._create_folders_section(scrollable_frame)
        self._create_info_section(scrollable_frame)
    
    def setup_variables(self):
        """Setup tkinter variables for form controls."""
        paths_settings = self.settings.get('paths', {})
        
        self.variables = {
            'mkvmerge_path': tk.StringVar(
                value=paths_settings.get('mkvmerge_path', '')
            ),
            'mkv_folder': tk.StringVar(
                value=paths_settings.get('mkv_folder', '')
            ),
            'output_folder': tk.StringVar(
                value=paths_settings.get('output_folder', '')
            )
        }
    
    def _create_mkvmerge_section(self, parent):
        """Create the MKVMerge executable path section."""
        # Section label
        mkvmerge_label = self.create_label(
            parent, "MKVMerge Executable Path:", bold=True
        )
        mkvmerge_label.pack(anchor='w', pady=(10, 5))
        
        # Entry with browse and auto-detect buttons
        mkvmerge_frame = ttk.Frame(parent, style='Modern.TFrame')
        mkvmerge_frame.pack(fill='x', pady=(0, 10))
        
        # Entry field
        entry = ttk.Entry(
            mkvmerge_frame,
            textvariable=self.variables['mkvmerge_path'],
            font=('Segoe UI', 10),
            style='Modern.TEntry'
        )
        entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        # Browse button
        browse_btn = ttk.Button(
            mkvmerge_frame,
            text="Browse...",
            style='Modern.TButton',
            command=lambda: self._browse_file(
                self.variables['mkvmerge_path'],
                "Select MKVMerge executable"
            )
        )
        browse_btn.pack(side='right', padx=(0, 10))
        
        # Auto-detect button
        auto_detect_btn = ttk.Button(
            mkvmerge_frame,
            text="Auto-detect",
            style='Modern.TButton',
            command=self._auto_detect_mkvmerge
        )
        auto_detect_btn.pack(side='right')
        
        # Info text
        info_text = self.create_info_text(
            parent,
            "Use 'Auto-detect' to automatically find MKVMerge on your system, "
            "or 'Browse' to manually select the executable.",
            wrap_length=600
        )
        info_text.pack(anchor='w', pady=(0, 15))
    
    def _create_folders_section(self, parent):
        """Create the folder configuration section."""
        # Default MKV Folder
        mkv_folder_label = self.create_label(
            parent, "Default MKV Input Folder:", bold=True
        )
        mkv_folder_label.pack(anchor='w', pady=(10, 5))
        
        mkv_folder_frame = self.create_entry_with_browse(
            parent,
            self.variables['mkv_folder'],
            lambda: self._browse_folder(
                self.variables['mkv_folder'],
                "Select default MKV input folder"
            )
        )
        mkv_folder_frame.pack(fill='x', pady=(0, 15))
        
        # Default Output Folder
        output_folder_label = self.create_label(
            parent, "Default Output Folder:", bold=True
        )
        output_folder_label.pack(anchor='w', pady=(10, 5))
        
        output_folder_frame = self.create_entry_with_browse(
            parent,
            self.variables['output_folder'],
            lambda: self._browse_folder(
                self.variables['output_folder'],
                "Select default output folder"
            )
        )
        output_folder_frame.pack(fill='x', pady=(0, 15))
    
    def _create_info_section(self, parent):
        """Create the informational text section."""
        info_text = self.create_info_text(
            parent,
            "Note: These paths will be used as defaults when the application starts. "
            "You can still override them in the main interface for individual operations."
        )
        info_text.pack(anchor='w', pady=(20, 10))
    
    def _browse_file(self, var, title):
        """
        Browse for a file and update the given variable.
        
        Args:
            var: tkinter StringVar to update
            title: Dialog title
        """
        filename = filedialog.askopenfilename(
            title=title,
            parent=self.parent
        )
        if filename:
            var.set(filename)
    
    def _browse_folder(self, var, title):
        """
        Browse for a folder and update the given variable.
        
        Args:
            var: tkinter StringVar to update
            title: Dialog title
        """
        folder = filedialog.askdirectory(
            title=title,
            parent=self.parent
        )
        if folder:
            var.set(folder)
    
    def _auto_detect_mkvmerge(self):
        """Auto-detect mkvmerge executable and update the path"""
        from tkinter import messagebox
        
        # Store the current path before we start
        old_path = self.variables['mkvmerge_path'].get()
        
        try:
            from core.config.user_config import find_mkvmerge, verify_mkvmerge
            
            # Show a progress message
            self.variables['mkvmerge_path'].set("Detecting...")
            self.parent.update()  # Force GUI update
            
            # Try to detect mkvmerge
            detected_path = find_mkvmerge()
            
            # Verify it works
            is_working, info = verify_mkvmerge(detected_path)
            
            if is_working:
                self.variables['mkvmerge_path'].set(detected_path)
                messagebox.showinfo(
                    "Auto-detect Success", 
                    f"✅ Found mkvmerge!\n\nPath: {detected_path}\n{info}"
                )
            else:
                # Restore old path on failure
                self.variables['mkvmerge_path'].set(old_path)
                messagebox.showwarning(
                    "Auto-detect Failed", 
                    f"❌ Could not find a working mkvmerge installation.\n\n"
                    f"Error: {info}\n\n"
                    f"Please install MKVToolNix or browse for the executable manually."
                )
                
        except Exception as e:
            # Restore old path on error
            self.variables['mkvmerge_path'].set(old_path)
            messagebox.showerror(
                "Auto-detect Error", 
                f"An error occurred during auto-detection:\n{str(e)}"
            )
    
    def validate_settings(self) -> Tuple[bool, Optional[str]]:
        """
        Validate the current path settings.
        
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        # Validate mkvmerge path if it's specified
        mkvmerge_path = self.variables['mkvmerge_path'].get().strip()
        if mkvmerge_path:
            # Try to verify mkvmerge works
            try:
                from core.config.user_config import verify_mkvmerge
                is_working, info = verify_mkvmerge(mkvmerge_path)
                if not is_working:
                    return False, f"MKVMerge validation failed: {info}"
            except ImportError:
                # Fallback to simple existence check for full paths
                if os.path.sep in mkvmerge_path and not os.path.exists(mkvmerge_path):
                    return False, f"MKVMerge path '{mkvmerge_path}' does not exist."
        
        # For folders, just create them if they don't exist - keep it simple
        mkv_folder = self.variables['mkv_folder'].get().strip()
        if mkv_folder:
            try:
                os.makedirs(mkv_folder, exist_ok=True)
            except OSError as e:
                return False, f"Cannot create MKV input folder '{mkv_folder}': {e}"
        
        output_folder = self.variables['output_folder'].get().strip()
        if output_folder:
            try:
                os.makedirs(output_folder, exist_ok=True)
            except OSError as e:
                return False, f"Cannot create output folder '{output_folder}': {e}"
        
        return True, None
    
    def get_settings_data(self) -> Dict:
        """
        Get the current path settings.
        
        Returns:
            dict: Dictionary containing path settings
        """
        return {
            'paths': {
                'mkvmerge_path': self.variables['mkvmerge_path'].get().strip(),
                'mkv_folder': self.variables['mkv_folder'].get().strip(),
                'output_folder': self.variables['output_folder'].get().strip()
            }
        }
