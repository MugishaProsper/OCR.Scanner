"""
Export utilities for batch processing results.
"""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ResultExporter:
    """Handles exporting of batch processing results."""
    
    @staticmethod
    def export_to_txt(results: List[Dict[str, Any]], file_path: str) -> None:
        """
        Export results to text file.
        
        Args:
            results: List of result dictionaries
            file_path: Output file path
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("OCR Batch Processing Results\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total files processed: {len(results)}\n\n")
                
                for i, result in enumerate(results, 1):
                    f.write(f"File {i}: {result['filename']}\n")
                    f.write(f"Status: {result['status']}\n")
                    f.write(f"Processed: {result['timestamp']}\n")
                    f.write("Extracted Text:\n")
                    f.write("-" * 30 + "\n")
                    f.write(result['text'] if result['text'] else "(No text detected)")
                    f.write("\n" + "=" * 50 + "\n\n")
            
            logger.info(f"Results exported to TXT: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to export to TXT: {e}")
            raise
    
    @staticmethod
    def export_to_csv(results: List[Dict[str, Any]], file_path: str) -> None:
        """
        Export results to CSV file.
        
        Args:
            results: List of result dictionaries
            file_path: Output file path
        """
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Filename', 'Status', 'Timestamp', 'Extracted Text'])
                
                for result in results:
                    writer.writerow([
                        result['filename'],
                        result['status'], 
                        result['timestamp'],
                        result['text'].replace('\n', ' ').replace('\r', ' ')
                    ])
            
            logger.info(f"Results exported to CSV: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            raise
    
    @staticmethod
    def export_to_json(results: List[Dict[str, Any]], file_path: str) -> None:
        """
        Export results to JSON file.
        
        Args:
            results: List of result dictionaries
            file_path: Output file path
        """
        try:
            export_data = {
                "metadata": {
                    "generated": datetime.now().isoformat(),
                    "total_files": len(results),
                    "version": "1.1.0"
                },
                "results": results
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results exported to JSON: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to export to JSON: {e}")
            raise