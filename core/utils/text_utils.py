"""
Text Processing Utilities

This module contains utilities for processing subtitle text,
including line breaking and formatting functions.
"""

import re


def break_long_subtitle_lines(text, max_line_length=45):
    """
    Break long subtitle lines into multiple lines at optimal positions.

    Args:
        text: The subtitle text to process
        max_line_length: Maximum characters per line (default 45)

    Returns:
        Text with line breaks inserted at optimal positions
    """
    if not text or len(text) <= max_line_length:
        return text

    lines = text.split('\n')
    processed_lines = []

    for line in lines:
        if len(line) <= max_line_length:
            processed_lines.append(line)
            continue

        broken_lines = []
        remaining_text = line.strip()

        while len(remaining_text) > max_line_length:
            best_break = find_best_break_point(remaining_text, max_line_length)

            if best_break == -1:
                best_break = find_word_boundary(
                    remaining_text, max_line_length)

            if best_break == -1:
                best_break = max_line_length

            current_line = remaining_text[:best_break].strip()
            if current_line:
                broken_lines.append(current_line)

            remaining_text = remaining_text[best_break:].strip()

        if remaining_text:
            broken_lines.append(remaining_text)

        processed_lines.extend(broken_lines)

    return '\n'.join(processed_lines)


def find_best_break_point(text, max_length):
    """Find the best position to break a line for readability."""
    if len(text) <= max_length:
        return -1

    search_text = text[:max_length]

    # Look for natural breaks in order of preference
    break_chars = ['. ', '! ', '? ', ', ', '; ', ' - ', ' – ', ' — ']

    for char in break_chars:
        last_pos = search_text.rfind(char)
        if last_pos > max_length * 0.5:  # Don't break too early
            return last_pos + len(char)

    return -1


def find_word_boundary(text, max_length):
    """Find the last word boundary within the maximum length."""
    if len(text) <= max_length:
        return -1

    search_text = text[:max_length]
    last_space = search_text.rfind(' ')

    if last_space > max_length * 0.3:  # Ensure we don't break too early
        return last_space + 1

    return -1


def process_srt_file_line_breaks(srt_file_path, max_line_length=45):
    """
    Process an SRT file to add proper line breaks for long subtitle lines.

    Args:
        srt_file_path: Path to the SRT file to process
        max_line_length: Maximum characters per line (default 45)
    """
    try:
        with open(srt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into subtitle blocks
        blocks = re.split(r'\n\s*\n', content.strip())
        processed_blocks = []

        for block in blocks:
            lines = block.split('\n')
            if len(lines) >= 3:  # Valid subtitle block
                # Keep number and timing unchanged
                subtitle_lines = lines[2:]
                subtitle_text = '\n'.join(subtitle_lines)

                # Process the subtitle text
                processed_text = break_long_subtitle_lines(
                    subtitle_text, max_line_length)

                # Reconstruct the block
                processed_block = lines[0] + '\n' + \
                    lines[1] + '\n' + processed_text
                processed_blocks.append(processed_block)
            else:
                processed_blocks.append(block)

        # Write back to file
        with open(srt_file_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(processed_blocks) + '\n')

        print(f"✅ Processed line breaks in {srt_file_path}")

    except Exception as e:
        print(f"⚠️ Error processing line breaks in {srt_file_path}: {str(e)}")


def clean_subtitle_text(text):
    """
    Clean subtitle text by removing unwanted characters and formatting.

    Args:
        text: Raw subtitle text

    Returns:
        str: Cleaned subtitle text
    """
    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove formatting codes
    text = re.sub(r'{\\\w+[^}]*}', '', text)

    # Clean up excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text
