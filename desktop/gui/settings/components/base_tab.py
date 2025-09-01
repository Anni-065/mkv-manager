#!/usr/bin/env python3
"""
Base Tab Component

Provides the foundation for all settings tab components with common functionality.
"""

import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from typing import Union, Dict, Tuple, Optional


class BaseTabComponent(ABC):
    """
    Abstract base class for all settings tab components.
    
    Provides common functionality and enforces a consistent interface
    for all tab components.
    """
    
    def __init__(self, parent, colors, settings, user_config):
        """
        Initialize the base tab component.
        
        Args:
            parent: The parent tkinter widget (usually notebook)
            colors: Dictionary containing color scheme
            settings: Current settings dictionary
            user_config: User configuration manager instance
        """
        self.parent = parent
        self.colors = colors
        self.settings = settings
        self.user_config = user_config
        
        # Create the main frame for this tab
        self.frame = ttk.Frame(parent, style='Modern.TFrame')
        
        # Variables to hold form data - to be populated by subclasses
        self.variables = {}
        
    @abstractmethod
    def create_content(self):
        """
        Create the tab's content. Must be implemented by subclasses.
        
        This method should create all the widgets and layout for the tab.
        """
        pass
    
    @abstractmethod
    def get_tab_name(self) -> str:
        """
        Return the display name for this tab.
        
        Returns:
            str: The name to show in the notebook tab
        """
        pass
    
    @abstractmethod
    def validate_settings(self) -> Tuple[bool, Optional[str]]:
        """
        Validate the current settings in this tab.
        
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        pass
    
    @abstractmethod
    def get_settings_data(self) -> Dict:
        """
        Get the current settings data from this tab.
        
        Returns:
            dict: Dictionary containing the settings for this tab
        """
        pass
    
    def setup_variables(self):
        """
        Setup tkinter variables for form controls.
        Should be called by subclasses in their create_content method.
        """
        pass
    
    def add_to_notebook(self, notebook):
        """
        Add this tab to the given notebook widget.
        
        Args:
            notebook: The ttk.Notebook widget to add this tab to
        """
        notebook.add(self.frame, text=self.get_tab_name())
    
    def create_label(self, parent, text, font_size=11, bold=False, style='Modern.TLabel'):
        """
        Create a standardized label widget.
        
        Args:
            parent: Parent widget
            text: Label text
            font_size: Font size (default: 11)
            bold: Whether to make text bold (default: False)
            style: TTK style to use (default: 'Modern.TLabel')
            
        Returns:
            ttk.Label: The created label widget
        """
        font_weight = 'bold' if bold else 'normal'
        label = ttk.Label(
            parent,
            text=text,
            font=('Segoe UI', font_size, font_weight),
            style=style
        )
        return label
    
    def create_entry_with_browse(self, parent, text_var, browse_command, 
                                 entry_width=None, button_text="Browse..."):
        """
        Create an entry widget with a browse button.
        
        Args:
            parent: Parent widget
            text_var: tkinter StringVar for the entry
            browse_command: Command to execute when browse button is clicked
            entry_width: Width of entry widget (optional)
            button_text: Text for the browse button (default: "Browse...")
            
        Returns:
            ttk.Frame: Frame containing the entry and button
        """
        frame = ttk.Frame(parent, style='Modern.TFrame')
        
        entry_kwargs = {
            'textvariable': text_var,
            'font': ('Segoe UI', 10),
            'style': 'Modern.TEntry'
        }
        if entry_width:
            entry_kwargs['width'] = entry_width
            
        entry = ttk.Entry(frame, **entry_kwargs)
        entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(
            frame,
            text=button_text,
            style='Modern.TButton',
            command=browse_command
        )
        browse_btn.pack(side='right')
        
        return frame
    
    def create_info_text(self, parent, text, wrap_length=800):
        """
        Create an informational text label.
        
        Args:
            parent: Parent widget
            text: Information text
            wrap_length: Text wrap length (default: 800)
            
        Returns:
            ttk.Label: The created info label
        """
        return ttk.Label(
            parent,
            text=text,
            font=('Segoe UI', 9),
            style='Subtitle.TLabel',
            wraplength=wrap_length
        )
