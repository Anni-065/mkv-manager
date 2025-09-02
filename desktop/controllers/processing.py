"""
Processing Controller for MKV Cleaner Desktop GUI
Handles file processing operations and threading
"""

import os
import threading
from tkinter import messagebox
from typing import Any, Optional, Callable, Union

import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
desktop_dir = os.path.dirname(current_dir)  # This goes up to /desktop from /desktop/controllers
root_dir = os.path.dirname(desktop_dir)     # This goes up to root from /desktop
sys.path.insert(0, root_dir)

try:
    from core.processing.mkv_processor import filter_and_remux
except ImportError:
    def filter_and_remux(file_path: str, output_folder: Optional[str] = None,
                         preferences: Optional[dict] = None, extract_subtitles: bool = False,
                         progress_callback: Optional[Callable] = None) -> Any:
        """Fallback function when core module is not available"""
        raise ImportError("filter_and_remux function not available")

# Import image utilities
current_dir = os.path.dirname(os.path.abspath(__file__))
gui_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, gui_dir)

try:
    from gui.utils import get_icon
    from tkinter import PhotoImage
except ImportError:
    PhotoImage = None

    def get_icon(icon_type: str) -> Optional[Any]:
        """Fallback function when image utils are not available"""
        return None


class ProcessingController:
    """Controller for file processing operations"""

    def __init__(self, gui, selected_files, language_config, output_folder_controller, file_selection_controller):
        self.gui = gui
        self.selected_files = selected_files
        self.language_config = language_config
        self.output_folder_controller = output_folder_controller
        self.file_selection_controller = file_selection_controller
        self.processing = False

    def process_files(self):
        """Process all selected files"""
        if not self.selected_files:
            messagebox.showwarning(
                "No Files", "Please select files to process.")
            return

        if self.processing:
            messagebox.showwarning(
                "Processing", "Files are already being processed.")
            return

        self.gui.process_button.config(
            state='disabled', bg=self.gui.colors['border_light'], fg=self.gui.colors['text_muted'], cursor='arrow')
        self.processing = True

        # Initialize progress bar
        self.gui.root.after(0, lambda: self.gui.progress_bar.config(value=0))
        self.gui.root.after(0, lambda: self.gui.progress_label.config(text="Starting processing..."))

        thread = threading.Thread(target=self.process_thread)
        thread.daemon = True
        thread.start()

    def process_thread(self):
        """Process files in a separate thread"""
        try:
            total_files = len(self.selected_files)

            files_by_output = {}
            for file_info in self.selected_files:
                output_folder = self.output_folder_controller.get_output_folder(
                    file_info['path'])
                if output_folder is None:
                    continue

                if output_folder not in files_by_output:
                    files_by_output[output_folder] = []
                files_by_output[output_folder].append(file_info)

            processed_count = 0

            for output_folder, files in files_by_output.items():
                try:
                    os.makedirs(output_folder, exist_ok=True)
                except Exception as e:
                    self.gui.root.after(0, lambda: messagebox.showerror(
                        "Error", f"Could not create output folder: {str(e)}"))
                    continue

                for file_info in files:
                    try:
                        # Initialize progress for this file
                        initial_progress = (processed_count / total_files) * 100
                        self.gui.root.after(0, lambda p=initial_progress: self.gui.progress_bar.config(value=p))
                        
                        status_text = f"Processing: {file_info['name']}"
                        self.gui.root.after(0, lambda t=status_text: self.gui.progress_label.config(
                            text=t))

                        preferences = {
                            'ALLOWED_AUDIO_LANGS': self.language_config['allowed_audio_langs'],
                            'ALLOWED_SUB_LANGS': self.language_config['allowed_sub_langs'],
                            'DEFAULT_AUDIO_LANG': self.language_config['default_audio_lang'],
                            'DEFAULT_SUBTITLE_LANG': self.language_config['default_subtitle_lang'],
                            'ORIGINAL_AUDIO_LANG': self.language_config['original_audio_lang'],
                            'ORIGINAL_SUBTITLE_LANG': self.language_config['original_subtitle_lang'],
                            'EXTRACT_SUBTITLES': self.gui.extract_subtitles.get(),
                            'SAVE_EXTRACTED_SUBTITLES': self.gui.save_extracted_subtitles.get()
                        }

                        def update_progress(mkvmerge_progress):
                            file_progress = mkvmerge_progress / 100.0
                            overall_progress = (
                                (processed_count + file_progress) / total_files) * 100
                            self.gui.root.after(
                                0, lambda p=overall_progress: self.gui.progress_bar.config(value=p))

                        filter_and_remux(
                            file_info['path'], output_folder, preferences, 
                            extract_subtitles=False, progress_callback=update_progress)

                        processed_count += 1

                    except Exception as e:
                        error_msg = f"Error processing {file_info['name']}: {str(e)}"
                        self.gui.root.after(0, lambda msg=error_msg: messagebox.showerror(
                            "Processing Error", msg))

            self.gui.root.after(
                0, lambda: self.gui.progress_bar.config(value=100))
            self.gui.root.after(0, lambda: self.gui.progress_label.config(
                text=f"Completed! Processed {processed_count} files."))

            success_msg = f"Successfully processed {processed_count} files!"
            self.gui.root.after(0, lambda: messagebox.showinfo(
                "Processing Complete", success_msg))

        except Exception as e:
            self.gui.root.after(0, lambda: messagebox.showerror(
                "Error", f"Processing failed: {str(e)}"))

        finally:
            self.gui.root.after(
                0, self.file_selection_controller.clear_selection)
            self.gui.root.after(0, lambda: self.gui.process_button.config(
                state='disabled', bg=self.gui.colors['border_light'], fg=self.gui.colors['text_muted'], cursor='arrow'))
            self.processing = False
