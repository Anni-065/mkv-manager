"""
MKV Operations Module

This module handles low-level MKV operations including
mkvmerge execution and subtitle extraction.
"""
import subprocess
import threading
import re
from ..utils.subprocess_utils import popen_hidden


def run_mkvmerge(cmd, progress_callback):
    """Run mkvmerge command and parse progress output"""
    try:
        process = popen_hidden(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1  # Line buffered
        )

        progress_patterns = [
            re.compile(r'Progress:\s*(\d{1,3})%'),
            re.compile(r'(\d{1,3})%'),
            re.compile(r'\[\s*(\d{1,3})%\s*\]'),
            re.compile(r'muxing:\s*(\d{1,3})%'),
        ]

        def read_output(stream, stream_name):
            for line in iter(stream.readline, ''):
                line = line.strip()

                if line:
                    print(f"{stream_name}: {line}")
                    
                    for pattern in progress_patterns:
                        match = pattern.search(line)

                        if match:
                            progress = int(match.group(1))

                            try:
                                progress_callback(progress)
                                break
                            except Exception as e:
                                print(f"DEBUG: Error in progress callback: {e}")

        stdout_thread = threading.Thread(target=read_output, args=(process.stdout, "STDOUT"))
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr, "STDERR"))

        stdout_thread.start()
        stderr_thread.start()

        process.wait()

        stdout_thread.join()
        stderr_thread.join()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)

    except Exception as e:
        print(f"Error running mkvmerge: {e}")
        raise
