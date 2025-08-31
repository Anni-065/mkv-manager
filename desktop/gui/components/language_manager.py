#!/usr/bin/env python3
"""
Language Manager Window for MKV Cleaner Desktop Application
Advanced settings for managing available languages
"""

from gui.utils import get_icon
from styles import UIHelpers
from core.config.constants import LANG_TITLES
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
components_dir = os.path.dirname(current_dir)
gui_dir = os.path.dirname(components_dir)
desktop_dir = os.path.dirname(gui_dir)
root_dir = os.path.dirname(desktop_dir)
sys.path.insert(0, root_dir)
sys.path.insert(0, desktop_dir)
sys.path.insert(0, gui_dir)

# Import image utilities


class LanguageManagerWindow:
    """Advanced language settings manager window"""

    def __init__(self, parent, colors, current_audio_langs, current_sub_langs, callback):
        self.parent = parent
        self.colors = colors
        self.callback = callback

        self.audio_langs = set(current_audio_langs)
        self.sub_langs = set(current_sub_langs)

        self.window = tk.Toplevel(parent)
        self.window.title("Language Manager - Advanced Settings")
        self.window.geometry("800x600")
        self.window.configure(bg=colors['bg'])
        self.window.transient(parent)

        self.center_window()
        self.create_interface()
        
        self.window.after(1, self.window.grab_set)

    def center_window(self):
        """Center the window on the parent"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"800x600+{x}+{y}")

    def create_interface(self):
        """Create the main interface"""
        header_frame = ttk.Frame(self.window, style='Modern.TFrame')
        header_frame.pack(fill='x', padx=20, pady=20)

        title_label = ttk.Label(
            header_frame,
            text="Language Manager",
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack(side='left')

        info_label = ttk.Label(
            header_frame,
            text="Configure which languages appear in the main language settings",
            font=('Segoe UI', 10)
        )
        info_label.pack(side='left', padx=(20, 0))

        content_frame = ttk.Frame(self.window, style='Modern.TFrame')
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True)

        self.audio_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(self.audio_frame, text="Audio Languages")
        self.create_audio_tab()

        self.subtitle_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(self.subtitle_frame, text="Subtitle Languages")
        self.create_subtitle_tab()

        buttons_frame = ttk.Frame(self.window, style='Modern.TFrame')
        buttons_frame.pack(fill='x', padx=20, pady=(0, 20))

        ttk.Frame(buttons_frame).pack(side='left', expand=True)

        save_btn = UIHelpers.create_image_button(
            buttons_frame, text="Save Changes",
            command=self.save_changes,
            button_type="success", colors=self.colors, icon_type="save",
            width=150, height=35
        )

        if save_btn:
            save_btn.pack(side='right')

    def create_audio_tab(self):
        """Create the audio languages tab"""
        search_frame = ttk.Frame(self.audio_frame, style='Modern.TFrame')
        search_frame.pack(fill='x', padx=20, pady=20)

        # Get search icon
        search_icon = get_icon('search')

        if search_icon:
            search_label = ttk.Label(
                search_frame, image=search_icon, compound='left', text="Search:")
        else:
            search_label = ttk.Label(
                search_frame, text="Search:", font=('Segoe UI', 10))

        search_label.pack(side='left')
        self.audio_search_var = tk.StringVar()
        self.audio_search_var.trace(
            'w', lambda *args: self.filter_languages('audio'))

        search_entry = ttk.Entry(
            search_frame, textvariable=self.audio_search_var,
            width=30
        )
        search_entry.pack(side='left', padx=(10, 20))

        select_all_btn = UIHelpers.create_button(
            search_frame, text="Select All",
            command=lambda: self.select_all_languages('audio'),
            button_type="primary", colors=self.colors, width=80, height=25
        )
        if select_all_btn:
            select_all_btn.pack(side='left', padx=(0, 10))

        clear_all_btn = UIHelpers.create_button(
            search_frame, text="Clear All",
            command=lambda: self.clear_all_languages('audio'),
            button_type="secondary", colors=self.colors, width=80, height=25
        )
        if clear_all_btn:
            clear_all_btn.pack(side='left')

        languages_container = ttk.Frame(
            self.audio_frame, style='Modern.TFrame')
        languages_container.pack(
            fill='both', expand=True, padx=20, pady=(0, 20))

        canvas = tk.Canvas(languages_container,
                           bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            languages_container, orient="vertical", command=canvas.yview)
        self.audio_scrollable_frame = ttk.Frame(canvas, style='Modern.TFrame')

        self.audio_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window(
            (0, 0), window=self.audio_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)

        self.audio_vars = {}
        self.audio_checkboxes = {}
        self.populate_language_checkboxes('audio')

    def create_subtitle_tab(self):
        """Create the subtitle languages tab"""
        search_frame = ttk.Frame(self.subtitle_frame, style='Modern.TFrame')
        search_frame.pack(fill='x', padx=20, pady=20)

        search_icon = get_icon('search')

        if search_icon:
            search_label = ttk.Label(
                search_frame, image=search_icon, compound='left', text="Search:")
        else:
            search_label = ttk.Label(
                search_frame, text="Search:", font=('Segoe UI', 10))

        search_label.pack(side='left')
        self.subtitle_search_var = tk.StringVar()
        self.subtitle_search_var.trace(
            'w', lambda *args: self.filter_languages('subtitle'))

        search_entry = ttk.Entry(
            search_frame, textvariable=self.subtitle_search_var,
            width=30
        )
        search_entry.pack(side='left', padx=(10, 20))

        select_all_btn = UIHelpers.create_button(
            search_frame, text="Select All",
            command=lambda: self.select_all_languages('subtitle'),
            button_type="primary", colors=self.colors, width=80, height=25
        )
        if select_all_btn:
            select_all_btn.pack(side='left', padx=(0, 10))

        clear_all_btn = UIHelpers.create_button(
            search_frame, text="Clear All",
            command=lambda: self.clear_all_languages('subtitle'),
            button_type="secondary", colors=self.colors, width=80, height=25
        )
        if clear_all_btn:
            clear_all_btn.pack(side='left')

        languages_container = ttk.Frame(
            self.subtitle_frame, style='Modern.TFrame')
        languages_container.pack(
            fill='both', expand=True, padx=20, pady=(0, 20))

        canvas = tk.Canvas(languages_container,
                           bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            languages_container, orient="vertical", command=canvas.yview)
        self.subtitle_scrollable_frame = ttk.Frame(
            canvas, style='Modern.TFrame')

        self.subtitle_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window(
            (0, 0), window=self.subtitle_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)

        self.subtitle_vars = {}
        self.subtitle_checkboxes = {}
        self.populate_language_checkboxes('subtitle')

    def populate_language_checkboxes(self, lang_type):
        """Populate checkboxes for languages"""
        if lang_type == 'audio':
            parent_frame = self.audio_scrollable_frame
            vars_dict = self.audio_vars
            checkboxes_dict = self.audio_checkboxes
            selected_langs = self.audio_langs
        else:
            parent_frame = self.subtitle_scrollable_frame
            vars_dict = self.subtitle_vars
            checkboxes_dict = self.subtitle_checkboxes
            selected_langs = self.sub_langs

        for widget in parent_frame.winfo_children():
            widget.destroy()

        sorted_langs = sorted(LANG_TITLES.items(), key=lambda x: x[1])

        row = 0
        col = 0

        for lang_code, lang_name in sorted_langs:
            if lang_code == "und":
                continue

            var = tk.BooleanVar()
            var.set(lang_code in selected_langs)
            vars_dict[lang_code] = var

            checkbox = ttk.Checkbutton(
                parent_frame,
                text=f"{lang_code} - {lang_name}",
                variable=var,
                style='Modern.TCheckbutton'
            )
            checkbox.grid(row=row, column=col, sticky='w', padx=10, pady=2)
            checkboxes_dict[lang_code] = checkbox

            col += 1
            if col > 2:
                col = 0
                row += 1

    def filter_languages(self, lang_type):
        """Filter languages based on search text"""
        if lang_type == 'audio':
            search_text = self.audio_search_var.get().lower()
            checkboxes_dict = self.audio_checkboxes
        else:
            search_text = self.subtitle_search_var.get().lower()
            checkboxes_dict = self.subtitle_checkboxes

        for lang_code, checkbox in checkboxes_dict.items():
            lang_name = LANG_TITLES.get(lang_code, "").lower()
            if search_text in lang_code.lower() or search_text in lang_name:
                checkbox.grid()
            else:
                checkbox.grid_remove()

    def select_all_languages(self, lang_type):
        """Select all visible languages"""
        if lang_type == 'audio':
            vars_dict = self.audio_vars
            checkboxes_dict = self.audio_checkboxes
        else:
            vars_dict = self.subtitle_vars
            checkboxes_dict = self.subtitle_checkboxes

        for lang_code, checkbox in checkboxes_dict.items():
            if checkbox.winfo_viewable():
                vars_dict[lang_code].set(True)

    def clear_all_languages(self, lang_type):
        """Clear all visible languages"""
        if lang_type == 'audio':
            vars_dict = self.audio_vars
            checkboxes_dict = self.audio_checkboxes
        else:
            vars_dict = self.subtitle_vars
            checkboxes_dict = self.subtitle_checkboxes

        for lang_code, checkbox in checkboxes_dict.items():
            if checkbox.winfo_viewable():
                vars_dict[lang_code].set(False)

    def save_changes(self):
        """Save the language changes"""
        new_audio_langs = {code for code,
                           var in self.audio_vars.items() if var.get()}
        new_sub_langs = {code for code,
                         var in self.subtitle_vars.items() if var.get()}

        if not new_audio_langs:
            messagebox.showerror(
                "No Audio Languages",
                "Please select at least one audio language.",
                parent=self.window
            )
            return

        if not new_sub_langs:
            messagebox.showerror(
                "No Subtitle Languages",
                "Please select at least one subtitle language.",
                parent=self.window
            )
            return

        self.callback(new_audio_langs, new_sub_langs)
        self.window.destroy()
