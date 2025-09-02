#!/usr/bin/env python3
"""
Modern styling configuration for MKV Cleaner Desktop GUI
This module contains all color schemes, ttk styles, and UI configuration
"""

import tkinter as tk
from tkinter import ttk
import platform

# lazy import to avoid circular import errors
HAS_IMAGES = None
get_icon = None


def _lazy_import_icons():
    """Lazy import of icon utilities to avoid circular imports"""
    global HAS_IMAGES, get_icon
    if HAS_IMAGES is None:
        try:
            from gui.utils.image_utils import get_icon as _get_icon
            HAS_IMAGES = True
            get_icon = _get_icon
        except ImportError:
            HAS_IMAGES = False
            get_icon = None
    return HAS_IMAGES, get_icon


class ModernColorScheme:
    """Modern color scheme with enhanced contrast and accessibility"""

    def __init__(self):
        self.colors = {
            # Main background colors - pure white throughout
            'bg': '#ffffff',                # Pure white background everywhere
            'card_bg': '#ffffff',           # Pure white for cards
            'surface': '#ffffff',           # Pure white surface

            # Primary accent colors - stronger blues for better contrast
            'accent': '#075fc4',            # GitHub blue - AAA contrast
            'accent_hover': '#0860ca',      # Darker hover state
            'accent_light': '#dbeafe',      # Light blue background
            'accent_dark': '#0550ae',       # Dark blue for high contrast

            # Semantic colors with better contrast ratios
            'success': '#1a7f37',           # Darker green for better contrast
            'success_light': '#dcfce7',     # Light green background
            'success_hover': '#166534',     # Darker green hover

            'danger': '#cf222e',            # Darker red for better contrast
            'danger_light': '#ffeef0',      # Light red background
            'danger_hover': '#a40e26',      # Darker red hover

            # Text colors with enhanced contrast ratios
            'text': '#1f2328',              # Almost black for maximum contrast
            'text_secondary': '#656d76',    # Medium gray for secondary text
            'text_muted': '#8b949e',        # Lighter gray for muted text
            'text_inverse': '#ffffff',      # White text for dark backgrounds

            # Border and divider colors
            'border': '#d1d9e0',            # Visible border color
            'border_light': '#eaeef2',      # Light border
            'border_strong': '#8b949e',     # Strong border for emphasis
            'button_border': '#075fc4',

            # Interactive element colors
            'drop_zone': '#f0f6ff',         # Light blue for drop zone
            'drop_zone_hover': '#e1eeff',   # Darker blue for hover
            'drop_zone_active': '#d2e7ff',  # Active state
            'drop_zone_border': '#075fc4',  # Border color for drop zone

            # Shadow and depth
            'shadow': 'rgba(31, 35, 40, 0.12)',
            'shadow_strong': 'rgba(31, 35, 40, 0.2)',

            # Focus and selection colors
            'focus': '#075fc4',             # Focus ring color
            'selection': '#075fc4',         # Selection background
            'selection_light': '#e6f3ff',   # Light selection background
        }

    def get_color(self, name):
        """Get color by name"""
        return self.colors.get(name, '#000000')

    def get_all_colors(self):
        """Get all colors dictionary"""
        return self.colors.copy()


