#!/usr/bin/env python3
"""
Basic usage example for OCR Scanner.

This example demonstrates how to use the OCR Scanner programmatically
without the GUI interface.
"""

import sys
import cv2
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ocr_scanner.core.image_processor import ImageProcessor


def process_single_image(image_path: str) -> str:
    """
    Process a single image and extract text.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    # Apply preprocessing (optional)
    processed_image = ImageProcessor.apply_preprocessing(image, "Grayscale")
    
    # Run OCR
    text = ImageProcessor.run_ocr(processed_image)
    
    return text


def main():
    """Main function demonstrating basic usage."""
    if len(sys.argv) != 2:
        print("Usage: python basic_usage.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        text = process_single_image(image_path)
        print("Extracted Text:")
        print("-" * 40)
        print(text)
        
    except Exception as e:
        print(f"Error processing image: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()