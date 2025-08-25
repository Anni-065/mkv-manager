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
    # print(f"DEBUG: Command: {' '.join(cmd)}")

    try:
        process = popen_hidden(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=0
        )

        progress_pattern = re.compile(r'\b\w+:\s*(100|[0-9]?[0-9])%')

        def read_stdout():
            for line in iter(process.stdout.readline, ''):
                line = line.strip()

                if line:
                    print(f"STDOUT: {line}")
                    match = progress_pattern.search(line)

                    if match:
                        progress = int(match.group(1))

                        try:
                            progress_callback(progress)
                        except Exception as e:
                            print(f"DEBUG: Error in progress callback: {e}")

        stdout_thread = threading.Thread(target=read_stdout)

        stdout_thread.start()

        process.wait()

        stdout_thread.join()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)

        print(
            f"DEBUG: mkvmerge completed with return code: {process.returncode}")

    except Exception as e:
        print(f"Error running mkvmerge: {e}")
        raise
