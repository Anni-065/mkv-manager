"""
Subprocess Utilities Module

This module provides utility functions for running subprocess commands
with hidden console windows on Windows platforms.
"""

import os
import subprocess


def get_subprocess_kwargs():
    """
    Get subprocess keyword arguments to hide console windows on Windows.

    Returns:
        dict: Dictionary containing startupinfo and creationflags for subprocess calls
    """
    if os.name == 'nt':  # Windows
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        return {
            'startupinfo': startupinfo,
            'creationflags': subprocess.CREATE_NO_WINDOW
        }
    else:
        return {}


def run_hidden(cmd, **kwargs):
    """
    Run a subprocess command with hidden console window on Windows.

    Args:
        cmd: Command to run (list or string)
        **kwargs: Additional keyword arguments to pass to subprocess.run

    Returns:
        subprocess.CompletedProcess: Result of the subprocess run
    """
    subprocess_kwargs = get_subprocess_kwargs()

    # Set encoding for Windows to handle special characters
    if os.name == 'nt' and 'encoding' not in kwargs:
        kwargs['encoding'] = 'utf-8'

    subprocess_kwargs.update(kwargs)
    return subprocess.run(cmd, **subprocess_kwargs)


def popen_hidden(cmd, **kwargs):
    """
    Create a subprocess.Popen with hidden console window on Windows.

    Args:
        cmd: Command to run (list or string)
        **kwargs: Additional keyword arguments to pass to subprocess.Popen

    Returns:
        subprocess.Popen: Popen object
    """
    subprocess_kwargs = get_subprocess_kwargs()
    subprocess_kwargs.update(kwargs)
    return subprocess.Popen(cmd, **subprocess_kwargs)
