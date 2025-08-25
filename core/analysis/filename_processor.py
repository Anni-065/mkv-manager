"""
Filename Processing Module

This module handles extraction of series information from filenames,
including season/episode detection and quality tag removal.
"""

import re
import os
from ..config.constants import (
    QUALITY_PATTERN_SERIES, SEASON_EPISODE_PATTERN,
    ABBREVIATIONS, QUALITY_PATTERNS
)


def extract_series_info(filename):
    """
    Extract series information from filename including title, season, episode, and episode title.

    Args:
        filename: The filename to parse

    Returns:
        tuple: (series_title, season_episode_tag, season_num, episode_num, episode_title)
    """
    base_name = os.path.splitext(filename)[0]

    protected_name = base_name

    for abbrev, placeholder in ABBREVIATIONS.items():
        protected_name = protected_name.replace(abbrev, placeholder)

    season_episode_match = re.search(SEASON_EPISODE_PATTERN, protected_name)
    if not season_episode_match:
        return None, None, None, None, None

    season_num = int(season_episode_match.group(1))
    episode_num = int(season_episode_match.group(2))
    season_episode_tag = f"S{season_num:02d}E{episode_num:02d}"

    # Extract series title
    series_title_end = season_episode_match.start()
    series_title = protected_name[:series_title_end].strip()

    series_title = re.sub(r'[._-]+$', '', series_title)
    series_title = re.sub(r'[._-]+', ' ', series_title).strip()

    # Extract episode title
    episode_part = protected_name[season_episode_match.end():].strip()
    episode_part = re.sub(r'^[._-]+', '', episode_part)

    episode_title = re.sub(QUALITY_PATTERN_SERIES, '',
                           episode_part, flags=re.IGNORECASE).strip()
    episode_title = re.sub(r'[._-]+$', '', episode_title)
    episode_title = re.sub(r'[._-]+', ' ', episode_title).strip()

    # Restore abbreviations in all parts
    for abbrev, placeholder in ABBREVIATIONS.items():
        series_title = series_title.replace(placeholder, abbrev)
        if episode_title:
            episode_title = episode_title.replace(placeholder, abbrev)

    series_title = series_title.strip()
    episode_title = episode_title.strip() if episode_title else None

    # Remove empty episode title
    if episode_title and (len(episode_title) < 2 or episode_title.lower() in ['episode', 'ep']):
        episode_title = None

    return series_title, season_episode_tag, season_num, episode_num, episode_title


def clean_filename_quality_tags(filename):
    """
    Remove quality tags and encoding information from filename.

    Args:
        filename: The filename to clean

    Returns:
        str: Cleaned filename
    """
    base_name = os.path.splitext(filename)[0]

    for pattern in QUALITY_PATTERNS:
        base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)

    base_name = re.sub(r'[._-]+', ' ', base_name).strip()
    base_name = re.sub(r'\s+', ' ', base_name)

    return base_name
