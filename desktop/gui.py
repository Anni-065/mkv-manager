#!/usr/bin/env python3
"""
Modern GUI for MKV Cleaner Desktop Application
"""

from controllers import MKVCleanerController
from core.constants import LANG_TITLES
from styles import ModernStyleManager, ModernColorScheme, UIHelpers, ICONS
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


try:
    from core.config import *
    print("✅ Using personal config.py")
except ImportError:
    try:
        from core.config_example import *
        print("⚠️ Using config_example.py - Consider creating a personal config.py")
    except ImportError:
        print("❌ No configuration file found!")
        sys.exit(1)


class MKVCleanerGUI:
    """GUI class for the MKV Cleaner application"""

    def __init__(self):
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()

        self.root.title("MKV Cleaner")
        self.root.geometry("1000x800")

        self.controller = MKVCleanerController(self)

        self.color_scheme = ModernColorScheme()
        self.style_manager = ModernStyleManager(self.color_scheme)
        self.style_manager.setup_all_styles()

        self.colors = self.color_scheme.get_all_colors()

        self.root.configure(bg=self.colors['bg'])

        self.output_option = tk.StringVar(value="same_folder")
        self.custom_folder = tk.StringVar()
        self.extract_subtitles = tk.BooleanVar(
            value=globals().get('EXTRACT_SUBTITLES', False))
        self.save_extracted_subtitles = tk.BooleanVar(
            value=globals().get('SAVE_EXTRACTED_SUBTITLES', False))

        self.audio_lang_vars = {}
        self.subtitle_lang_vars = {}
        self.default_audio_var = tk.StringVar()
        self.default_subtitle_var = tk.StringVar()
        self.original_audio_var = tk.StringVar()
        self.original_subtitle_var = tk.StringVar()

        self.language_settings_expanded = tk.BooleanVar(value=False)

        self.init_language_vars()
        self.create_interface()
        self.setup_drag_drop()
        self.controller.update_process_button_state()

    def init_language_vars(self):
        """Initialize language variables with default values for configured languages only"""

        for lang_code in ALLOWED_AUDIO_LANGS:
            if lang_code in LANG_TITLES:
                var = tk.BooleanVar()
                var.set(True)
                self.audio_lang_vars[lang_code] = var

        for lang_code in ALLOWED_SUB_LANGS:
            if lang_code in LANG_TITLES:
                var = tk.BooleanVar()
                var.set(True)
                self.subtitle_lang_vars[lang_code] = var

        self.default_audio_var.set(
            f"{DEFAULT_AUDIO_LANG} - {LANG_TITLES.get(DEFAULT_AUDIO_LANG, 'Unknown')}")
        self.default_subtitle_var.set(
            f"{DEFAULT_SUBTITLE_LANG} - {LANG_TITLES.get(DEFAULT_SUBTITLE_LANG, 'Unknown')}")
        self.original_audio_var.set(
            f"{ORIGINAL_AUDIO_LANG} - {LANG_TITLES.get(ORIGINAL_AUDIO_LANG, 'Unknown')}")
        self.original_subtitle_var.set(
            f"{ORIGINAL_SUBTITLE_LANG} - {LANG_TITLES.get(ORIGINAL_SUBTITLE_LANG, 'Unknown')}")

    def setup_drag_drop(self):
        if DND_AVAILABLE:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.controller.on_drop)

    def toggle_language_settings(self):
        current_state = self.language_settings_expanded.get()
        self.language_settings_expanded.set(not current_state)
        self.update_language_settings_visibility()

    def update_language_settings_visibility(self):
        if hasattr(self, 'language_settings_content'):
            if self.language_settings_expanded.get():
                self.language_settings_header.grid_remove()
                self.language_settings_content.config(
                    text="  🌐 Language Settings     ▼   ")
                self.language_settings_content.grid()
            else:
                self.language_settings_content.grid_remove()
                self.language_settings_header.config(
                    text="  🌐 Language Settings     ▶   ")
                self.language_settings_header.grid()

    def create_interface(self):
        """Create the main interface"""
        self.canvas = tk.Canvas(
            self.root, bg=self.colors['bg'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style='Modern.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind('<Configure>', self._on_canvas_configure)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.root.update_idletasks()
        scrollbar_width = self.scrollbar.winfo_reqwidth()

        left_padding = 20
        right_padding = 20 + (scrollbar_width // 2)

        main_frame = ttk.Frame(self.scrollable_frame, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=(
            left_padding, right_padding), pady=20)

        self.create_header(main_frame)
        self.create_language_settings(main_frame)
        self.create_file_section(main_frame)
        self.create_output_section(main_frame)
        self.create_process_section(main_frame)

        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        self.bind_mousewheel()

    def create_header(self, parent):
        """Create the header section"""
        header_frame = ttk.Frame(parent, style='Modern.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ttk.Label(header_frame, text="MKV Cleaner",
                                style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky='w')

        if DND_AVAILABLE:
            drop_label = ttk.Label(header_frame, text="💡 Drag and drop MKV files or folders anywhere in this window",
                                   style='Subtitle.TLabel')
            drop_label.grid(row=1, column=0,  sticky='w', pady=(0, 10))

    def create_language_settings(self, parent):
        lang_container = ttk.Frame(parent, style='Modern.TFrame')
        lang_container.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        lang_container.grid_columnconfigure(0, weight=1)

        self.language_settings_header = ttk.LabelFrame(lang_container, text="  🌐 Language Settings     ▶   ",
                                                       style='Modern.TLabelframe')
        self.language_settings_header.grid(row=0, column=0, sticky='ew')
        self.language_settings_header.grid_columnconfigure(0, weight=1)

        header_padding = ttk.Frame(
            self.language_settings_header, style='Modern.TFrame')
        header_padding.grid(row=0, column=0, sticky='ew', padx=5, pady=20)

        self.language_settings_header.bind(
            "<Button-1>", lambda e: self.toggle_language_settings())

        self.language_settings_content = ttk.LabelFrame(lang_container, text="",
                                                        style='Modern.TLabelframe')
        self.language_settings_content.grid(row=0, column=0, sticky='ew')
        self.language_settings_content.grid_columnconfigure(0, weight=1)
        self.language_settings_content.grid_columnconfigure(1, weight=1)

        self.language_settings_content.bind(
            "<Button-1>", lambda e: self.toggle_language_settings())

        # Inner content frame
        self.language_settings_inner = ttk.Frame(
            self.language_settings_content, style='Modern.TFrame')
        self.language_settings_inner.grid(
            row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        self.language_settings_inner.grid_columnconfigure(0, weight=1)
        self.language_settings_inner.grid_columnconfigure(1, weight=1)

        # Audio section
        audio_frame = ttk.Frame(
            self.language_settings_inner, style='Modern.TFrame')
        audio_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        audio_label = ttk.Label(audio_frame, text="🎵 Audio Languages",
                                style='SectionHeader.TLabel')
        audio_label.grid(row=0, column=0, sticky='w', pady=(0, 10))

        audio_check_frame = ttk.Frame(audio_frame, style='Modern.TFrame')
        audio_check_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))

        row = 0
        col = 0

        for lang_code in ALLOWED_AUDIO_LANGS:
            if lang_code in self.audio_lang_vars and lang_code in LANG_TITLES:
                lang_name = LANG_TITLES[lang_code]
                checkbox = ttk.Checkbutton(
                    audio_check_frame,
                    text=f"{lang_code} - {lang_name}",
                    variable=self.audio_lang_vars[lang_code],
                    command=self.controller.update_language_settings,
                    style='Modern.TCheckbutton'
                )
                checkbox.grid(row=row, column=col, sticky='w',
                              padx=(0, 20), pady=2)
                col += 1
                if col > 2:
                    col = 0
                    row += 1

        default_audio_label = ttk.Label(audio_frame, text="Default Audio:",
                                        style='Modern.TLabel')
        default_audio_label.grid(row=2, column=0, sticky='w', pady=(10, 5))

        default_audio_combo = ttk.Combobox(
            audio_frame, textvariable=self.default_audio_var,
            values=[
                f"{code} - {LANG_TITLES[code]}" for code in ALLOWED_AUDIO_LANGS if code in LANG_TITLES],
            state='readonly', style='Modern.TCombobox'
        )
        default_audio_combo.grid(row=3, column=0, sticky='ew', pady=(0, 10))
        default_audio_combo.bind(
            '<<ComboboxSelected>>', self.controller.update_language_settings)

        original_audio_label = ttk.Label(audio_frame, text="Original Audio:",
                                         style='Modern.TLabel')
        original_audio_label.grid(row=4, column=0, sticky='w', pady=(0, 5))

        original_audio_combo = ttk.Combobox(
            audio_frame, textvariable=self.original_audio_var,
            values=[
                f"{code} - {LANG_TITLES[code]}" for code in ALLOWED_AUDIO_LANGS if code in LANG_TITLES],
            state='readonly', style='Modern.TCombobox'
        )
        original_audio_combo.grid(row=5, column=0, sticky='ew')
        original_audio_combo.bind(
            '<<ComboboxSelected>>', self.controller.update_language_settings)

        # Subtitle section
        subtitle_frame = ttk.Frame(
            self.language_settings_inner, style='Modern.TFrame')
        subtitle_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)

        subtitle_label = ttk.Label(subtitle_frame, text="📝 Subtitle Languages",
                                   style='SectionHeader.TLabel')
        subtitle_label.grid(row=0, column=0, sticky='w', pady=(0, 10))

        subtitle_check_frame = ttk.Frame(subtitle_frame, style='Modern.TFrame')
        subtitle_check_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))

        row = 0
        col = 0

        for lang_code in ALLOWED_SUB_LANGS:
            if lang_code in self.subtitle_lang_vars and lang_code in LANG_TITLES:
                lang_name = LANG_TITLES[lang_code]
                checkbox = ttk.Checkbutton(
                    subtitle_check_frame,
                    text=f"{lang_code} - {lang_name}",
                    variable=self.subtitle_lang_vars[lang_code],
                    command=self.controller.update_language_settings,
                    style='Modern.TCheckbutton'
                )
                checkbox.grid(row=row, column=col, sticky='w',
                              padx=(0, 20), pady=2)
                col += 1
                if col > 2:
                    col = 0
                    row += 1

        default_subtitle_label = ttk.Label(subtitle_frame, text="Default Subtitle:",
                                           style='Modern.TLabel')
        default_subtitle_label.grid(row=2, column=0, sticky='w', pady=(10, 5))

        default_subtitle_combo = ttk.Combobox(
            subtitle_frame, textvariable=self.default_subtitle_var,
            values=[
                f"{code} - {LANG_TITLES[code]}" for code in ALLOWED_SUB_LANGS if code in LANG_TITLES],
            state='readonly', style='Modern.TCombobox'
        )
        default_subtitle_combo.grid(row=3, column=0, sticky='ew', pady=(0, 10))
        default_subtitle_combo.bind(
            '<<ComboboxSelected>>', self.controller.update_language_settings)

        original_subtitle_label = ttk.Label(subtitle_frame, text="Original Subtitle:",
                                            style='Modern.TLabel')
        original_subtitle_label.grid(row=4, column=0, sticky='w', pady=(0, 5))

        all_configured_langs = list(
            ALLOWED_AUDIO_LANGS.union(ALLOWED_SUB_LANGS))
        original_subtitle_combo = ttk.Combobox(
            subtitle_frame, textvariable=self.original_subtitle_var,
            values=[
                f"{code} - {LANG_TITLES[code]}" for code in all_configured_langs if code in LANG_TITLES],
            state='readonly', style='Modern.TCombobox'
        )
        original_subtitle_combo.grid(row=5, column=0, sticky='ew')
        original_subtitle_combo.bind(
            '<<ComboboxSelected>>', self.controller.update_language_settings)

        subtitle_processing_label = ttk.Label(subtitle_frame, text="🔄 Subtitle Processing:",
                                              style='SectionHeader.TLabel')
        subtitle_processing_label.grid(
            row=6, column=0, sticky='w', pady=(15, 5))

        extract_subtitles_check = ttk.Checkbutton(
            subtitle_frame,
            text="Convert subtitles to SRT format",
            variable=self.extract_subtitles,
            command=self.controller.update_language_settings,
            style='Modern.TCheckbutton'
        )
        extract_subtitles_check.grid(row=7, column=0, sticky='w', pady=(0, 5))

        save_extracted_check = ttk.Checkbutton(
            subtitle_frame,
            text="Save extracted SRT files next to processed MKV",
            variable=self.save_extracted_subtitles,
            command=self.controller.update_language_settings,
            style='Modern.TCheckbutton'
        )
        save_extracted_check.grid(row=8, column=0, sticky='w', pady=(0, 10))

        save_btn = UIHelpers.create_button(
            self.language_settings_inner, text="💾 Save Settings", command=self.controller.save_language_settings,
            button_type="success", colors=self.colors, width=120, height=35
        )
        save_btn.grid(row=1, column=0, columnspan=2, pady=(10, 15))

        self.update_language_settings_visibility()

    def create_file_section(self, parent):
        """Create the file selection section"""
        file_frame = ttk.LabelFrame(parent, text="  📁 File Selection  ",
                                    style='Modern.TLabelframe')
        file_frame.grid(row=2, column=0, sticky='nsew', pady=(0, 20))
        file_frame.grid_columnconfigure(0, weight=1)
        file_frame.grid_rowconfigure(1, weight=1)

        button_frame = ttk.Frame(file_frame, style='Modern.TFrame')
        button_frame.grid(row=0, column=0, sticky='ew', padx=15, pady=15)

        browse_files_btn = UIHelpers.create_button(
            button_frame, text="📄 Select Files", command=self.controller.browse_files,
            button_type="primary", colors=self.colors, width=120, height=35
        )
        browse_files_btn.grid(row=0, column=0, padx=(0, 10))

        browse_folder_btn = UIHelpers.create_button(
            button_frame, text="📁 Select Folder", command=self.controller.browse_folder,
            button_type="secondary", colors=self.colors, width=120, height=35
        )
        browse_folder_btn.grid(row=0, column=1, padx=(0, 10))

        clear_btn = UIHelpers.create_button(
            button_frame, text="Clear All", command=self.controller.clear_selection,
            button_type="danger", colors=self.colors, width=80, height=35
        )
        clear_btn.grid(row=0, column=2)

        list_frame = ttk.Frame(file_frame, style='Modern.TFrame')
        list_frame.grid(row=1, column=0, sticky='nsew', padx=15, pady=(0, 15))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        columns = ('Name', 'Path', 'Size', 'Series')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                      style='Modern.Treeview')

        self.file_tree.heading('Name', text='File Name')
        self.file_tree.heading('Path', text='Location')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Series', text='Series Info')

        self.file_tree.column('Name', width=300)
        self.file_tree.column('Path', width=350)
        self.file_tree.column('Size', width=80)
        self.file_tree.column('Series', width=220)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.file_tree.yview,
                                  style='Modern.Vertical.TScrollbar')
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        self.file_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

    def create_output_section(self, parent):
        """Create the output options section"""
        output_frame = ttk.LabelFrame(parent, text="  📂 Output Options  ",
                                      style='Modern.TLabelframe')
        output_frame.grid(row=3, column=0, sticky='ew', pady=(0, 20))
        output_frame.grid_columnconfigure(0, weight=1)

        options_frame = ttk.Frame(output_frame, style='Modern.TFrame')
        options_frame.grid(row=0, column=0, sticky='ew', padx=15, pady=15)

        same_folder_radio = ttk.Radiobutton(
            options_frame, text="📁 Same folder (in 'processed' subfolder)",
            variable=self.output_option, value="same_folder",
            style='Modern.TRadiobutton'
        )
        same_folder_radio.grid(row=0, column=0, sticky='w', pady=5)

        downloads_radio = ttk.Radiobutton(
            options_frame, text="📥 Downloads folder",
            variable=self.output_option, value="downloads",
            style='Modern.TRadiobutton'
        )
        downloads_radio.grid(row=1, column=0, sticky='w', pady=5)

        custom_radio = ttk.Radiobutton(
            options_frame, text="📂 Custom folder:",
            variable=self.output_option, value="custom",
            style='Modern.TRadiobutton'
        )
        custom_radio.grid(row=2, column=0, sticky='w', pady=5)

        custom_frame = ttk.Frame(options_frame, style='Modern.TFrame')
        custom_frame.grid(row=3, column=0, sticky='ew', padx=(25, 0), pady=5)
        custom_frame.grid_columnconfigure(0, weight=1)

        custom_entry = ttk.Entry(custom_frame, textvariable=self.custom_folder,
                                 style='Modern.TEntry')
        custom_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))

        browse_custom_btn = UIHelpers.create_button(
            custom_frame, text="Browse", command=self.controller.browse_custom_folder,
            button_type="secondary", colors=self.colors, width=80, height=30
        )
        browse_custom_btn.grid(row=0, column=1)

    def create_process_section(self, parent):
        """Create the process section"""
        process_frame = ttk.Frame(parent, style='Modern.TFrame')
        process_frame.grid(row=4, column=0, sticky='ew')
        process_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ttk.Progressbar(
            process_frame, mode='determinate',
            style='Modern.Horizontal.TProgressbar'
        )
        self.progress_bar.grid(row=0, column=0, sticky='ew', pady=(0, 10))

        self.progress_label = ttk.Label(
            process_frame, text="Ready to process files",
            style='Modern.TLabel'
        )
        self.progress_label.grid(row=1, column=0, pady=(0, 15))

        self.process_button = UIHelpers.create_button(
            process_frame, text="🚀 Process Files", command=self.controller.process_files,
            button_type="secondary", colors=self.colors, width=200, height=45
        )
        self.process_button.grid(row=2, column=0, pady=(0, 10))

    def update_config_display(self):
        """Update the configuration display"""
        pass

    def bind_mousewheel(self):
        """Bind mouse wheel to scrolling"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind("<MouseWheel>", _on_mousewheel)

        def bind_to_mousewheel(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_to_mousewheel(child)

        self.root.after(100, lambda: bind_to_mousewheel(self.root))

    def _on_canvas_configure(self, event):
        """Handle canvas resize events to update scrollable frame width"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MKVCleanerGUI()
    app.run()