class ModernStyleManager:
    """Manager for modern ttk styles"""

    def __init__(self, color_scheme):
        self.colors = color_scheme.get_all_colors()
        self.style = ttk.Style()

        available_themes = self.style.theme_names()
        if 'vista' in available_themes:
            self.style.theme_use('vista')
        elif 'winnative' in available_themes:
            self.style.theme_use('winnative')
        elif 'clam' in available_themes:
            self.style.theme_use('clam')
        else:
            pass

    def _setup_frame_styles(self):
        """Configure modern frame styles with enhanced visual hierarchy"""
        # Modern label frame with white background
        self.style.configure('Modern.TLabelframe',
                             background=self.colors['bg'],
                             borderwidth=1,
                             relief='solid',
                             bordercolor=self.colors['border'],
                             lightcolor=self.colors['bg'],
                             darkcolor=self.colors['border'])

        self.style.configure('Modern.TLabelframe.Label',
                             background=self.colors['bg'],
                             font=('Segoe UI', 12, 'bold'),
                             foreground=self.colors['text'],
                             padding=(10, 5))

        # Card-style label frame with subtle shadow effect
        self.style.configure('Card.TLabelframe',
                             background=self.colors['card_bg'],
                             borderwidth=1,
                             relief='solid',
                             bordercolor=self.colors['border'],
                             lightcolor=self.colors['card_bg'],
                             darkcolor=self.colors['border'])

        self.style.configure('Card.TLabelframe.Label',
                             background=self.colors['card_bg'],
                             font=('Segoe UI', 12, 'bold'),
                             foreground=self.colors['text'],
                             padding=(10, 5))

        # Main frame
        self.style.configure('Modern.TFrame',
                             background=self.colors['bg'],
                             borderwidth=0,
                             relief='flat')

        # Card frame for content sections
        self.style.configure('Card.TFrame',
                             background=self.colors['card_bg'],
                             borderwidth=0,
                             relief='flat')

        # Surface frame for elevation
        self.style.configure('Surface.TFrame',
                             background=self.colors['surface'],
                             borderwidth=0,
                             relief='flat')

    def _setup_entry_styles(self):
        """Configure modern entry styles with enhanced accessibility"""
        self.style.configure('Modern.TEntry',
                             fieldbackground=self.colors['bg'],
                             borderwidth=2,
                             relief='solid',
                             bordercolor=self.colors['border'],
                             font=('Segoe UI', 10),
                             padding=(12, 10),
                             focuscolor=self.colors['focus'],
                             foreground=self.colors['text'],
                             selectbackground=self.colors['selection'],
                             selectforeground=self.colors['text_inverse'])

        self.style.map('Modern.TEntry',
                       bordercolor=[('focus', self.colors['accent']),
                                    ('active', self.colors['accent'])],
                       fieldbackground=[('focus', self.colors['bg']),
                                        ('readonly', self.colors['surface'])],
                       foreground=[('disabled', self.colors['text_muted'])])

    def _setup_treeview_styles(self):
        """Configure modern treeview styles with enhanced readability"""
        self.style.configure('Modern.Treeview',
                             background=self.colors['bg'],
                             foreground=self.colors['text'],
                             fieldbackground=self.colors['bg'],
                             font=('Segoe UI', 9),
                             rowheight=32,
                             borderwidth=1,
                             relief='solid',
                             bordercolor=self.colors['border'],
                             selectbackground=self.colors['selection_light'],
                             selectforeground=self.colors['text'])

        self.style.configure('Modern.Treeview.Heading',
                             background=self.colors['surface'],
                             foreground=self.colors['text'],
                             font=('Segoe UI', 9, 'bold'),
                             relief='flat',
                             borderwidth=1,
                             bordercolor=self.colors['border'],
                             padding=(10, 8))

        self.style.map('Modern.Treeview',
                       background=[
                           ('selected', self.colors['selection_light'])],
                       foreground=[('selected', self.colors['text'])],
                       fieldbackground=[('selected', self.colors['selection_light'])])

        self.style.map('Modern.Treeview.Heading',
                       background=[('active', self.colors['border_light']),
                                   ('pressed', self.colors['border'])])

    def _setup_label_styles(self):
        """Configure modern label styles with proper backgrounds"""
        # Modern label style with white background
        self.style.configure('Modern.TLabel',
                             background=self.colors['bg'],
                             foreground=self.colors['text'],
                             font=('Segoe UI', 10),
                             padding=(4, 2),
                             borderwidth=0,
                             relief='flat')

        # Title label style
        self.style.configure('Title.TLabel',
                             background=self.colors['bg'],
                             foreground=self.colors['text'],
                             font=('Segoe UI', 18, 'bold'),
                             padding=(0, 10),
                             borderwidth=0,
                             relief='flat')

        # Subtitle label style
        self.style.configure('Subtitle.TLabel',
                             background=self.colors['bg'],
                             foreground=self.colors['text_secondary'],
                             font=('Segoe UI', 11),
                             padding=(0, 5),
                             borderwidth=0,
                             relief='flat')

        # Section header label style
        self.style.configure('SectionHeader.TLabel',
                             background=self.colors['bg'],
                             foreground=self.colors['text'],
                             font=('Segoe UI', 12, 'bold'),
                             padding=(0, 8),
                             borderwidth=0,
                             relief='flat')

        # Info label style
        self.style.configure('Info.TLabel',
                             background=self.colors['bg'],
                             foreground=self.colors['text_secondary'],
                             font=('Segoe UI', 9, 'italic'),
                             padding=(0, 4),
                             borderwidth=0,
                             relief='flat')

    def _setup_radiobutton_styles(self):
        """Configure modern radiobutton styles with better contrast"""
        self.style.configure('Modern.TRadiobutton',
                             background=self.colors['bg'],
                             foreground=self.colors['text'],
                             font=('Segoe UI', 10),
                             focuscolor=self.colors['focus'],
                             padding=(8, 6),
                             borderwidth=0,
                             relief='flat')

        self.style.map('Modern.TRadiobutton',
                       background=[('active', self.colors['bg']),
                                   ('selected', self.colors['bg'])],
                       foreground=[('disabled', self.colors['text_muted'])])

    def _setup_checkbutton_styles(self):
        """Configure modern checkbutton styles with consistent backgrounds"""
        self.style.configure('Modern.TCheckbutton',
                             background=self.colors['bg'],
                             foreground=self.colors['text'],
                             font=('Segoe UI', 10),
                             focuscolor=self.colors['focus'],
                             padding=(8, 6),
                             borderwidth=0,
                             relief='flat')

        self.style.map('Modern.TCheckbutton',
                       background=[('active', self.colors['bg']),
                                   ('selected', self.colors['bg'])],
                       foreground=[('disabled', self.colors['text_muted'])])

    def _setup_combobox_styles(self):
        """Configure modern combobox styles with consistent backgrounds"""
        self.style.configure('Modern.TCombobox',
                             background=self.colors['bg'],
                             foreground=self.colors['text'],
                             fieldbackground=self.colors['bg'],
                             borderwidth=2,
                             bordercolor=self.colors['border'],
                             lightcolor=self.colors['bg'],
                             darkcolor=self.colors['border'],
                             font=('Segoe UI', 10),
                             padding=(12, 10),
                             relief='solid',
                             arrowcolor=self.colors['text_secondary'])

        self.style.map('Modern.TCombobox',
                       background=[('active', self.colors['bg']),
                                   ('focus', self.colors['bg'])],
                       foreground=[('active', self.colors['text']),
                                   ('focus', self.colors['text'])],
                       fieldbackground=[('active', self.colors['bg']),
                                        ('focus', self.colors['bg'])],
                       bordercolor=[('active', self.colors['accent']),
                                    ('focus', self.colors['accent'])])

    def _setup_progressbar_styles(self):
        """Configure modern progressbar styles with enhanced visibility"""
        self.style.configure('Modern.Horizontal.TProgressbar',
                             background=self.colors['success'],
                             troughcolor=self.colors['border_light'],
                             borderwidth=1,
                             lightcolor=self.colors['success'],
                             darkcolor=self.colors['success_hover'],
                             thickness=14,
                             relief='flat',
                             bordercolor=self.colors['border'],
                             foreground=self.colors['success'])

        self.style.layout('Modern.Horizontal.TProgressbar',
                          [('Horizontal.Progressbar.trough',
                           {'children': [('Horizontal.Progressbar.pbar',
                                          {'side': 'left', 'sticky': 'ns'})],
                            'sticky': 'nswe'})])

        self.style.map('Modern.Horizontal.TProgressbar',
                       background=[('active', self.colors['success']),
                                   ('pressed', self.colors['success_hover'])])

        current_platform = platform.system()
        if current_platform == 'Linux':
            self.style.configure('Modern.Horizontal.TProgressbar',
                                 pbarrelief='flat',
                                 troughrelief='flat')
            
            try:
                self.style.element_options('Horizontal.Progressbar.pbar')
                self.style.configure('Modern.Horizontal.TProgressbar',
                                     pbar=self.colors['success'])
            except tk.TclError:
                pass  # Some Linux systems don't support this
        
        elif current_platform == 'Darwin':  # macOS
            # macOS might need different styling
            self.style.configure('Modern.Horizontal.TProgressbar',
                                 focuscolor='none')
        
    def _setup_scrollbar_styles(self):
        """Configure modern scrollbar styles"""
        self.style.configure('Modern.Vertical.TScrollbar',
                             background=self.colors['surface'],
                             troughcolor=self.colors['border_light'],
                             borderwidth=0,
                             arrowcolor=self.colors['text_secondary'],
                             darkcolor=self.colors['border'],
                             lightcolor=self.colors['card_bg'],
                             gripcount=0,
                             relief='flat')

        self.style.map('Modern.Vertical.TScrollbar',
                       background=[('active', self.colors['border']),
                                   ('pressed', self.colors['border_strong'])])

        self.style.configure('Modern.Horizontal.TScrollbar',
                             background=self.colors['surface'],
                             troughcolor=self.colors['border_light'],
                             borderwidth=0,
                             arrowcolor=self.colors['text_secondary'],
                             darkcolor=self.colors['border'],
                             lightcolor=self.colors['card_bg'],
                             gripcount=0,
                             relief='flat')

        self.style.map('Modern.Horizontal.TScrollbar',
                       background=[('active', self.colors['border']),
                                   ('pressed', self.colors['border_strong'])])

    def setup_all_styles(self):
        self._setup_frame_styles()
        self._setup_label_styles()
        self._setup_entry_styles()
        self._setup_treeview_styles()
        self._setup_radiobutton_styles()
        self._setup_checkbutton_styles()
        self._setup_combobox_styles()
        self._setup_progressbar_styles()
        self._setup_scrollbar_styles()

        self.style.configure(
            'TLabel', background=self.colors['bg'], foreground='#1f2328')

    @staticmethod
    def create_simple_frame(parent, bg_color, border_color=None, padding=10):
        """Create a simple frame with optional border"""

        container = tk.Frame(parent, bg=bg_color, relief='flat', bd=0)

        if border_color:
            inner_frame = tk.Frame(container, bg=bg_color, relief='solid', bd=1,
                                   highlightbackground=border_color, highlightthickness=1,
                                   highlightcolor=border_color)
        else:
            inner_frame = tk.Frame(container, bg=bg_color, relief='flat', bd=0)

        inner_frame.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)

        return container, inner_frame

    @staticmethod
    def create_card(parent, title, colors, padding=20):
        """Create card-style frame with clean modern styling"""

        container = tk.Frame(parent, bg=colors['bg'], relief='flat', bd=0)

        card_frame = tk.Frame(container, bg=colors['card_bg'], relief='solid',
                              bd=1, highlightbackground=colors['border'],
                              highlightcolor=colors['border'], highlightthickness=0)
        card_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        content_frame = tk.Frame(
            card_frame, bg=colors['card_bg'], relief='flat', bd=0)
        content_frame.pack(fill=tk.BOTH, expand=True,
                           padx=padding, pady=padding)

        return container, content_frame


