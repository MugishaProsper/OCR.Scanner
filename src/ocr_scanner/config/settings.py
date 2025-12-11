"""
Application settings and configuration.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any

# Application constants
APP_NAME = "OCR Scanner"
APP_VERSION = "1.1.0"
AUTHOR = "Mugisha Prosper"

# File extensions
SUPPORTED_IMAGE_FORMATS = [
    "*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tiff", "*.tif", "*.gif"
]

IMAGE_FILTER = "Image Files (" + " ".join(SUPPORTED_IMAGE_FORMATS) + ")"

# OCR settings
DEFAULT_OCR_CONFIG = {
    "confidence_threshold": 60,
    "language": "eng",
    "page_segmentation_mode": 6,  # PSM_SINGLE_UNIFORM_BLOCK
}

# Supported OCR languages
SUPPORTED_LANGUAGES = {
    "eng": "English",
    "spa": "Spanish", 
    "fra": "French",
    "deu": "German",
    "ita": "Italian",
    "por": "Portuguese",
    "rus": "Russian",
    "chi_sim": "Chinese (Simplified)",
    "chi_tra": "Chinese (Traditional)",
    "jpn": "Japanese",
    "kor": "Korean",
    "ara": "Arabic",
    "hin": "Hindi",
    "tha": "Thai",
    "vie": "Vietnamese",
    "nld": "Dutch",
    "swe": "Swedish",
    "nor": "Norwegian",
    "dan": "Danish",
    "fin": "Finnish",
    "pol": "Polish",
    "ces": "Czech",
    "hun": "Hungarian",
    "tur": "Turkish",
    "heb": "Hebrew",
    "ukr": "Ukrainian",
    "bul": "Bulgarian",
    "hrv": "Croatian",
    "slv": "Slovenian",
    "slk": "Slovak",
    "ron": "Romanian",
    "ell": "Greek",
    "lav": "Latvian",
    "lit": "Lithuanian",
    "est": "Estonian"
}

# GUI settings
DEFAULT_WINDOW_SIZE = (1400, 900)
DEFAULT_IMAGE_DISPLAY_SIZE = (640, 480)

# Preprocessing options
PREPROCESSING_OPTIONS = [
    "None",
    "Grayscale", 
    "Threshold",
    "Adaptive Threshold",
    "Denoise",
    "Auto Rotate",
    "Deskew",
    "Perspective Correction"
]

# Export formats
EXPORT_FORMATS = {
    "txt": "Text Files (*.txt)",
    "csv": "CSV Files (*.csv)",
    "json": "JSON Files (*.json)"
}

# Paths
def get_app_data_dir() -> Path:
    """Get application data directory."""
    if os.name == 'nt':  # Windows
        base_dir = Path(os.environ.get('APPDATA', Path.home()))
    else:  # Unix-like
        base_dir = Path.home() / '.local' / 'share'
    
    app_dir = base_dir / 'ocr-scanner'
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir

def get_config_dir() -> Path:
    """Get configuration directory."""
    if os.name == 'nt':  # Windows
        base_dir = Path(os.environ.get('APPDATA', Path.home()))
    else:  # Unix-like
        base_dir = Path.home() / '.config'
    
    config_dir = base_dir / 'ocr-scanner'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_log_dir() -> Path:
    """Get log directory."""
    log_dir = get_app_data_dir() / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

def setup_logging(level: int = logging.INFO) -> None:
    """Setup application logging."""
    log_dir = get_log_dir()
    log_file = log_dir / 'ocr_scanner.log'
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Prevent duplicate logs
    root_logger.propagate = False