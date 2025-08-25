LANG_TITLES = {
    "eng": "English",
    "spa": "Spanish",
    "ger": "German",
    "fre": "French",
    "ita": "Italian",
    "por": "Portuguese",
    "rus": "Russian",
    "jpn": "Japanese",
    "kor": "Korean",
    "zho": "Chinese",
    "ara": "Arabic",
    "hin": "Hindi",
    "tur": "Turkish",
    "nld": "Dutch",
    "tha": "Thai",
    "vie": "Vietnamese",
    "pol": "Polish",
    "swe": "Swedish",
    "dan": "Danish",
    "nor": "Norwegian",
    "fin": "Finnish",
    "gre": "Greek",
    "heb": "Hebrew",
    "cze": "Czech",
    "hun": "Hungarian",
    "rou": "Romanian",
    "bul": "Bulgarian",
    "ukr": "Ukrainian",
    "mar": "Marathi",
    "fas": "Persian",
    "urd": "Urdu",
    "ind": "Indonesian",
    "may": "Malay",
    "kan": "Kannada",
    "tam": "Tamil",
    "tel": "Telugu",
    "guj": "Gujarati",
    "mal": "Malayalam",
    "pan": "Punjabi",
    "ben": "Bengali",
    "srp": "Serbian",
    "slk": "Slovak",
    "slv": "Slovenian",
    "hrv": "Croatian",
    "cat": "Catalan",
    "lit": "Lithuanian",
    "lav": "Latvian",
    "est": "Estonian",
    "glg": "Galician",
    "nep": "Nepali",
    "und": "",
}

QUALITY_TAGS = [
    r'1080p', r'720p', r'480p', r'4K', r'UHD', r'HDR', r'WEB-DL', r'BluRay', r'BDRip', r'DVDRip',
    r'x264', r'x265', r'HEVC', r'AAC', r'DTS', r'AC3', r'5\.1', r'2\.0', r'\d+Kbps', r'MSubs',
    r'NF', r'AMZN', r'HULU', r'DSNP', r'HBO', r'PARAMOUNT', r'APPLE', r'PEACOCK', r'SHOWTIME',
    r'STARZ', r'VUDU', r'FANDANGO', r'ROKU', r'TUBI', r'CRACKLE', r'PLUTO', r'FREEVEE', r'REDBOX',
    r'Webrip', r'WebRip', r'WEBRip', r'10bit', r'8bit', r'EAC3', r'DDP5', r'APEX', r'WEB'
]

QUALITY_PATTERNS = [
    r'\([^)]*(?:WEB|1080p|720p|480p|x264|x265|AC3|DTS|AAC)\b[^)]*\)',
    r'\[[^]]*(?:WEB|1080p|720p|480p|x264|x265|AC3|DTS|AAC|[A-F0-9]{8})\b[^]]*\]',
    r'(?:^|\s|[._-])(' + '|'.join(QUALITY_TAGS) + r')(?=\s|[._-]|$)',
    r'\b\d{3,4}p\b',
    r'\bx26[45]\b',
    r'\b[A-F0-9]{8}\b'
]

QUALITY_TAGS_SERIES = [
    r'1080p', r'720p', r'480p', r'4K', r'UHD', r'HDR', r'WEB-DL', r'BluRay', r'BDRip', r'DVDRip',
    r'x264', r'x265', r'HEVC', r'AAC', r'DTS', r'AC3', r'5\.1', r'2\.0', r'\d+Kbps', r'MSubs',
    r'NF', r'AMZN', r'HULU', r'DSNP', r'HBO', r'PARAMOUNT', r'APPLE', r'PEACOCK', r'SHOWTIME',
    r'STARZ', r'VUDU', r'FANDANGO', r'ROKU', r'TUBI', r'CRACKLE', r'PLUTO', r'FREEVEE', r'REDBOX',
    r'Episode\s+\d+', r'Ep\s+\d+', r'Part\s+\d+'
]

ABBREVIATIONS = {
    'K.': '###K_DOT###',
    'Dr.': '###DR_DOT###',
    'Mr.': '###MR_DOT###',
    'Mrs.': '###MRS_DOT###',
    'Ms.': '###MS_DOT###',
    'St.': '###ST_DOT###',
    'Jr.': '###JR_DOT###',
    'Sr.': '###SR_DOT###'
}

SEASON_EPISODE_PATTERN = r'[Ss](\d+)[Ee](\d+)'
QUALITY_PATTERN_SERIES = r'\s*(' + '|'.join(QUALITY_TAGS_SERIES) + r').*$'
SOURCE_PATTERN = r'\[([^\]]+)\]'