class UIHelpers:
    """Helper functions for UI creation"""

    @staticmethod
    def create_button(parent, text, command, button_type="primary", colors=None, **kwargs):
        if colors is None:
            return None

        button_styles = {
            "primary": {
                "bg": colors['accent'],
                "fg": "white",
                "hover_bg": colors['accent_hover'],
                "active_bg": colors['accent_dark'],
                "border_color": None,
                "border_width": 0
            },
            "success": {
                "bg": colors['success'],
                "fg": "white",
                "hover_bg": colors['success_hover'],
                "active_bg": colors['success_hover'],
                "border_color": None,
                "border_width": 0
            },
            "danger": {
                "bg": colors['danger'],
                "fg": "white",
                "hover_bg": colors['danger_hover'],
                "active_bg": colors['danger_hover'],
                "border_color": None,
                "border_width": 0
            },
            "info": {
                "bg": colors['accent_light'],
                "fg": colors['accent'],
                "hover_bg": colors['accent_light'],
                "active_bg": colors['accent_light'],
                "border_color": colors['accent'],
                "border_width": 1
            },
            "secondary": {
                "bg": colors['card_bg'],
                "fg": colors['button_border'],
                "hover_bg": colors['surface'],
                "active_bg": colors['border_light'],
                "border_color": colors['button_border'],
                "border_width": 2
            }
        }

        style = button_styles.get(button_type, button_styles["primary"])

        padx = kwargs.get('padx', 20)
        pady = kwargs.get('pady', 8)

        try:
            parent_bg = parent.cget('bg')
        except:
            parent_bg = colors['bg']

        container = tk.Frame(parent, bg=parent_bg)

        canvas = tk.Canvas(container, highlightthickness=0,
                           bg=parent_bg, cursor='hand2')

        temp_label = tk.Label(container, text=text,
                              font=('Segoe UI', 10, 'bold'))
        temp_label.update_idletasks()
        text_width = temp_label.winfo_reqwidth()
        text_height = temp_label.winfo_reqheight()
        temp_label.destroy()

        button_width = text_width + (padx * 2)
        button_height = text_height + (pady * 2)
        corner_radius = 8

        canvas.configure(width=button_width, height=button_height)

        def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, fill_color, border_color=None, border_width=0):
            canvas.delete("button_bg")
            canvas.delete("button_border")

            canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2,
                                    fill=fill_color, outline="", tags="button_bg")
            canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius,
                                    fill=fill_color, outline="", tags="button_bg")

            canvas.create_arc(x1, y1, x1 + 2*radius, y1 + 2*radius,
                              start=90, extent=90, fill=fill_color, outline="", tags="button_bg")
            canvas.create_arc(x2 - 2*radius, y1, x2, y1 + 2*radius,
                              start=0, extent=90, fill=fill_color, outline="", tags="button_bg")
            canvas.create_arc(x1, y2 - 2*radius, x1 + 2*radius, y2,
                              start=180, extent=90, fill=fill_color, outline="", tags="button_bg")
            canvas.create_arc(x2 - 2*radius, y2 - 2*radius, x2, y2,
                              start=270, extent=90, fill=fill_color, outline="", tags="button_bg")

            if border_color and border_width > 0:
                canvas.create_rectangle(x1 + radius, y1, x2 - radius, y1 + border_width,
                                        fill=border_color, outline="", tags="button_border")
                canvas.create_rectangle(x1 + radius, y2 - border_width, x2 - radius, y2,
                                        fill=border_color, outline="", tags="button_border")
                canvas.create_rectangle(x1, y1 + radius, x1 + border_width, y2 - radius,
                                        fill=border_color, outline="", tags="button_border")
                canvas.create_rectangle(x2 - border_width, y1 + radius, x2, y2 - radius,
                                        fill=border_color, outline="", tags="button_border")

                corner_size = radius

                for i in range(corner_size):
                    for j in range(corner_size):
                        dx = corner_size - i
                        dy = corner_size - j
                        distance = (dx*dx + dy*dy) ** 0.5

                        if corner_size - border_width <= distance <= corner_size:
                            canvas.create_rectangle(x1 + i, y1 + j, x1 + i + 1, y1 + j + 1,
                                                    fill=border_color, outline="", tags="button_border")

                for i in range(corner_size):
                    for j in range(corner_size):
                        dx = i + 1
                        dy = corner_size - j
                        distance = (dx*dx + dy*dy) ** 0.5

                        if corner_size - border_width <= distance <= corner_size:
                            canvas.create_rectangle(x2 - corner_size + i, y1 + j, x2 - corner_size + i + 1, y1 + j + 1,
                                                    fill=border_color, outline="", tags="button_border")

                for i in range(corner_size):
                    for j in range(corner_size):
                        dx = corner_size - i
                        dy = j + 1
                        distance = (dx*dx + dy*dy) ** 0.5

                        if corner_size - border_width <= distance <= corner_size:
                            canvas.create_rectangle(x1 + i, y2 - corner_size + j, x1 + i + 1, y2 - corner_size + j + 1,
                                                    fill=border_color, outline="", tags="button_border")

                for i in range(corner_size):
                    for j in range(corner_size):
                        dx = i + 1
                        dy = j + 1
                        distance = (dx*dx + dy*dy) ** 0.5

                        if corner_size - border_width <= distance <= corner_size:
                            canvas.create_rectangle(x2 - corner_size + i, y2 - corner_size + j,
                                                    x2 - corner_size + i + 1, y2 - corner_size + j + 1,
                                                    fill=border_color, outline="", tags="button_border")

            canvas.tag_raise("button_text")

        draw_rounded_rect(canvas, 0, 0, button_width,
                          button_height, corner_radius, style["bg"],
                          style.get("border_color"), style.get("border_width", 0))

        text_item = canvas.create_text(button_width//2, button_height//2,
                                       text=text, fill=style["fg"],
                                       font=('Segoe UI', 10, 'bold'), tags="button_text")

        canvas.tag_raise("button_text")

        button_state = {"disabled": False}

        def on_enter(e):
            if not button_state["disabled"]:
                draw_rounded_rect(canvas, 0, 0, button_width, button_height,
                                  corner_radius, style["hover_bg"],
                                  style.get("border_color"), style.get("border_width", 0))
                canvas.itemconfig(text_item, fill=style["fg"])

        def on_leave(e):
            if not button_state["disabled"]:
                draw_rounded_rect(canvas, 0, 0, button_width, button_height,
                                  corner_radius, style["bg"],
                                  style.get("border_color"), style.get("border_width", 0))
                canvas.itemconfig(text_item, fill=style["fg"])

        def on_click(e):
            if not button_state["disabled"]:
                draw_rounded_rect(canvas, 0, 0, button_width, button_height,
                                  corner_radius, style["active_bg"],
                                  style.get("border_color"), style.get("border_width", 0))
                canvas.itemconfig(text_item, fill=style["fg"])
                parent.after(100, lambda: [
                    draw_rounded_rect(
                        canvas, 0, 0, button_width, button_height, corner_radius, style["hover_bg"],
                        style.get("border_color"), style.get("border_width", 0)),
                    canvas.itemconfig(text_item, fill=style["fg"])
                ])
                if command:
                    command()

        canvas.bind('<Enter>', on_enter)
        canvas.bind('<Leave>', on_leave)
        canvas.bind('<Button-1>', on_click)

        canvas.pack()

        def config_wrapper(state=None, bg=None, fg=None, cursor=None, **kwargs):
            if state is not None:
                button_state["disabled"] = (state == tk.DISABLED)
                if button_state["disabled"]:
                    draw_rounded_rect(canvas, 0, 0, button_width, button_height,
                                      corner_radius, colors['border_light'],
                                      None, 0)
                    canvas.itemconfig(text_item, fill=colors['text_muted'])
                    canvas.configure(cursor='arrow')
                else:
                    draw_rounded_rect(canvas, 0, 0, button_width, button_height,
                                      corner_radius, style["bg"],
                                      style.get("border_color"), style.get("border_width", 0))
                    canvas.itemconfig(text_item, fill=style["fg"])
                    canvas.configure(cursor='hand2')

                canvas.tag_raise("button_text")

            if bg is not None:
                if not button_state["disabled"]:
                    color_map = {
                        colors['border_light']: colors['border_light'],
                        colors['success']: colors['success'],
                        colors['danger']: colors['danger'],
                        colors['accent']: colors['accent']
                    }

                    mapped_color = color_map.get(bg, bg)

                    border_color = style.get(
                        "border_color") if button_type == "secondary" else None
                    border_width = style.get(
                        "border_width", 0) if button_type == "secondary" else 0

                    draw_rounded_rect(canvas, 0, 0, button_width, button_height,
                                      corner_radius, mapped_color, border_color, border_width)
                    if bg == colors['success']:
                        canvas.itemconfig(text_item, fill='white')
                    elif bg == colors['danger']:
                        canvas.itemconfig(text_item, fill='white')
                    elif bg == colors['accent']:
                        canvas.itemconfig(text_item, fill='white')
                    elif bg == colors['border_light']:
                        canvas.itemconfig(text_item, fill=colors['text_muted'])
                    else:
                        canvas.itemconfig(text_item, fill=style["fg"])

                    canvas.tag_raise("button_text")

            if fg is not None:
                if not button_state["disabled"]:
                    canvas.itemconfig(text_item, fill=fg)
                    canvas.tag_raise("button_text")

            if cursor is not None:
                canvas.configure(cursor=cursor)

        def cget_wrapper(option):
            if option == 'state':
                return tk.DISABLED if button_state["disabled"] else tk.NORMAL
            return None

        setattr(container, 'config', config_wrapper)
        setattr(container, 'configure', config_wrapper)
        setattr(container, 'cget', cget_wrapper)
        container['state'] = tk.NORMAL

        return container

    @staticmethod
    def create_labelframe(parent, text, colors, padding=15):
        """Create a simple label frame to replace ttk.LabelFrame"""

        frame = ttk.LabelFrame(
            parent, text=text, style='Modern.TLabelframe', padding=padding)
        return frame

    @staticmethod
    def create_hover_effect(widget, colors, enter_color, leave_color):
        def on_enter(e):
            widget.config(bg=enter_color)

        def on_leave(e):
            widget.config(bg=leave_color)

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    @staticmethod
    def create_drop_zone_hover(drop_zone, child_widgets, colors):
        original_bg = drop_zone.cget('bg')
        original_child_bgs = []

        for child in child_widgets:
            original_child_bgs.append(child.cget('bg'))

        def on_enter(e):
            current_relief = drop_zone.cget('relief')
            current_bd = drop_zone.cget('bd')
            current_height = drop_zone.cget('height')
            current_width = drop_zone.cget('width')

            drop_zone.config(bg=colors['drop_zone_hover'],
                             relief=current_relief, bd=current_bd,
                             height=current_height, width=current_width)

            for i, child in enumerate(child_widgets):
                child.config(bg=colors['drop_zone_hover'])

        def on_leave(e):
            current_relief = drop_zone.cget('relief')
            current_bd = drop_zone.cget('bd')
            current_height = drop_zone.cget('height')
            current_width = drop_zone.cget('width')

            drop_zone.config(bg=original_bg,
                             relief=current_relief, bd=current_bd,
                             height=current_height, width=current_width)

            for i, child in enumerate(child_widgets):
                child.config(bg=original_child_bgs[i])

        drop_zone.bind('<Enter>', on_enter)
        drop_zone.bind('<Leave>', on_leave)
        drop_zone.bind('<FocusIn>', lambda e: "break")
        drop_zone.bind('<FocusOut>', lambda e: "break")
        drop_zone.bind('<Button-1>', lambda e: "break")
        drop_zone.bind('<ButtonRelease-1>', lambda e: "break")

        drop_zone.configure(takefocus=False)

    @staticmethod
    def create_status_frame(parent, colors, status_type="info"):
        """Status frame with appropriate colors for different message types"""
        status_colors = {
            'info': colors['accent_light'],
            'success': colors['success_light'],
            'danger': colors['danger_light'],
            'error': colors['danger']
        }

        frame = tk.Frame(parent, bg=status_colors.get(status_type, colors['accent_light']),
                         relief='solid', bd=1, highlightthickness=0)
        return frame

    @staticmethod
    def create_image_button(parent, text, command, button_type="primary", colors=None, image=None, icon_type=None, is_light=True, **kwargs):
        """Create a button with custom colors and optional image support"""
        if colors is None:
            return None

        if icon_type and not image:
            has_images, icon_func = _lazy_import_icons()
            if has_images and icon_func:
                image = icon_func(icon_type, is_light=is_light)

        button_styles = {
            "primary": {
                "bg": colors['accent'],
                "fg": "white",
                "hover_bg": colors['accent_hover'],
                "active_bg": colors['accent_dark'],
                "border_color": None,
                "border_width": 0
            },
            "secondary": {
                "bg": colors['card_bg'],
                "fg": colors['button_border'],
                "hover_bg": colors['surface'],
                "active_bg": colors['border_light'],
                "border_color": colors['button_border'],
                "border_width": 2
            },
            "success": {
                "bg": colors['success'],
                "fg": "white",
                "hover_bg": colors['success_hover'],
                "active_bg": colors['success_hover'],
                "border_color": None,
                "border_width": 0
            },
            "danger": {
                "bg": colors['danger'],
                "fg": "white",
                "hover_bg": colors['danger_hover'],
                "active_bg": colors['danger_hover'],
                "border_color": None,
                "border_width": 0
            },
            "icon": {
                "bg": None,
                "fg": None,
                "hover_bg": None,
                "active_bg": None,
                "border_color": None,
                "border_width": 0
            }
        }

        style = button_styles.get(button_type, button_styles["primary"])

        padx = kwargs.get('padx', 20)
        pady = kwargs.get('pady', 8)

        try:
            parent_bg = parent.cget('bg')
        except:
            parent_bg = colors['bg']

        container = tk.Frame(parent, bg=parent_bg)
        canvas = tk.Canvas(container, highlightthickness=0,
                           bg=parent_bg, cursor='hand2')

        temp_label = tk.Label(container, text=text,
                              font=('Segoe UI', 10, 'bold'))
        temp_label.update_idletasks()
        text_width = temp_label.winfo_reqwidth()
        text_height = temp_label.winfo_reqheight()
        temp_label.destroy()

        image_width = 16 if image else 0
        image_padding = 5 if image else 0

        button_width = text_width + (padx * 2) + image_width + image_padding
        button_height = max(text_height + (pady * 2), 35)
        corner_radius = 8

        canvas.configure(width=button_width, height=button_height)

        def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, fill_color, border_color=None, border_width=0):
            canvas.delete("button_bg")
            canvas.delete("button_border")
            canvas.delete("button_text")
            canvas.delete("button_image")

            if button_type == "icon":
                content_x = button_width // 2

                if image:
                    if text and text.strip():
                        image_x = content_x - \
                            (image_width + image_padding +
                             text_width) // 2 + image_width // 2
                        text_x = image_x + image_width // 2 + image_padding + text_width // 2

                        canvas.create_image(
                            image_x, button_height // 2, image=image, tags="button_image")
                        canvas.create_text(text_x, button_height // 2, text=text, fill=colors['text'],
                                           font=('Segoe UI', 10, 'bold'), tags="button_text")
                    else:
                        canvas.create_image(
                            content_x, button_height // 2, image=image, tags="button_image")
                elif text and text.strip():
                    canvas.create_text(content_x, button_height // 2, text=text, fill=colors['text'],
                                       font=('Segoe UI', 10, 'bold'), tags="button_text")
                return

            if fill_color:
                canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2,
                                        fill=fill_color, outline="", tags="button_bg")
                canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius,
                                        fill=fill_color, outline="", tags="button_bg")

                canvas.create_arc(x1, y1, x1 + 2*radius, y1 + 2*radius,
                                  start=90, extent=90, fill=fill_color, outline="", tags="button_bg")
                canvas.create_arc(x2 - 2*radius, y1, x2, y1 + 2*radius,
                                  start=0, extent=90, fill=fill_color, outline="", tags="button_bg")
                canvas.create_arc(x1, y2 - 2*radius, x1 + 2*radius, y2,
                                  start=180, extent=90, fill=fill_color, outline="", tags="button_bg")
                canvas.create_arc(x2 - 2*radius, y2 - 2*radius, x2, y2,
                                  start=270, extent=90, fill=fill_color, outline="", tags="button_bg")

            if border_color and border_width > 0:
                if button_type == "secondary":
                    canvas.create_rectangle(x1 + radius, y1, x2 - radius, y1 + border_width,
                                            fill=border_color, outline="", tags="button_border")
                    canvas.create_rectangle(x1 + radius, y2 - border_width, x2 - radius, y2,
                                            fill=border_color, outline="", tags="button_border")
                    canvas.create_rectangle(x1, y1 + radius, x1 + border_width, y2 - radius,
                                            fill=border_color, outline="", tags="button_border")
                    canvas.create_rectangle(x2 - border_width, y1 + radius, x2, y2 - radius,
                                            fill=border_color, outline="", tags="button_border")

                    corner_size = radius
                    for i in range(corner_size):
                        for j in range(corner_size):
                            dx = corner_size - i
                            dy = corner_size - j
                            distance = (dx*dx + dy*dy) ** 0.5

                            if corner_size - border_width <= distance <= corner_size:
                                canvas.create_rectangle(x1 + i, y1 + j, x1 + i + 1, y1 + j + 1,
                                                        fill=border_color, outline="", tags="button_border")

                    for i in range(corner_size):
                        for j in range(corner_size):
                            dx = i + 1
                            dy = corner_size - j
                            distance = (dx*dx + dy*dy) ** 0.5

                            if corner_size - border_width <= distance <= corner_size:
                                canvas.create_rectangle(x2 - corner_size + i, y1 + j, x2 - corner_size + i + 1, y1 + j + 1,
                                                        fill=border_color, outline="", tags="button_border")

                    for i in range(corner_size):
                        for j in range(corner_size):
                            dx = corner_size - i
                            dy = j + 1
                            distance = (dx*dx + dy*dy) ** 0.5

                            if corner_size - border_width <= distance <= corner_size:
                                canvas.create_rectangle(x1 + i, y2 - corner_size + j, x1 + i + 1, y2 - corner_size + j + 1,
                                                        fill=border_color, outline="", tags="button_border")

                    for i in range(corner_size):
                        for j in range(corner_size):
                            dx = i + 1
                            dy = j + 1
                            distance = (dx*dx + dy*dy) ** 0.5
                            if corner_size - border_width <= distance <= corner_size:
                                canvas.create_rectangle(x2 - corner_size + i, y2 - corner_size + j,
                                                        x2 - corner_size + i + 1, y2 - corner_size + j + 1,
                                                        fill=border_color, outline="", tags="button_border")
                else:
                    canvas.create_rectangle(x1, y1, x2, y2, outline=border_color,
                                            width=border_width, tags="button_border")

            content_x = button_width // 2
            if image:
                if text and text.strip():
                    image_x = content_x - \
                        (image_width + image_padding +
                         text_width) // 2 + image_width // 2
                    text_x = image_x + image_width // 2 + image_padding + text_width // 2

                    canvas.create_image(
                        image_x, button_height // 2, image=image, tags="button_image")
                    canvas.create_text(text_x, button_height // 2, text=text, fill=style["fg"],
                                       font=('Segoe UI', 10, 'bold'), tags="button_text")
                else:
                    canvas.create_image(
                        content_x, button_height // 2, image=image, tags="button_image")

            elif text and text.strip():
                canvas.create_text(content_x, button_height // 2, text=text, fill=style["fg"],
                                   font=('Segoe UI', 10, 'bold'), tags="button_text")

        draw_rounded_rect(canvas, 0, 0, button_width, button_height, corner_radius,
                          style["bg"], style.get("border_color"), style.get("border_width", 0))

        button_state = {"disabled": False}

        def on_enter(e):
            if not button_state["disabled"]:
                if button_type == "icon":
                    draw_rounded_rect(canvas, 0, 0, button_width, button_height,
                                      corner_radius, colors['border_light'], None, 0)
                else:
                    draw_rounded_rect(canvas, 0, 0, button_width, button_height,
                                      corner_radius, style["hover_bg"],
                                      style.get("border_color"), style.get("border_width", 0))

        def on_leave(e):
            if not button_state["disabled"]:
                if button_type == "icon":
                    draw_rounded_rect(canvas, 0, 0, button_width, button_height,
                                      corner_radius, None, None, 0)
                else:
                    draw_rounded_rect(canvas, 0, 0, button_width, button_height,
                                      corner_radius, style["bg"],
                                      style.get("border_color"), style.get("border_width", 0))

        def on_click(e):
            if not button_state["disabled"]:
                if button_type == "icon":
                    draw_rounded_rect(canvas, 0, 0, button_width, button_height,
                                      corner_radius, colors['border'], None, 0)
                    parent.after(100, lambda: draw_rounded_rect(
                        canvas, 0, 0, button_width, button_height, corner_radius, colors['border_light'], None, 0))
                else:
                    draw_rounded_rect(canvas, 0, 0, button_width, button_height,
                                      corner_radius, style["active_bg"],
                                      style.get("border_color"), style.get("border_width", 0))
                    parent.after(100, lambda: draw_rounded_rect(
                        canvas, 0, 0, button_width, button_height, corner_radius, style["hover_bg"],
                        style.get("border_color"), style.get("border_width", 0)))
                if command:
                    command()

        canvas.bind('<Enter>', on_enter)
        canvas.bind('<Leave>', on_leave)
        canvas.bind('<Button-1>', on_click)
        canvas.pack()

        return container

    @staticmethod
    def create_progress_bar(parent, colors=None, **kwargs):
        """Create a cross-platform progress bar with consistent styling"""
        if colors is None:
            return ttk.Progressbar(parent, mode='determinate', **kwargs)
        
        class CustomProgressBar:
            def __init__(self, parent, colors, **kwargs):
                self.container = tk.Frame(parent, bg=colors.get('bg', '#ffffff'))
                
                self.min_width = kwargs.get('width', 300)
                self.height = kwargs.get('height', 14)
                
                self.canvas = tk.Canvas(self.container, height=self.height,
                                       bg=colors.get('bg', '#ffffff'),
                                       highlightthickness=1,
                                       highlightbackground=colors.get('border', '#cccccc'))
                
                self.canvas.pack(fill='both', expand=True, padx=2, pady=2)
                self.current_value = 0
                self.colors = colors
                
                self.canvas.bind('<Configure>', self._on_canvas_resize)
                
                self.container.after(10, self._draw_progress_bar)
            
            def _on_canvas_resize(self, event):
                """Redraw progress bar when canvas is resized"""
                self._draw_progress_bar()
            
            def _draw_progress_bar(self):
                """Draw the progress bar based on current canvas size"""
                self.canvas.delete('all')
                
                self.canvas.update_idletasks()
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                if canvas_width <= 1 or canvas_height <= 1:
                    return
                
                self.canvas.create_rectangle(2, 2, canvas_width-2, canvas_height-2,
                                           fill=self.colors.get('border_light', '#f0f0f0'),
                                           outline=self.colors.get('border', '#cccccc'),
                                           tags='trough')
                
                if self.current_value > 0:
                    progress_width = max(2, (self.current_value / 100.0) * (canvas_width - 4))
                    self.canvas.create_rectangle(2, 2, progress_width + 2, canvas_height - 2,
                                               fill=self.colors.get('success', '#1a7f37'),
                                               outline='',
                                               tags='progress')
            
            def config(self, value=None, **kwargs):
                if value is not None:
                    self.current_value = max(0, min(100, value))
                    self._draw_progress_bar()
            
            def configure(self, **kwargs):
                if 'value' in kwargs:
                    self.config(value=kwargs['value'])
            
            def get(self):
                return self.current_value
            
            def grid(self, **kwargs):
                return self.container.grid(**kwargs)
            
            def pack(self, **kwargs):
                return self.container.pack(**kwargs)
            
            def place(self, **kwargs):
                return self.container.place(**kwargs)
        
        return CustomProgressBar(parent, colors, **kwargs)


FONTS = {
    'title': ('Segoe UI', 28, 'bold'),
    'subtitle': ('Segoe UI', 13),
    'heading': ('Segoe UI', 12, 'bold'),
    'body': ('Segoe UI', 10),
    'body_bold': ('Segoe UI', 10, 'bold'),
    'small': ('Segoe UI', 9),
    'small_bold': ('Segoe UI', 9, 'bold'),
    'large_icon': ('Segoe UI', 24),
    'medium_icon': ('Segoe UI', 20),
    'small_icon': ('Segoe UI', 16),
    'button': ('Segoe UI', 10, 'bold'),
    'label': ('Segoe UI', 10),
    'status': ('Segoe UI', 9)
}

LAYOUT = {
    'main_padding': 20,
    'card_padding': 20,
    'section_spacing': 20,
    'element_spacing': 12,
    'small_spacing': 8,
    'button_spacing': 12,
    'title_height': 80,
    'drop_zone_height': 100,
    'info_zone_height': 70,
    'tree_height': 8,
    'card_border_radius': 8,
    'button_border_radius': 6
}
