#!/usr/bin/env python3
"""
Batch processing example for OCR Scanner.

This example demonstrates how to use the batch processing functionality
programmatically without the GUI interface.
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ocr_scanner.core.batch_processor import BatchProcessor
from ocr_scanner.utils.export import ResultExporter


class SimpleBatchProcessor:
    """Simple batch processor for command-line usage."""
    
    def __init__(self):
        self.results = []
    
    def process_images(self, image_paths: List[str], 
                      preprocessing_method: str = "None",
                      threshold_value: int = 127) -> List[Dict[str, Any]]:
        """
        Process multiple images and return results.
        
        Args:
            image_paths: List of image file paths
            preprocessing_method: Preprocessing method to apply
            threshold_value: Threshold value for binary threshold
            
        Returns:
            List of processing results
        """
        results = []
        
        for i, image_path in enumerate(image_paths):
            try:
                filename = os.path.basename(image_path)
                print(f"Processing {i+1}/{len(image_paths)}: {filename}")
                
                # Create a simple processor for this image
                processor = BatchProcessor([image_path], preprocessing_method, threshold_value)
                
                # Process the image (simplified version)
                import cv2
                image = cv2.imread(image_path)
                if image is None:
                    results.append({
                        'filename': filename,
                        'text': '',
                        'status': 'Error: Could not load image',
                        'timestamp': ''
                    })
                    continue
                
                # Apply preprocessing
                processed_image = processor._apply_preprocessing(image)
                
                # Run OCR
                text, status = processor._run_ocr(processed_image)
                
                results.append({
                    'filename': filename,
                    'text': text,
                    'status': status,
                    'timestamp': ''
                })
                
            except Exception as e:
                results.append({
                    'filename': os.path.basename(image_path),
                    'text': '',
                    'status': f'Error: {str(e)}',
                    'timestamp': ''
                })
        
        return results


def main():
    """Main function demonstrating batch processing."""
    if len(sys.argv) < 3:
        print("Usage: python batch_processing_example.py <output_file> <image1> [image2] ...")
        print("Example: python batch_processing_example.py results.txt image1.png image2.jpg")
        sys.exit(1)
    
    output_file = sys.argv[1]
    image_paths = sys.argv[2:]
    
    # Validate image files
    valid_paths = []
    for path in image_paths:
        if os.path.exists(path):
            valid_paths.append(path)
        else:
            print(f"Warning: File not found: {path}")
    
    if not valid_paths:
        print("Error: No valid image files found")
        sys.exit(1)
    
    print(f"Processing {len(valid_paths)} images...")
    
    try:
        # Process images
        processor = SimpleBatchProcessor()
        results = processor.process_images(valid_paths, "Grayscale")
        
        # Export results
        if output_file.endswith('.csv'):
            ResultExporter.export_to_csv(results, output_file)
        elif output_file.endswith('.json'):
            ResultExporter.export_to_json(results, output_file)
        else:
            ResultExporter.export_to_txt(results, output_file)
        
        # Print summary
        successful = len([r for r in results if r['status'] == 'Success'])
        print(f"\nProcessing completed!")
        print(f"Successfully processed: {successful}/{len(results)} images")
        print(f"Results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error during batch processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()