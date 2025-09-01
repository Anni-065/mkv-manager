"""
Track Analysis Module

This module contains functions for analyzing MKV track information
"""
import os
import subprocess
import json
from ..utils.subprocess_utils import run_hidden

try:
    from ..config.user_config import MKVMERGE_PATH
except ImportError:
    from ..config import MKVMERGE_PATH


def is_forced_subtitle_by_name(track_name):
    """
    Check if a subtitle track should be treated as forced based on its name.
    Returns True if the track name contains indicators of forced subtitles.
    """
    if not track_name:
        return False

    track_name_lower = track_name.lower()
    forced_indicators = ['signs', 'songs', 'forced']

    result = any(
        indicator in track_name_lower for indicator in forced_indicators)

    return result


def get_track_info(file_path):
    """
    Extract track information from an MKV file using mkvmerge.

    Args:
        file_path: Path to the MKV file

    Returns:
        List of track dictionaries with id, type, language, forced status, etc.
    """
    try:
        file_path = os.path.normpath(file_path)

        if not os.path.exists(file_path):
            print(f"Error: File does not exist: {file_path}")
            return []

        if not os.access(file_path, os.R_OK):
            print(f"Error: File is not readable: {file_path}")
            return []

        print(f"DEBUG: Analyzing tracks for: {os.path.basename(file_path)}")
        cmd = [MKVMERGE_PATH, "-J", file_path]

        result = run_hidden(cmd, capture_output=True, text=True)

        if result is None:
            print(
                f"Error: mkvmerge command returned None for file: {file_path}")
            return []

        if result.returncode != 0:
            print(
                f"Error: mkvmerge failed with return code {result.returncode}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return []

        if not result.stdout:
            print(
                f"Error: mkvmerge returned empty output for file: {file_path}")
            return []

        data = json.loads(result.stdout)
        tracks = []

        for track in data.get("tracks", []):
            track_name = track["properties"].get("track_name", "")
            original_forced = track["properties"].get("forced_track", False)

            name_based_forced = is_forced_subtitle_by_name(track_name)
            is_forced = original_forced or name_based_forced

            tracks.append({
                "id": track["id"],
                "type": track["type"],
                "lang": track["properties"].get("language", "und"),
                "forced": is_forced,
                "hearing_impaired": track["properties"].get("hearing_impaired_flag", False),
                "track_name": track_name
            })

        return tracks

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from mkvmerge output for file: {file_path}")
        print(f"JSON Error: {str(e)}")
        if result and result.stdout:
            print(f"Raw output: {result.stdout[:500]}...")  # First 500 chars
        return []
    except subprocess.CalledProcessError as e:
        print(f"Error running mkvmerge command: {str(e)}")
        return []
    except Exception as e:
        print(f"Unexpected error in get_track_info: {str(e)}")
        return []
