#!/usr/bin/env python3
"""
Migration script to help users transition from old structure to new structure.
"""

import os
import sys
import shutil
from pathlib import Path


def main():
    """Main migration function."""
    print("OCR Scanner - Migration to Professional Structure")
    print("=" * 50)
    
    # Check if old file exists
    old_file = Path("ocr-scanner.py")
    if not old_file.exists():
        print("✓ No migration needed - old structure not found")
        return
    
    print("Found legacy ocr-scanner.py file")
    
    # Check if new structure exists
    new_structure = Path("src/ocr_scanner")
    if new_structure.exists():
        print("✓ New structure already exists")
        
        # Ask user if they want to backup old file
        response = input("Do you want to backup the old ocr-scanner.py file? (y/n): ")
        if response.lower() in ['y', 'yes']:
            backup_path = Path("ocr-scanner.py.backup")
            shutil.copy2(old_file, backup_path)
            print(f"✓ Backed up to {backup_path}")
        
        # Ask if they want to remove old file
        response = input("Do you want to remove the old ocr-scanner.py file? (y/n): ")
        if response.lower() in ['y', 'yes']:
            old_file.unlink()
            print("✓ Removed old ocr-scanner.py file")
    else:
        print("✗ New structure not found. Please run the setup first.")
        return
    
    print("\nMigration completed!")
    print("\nNext steps:")
    print("1. Install the new version: pip install -e .")
    print("2. Run the application: ocr-scanner")
    print("3. Or run from source: python -m src.ocr_scanner.main")


if __name__ == "__main__":
    main()