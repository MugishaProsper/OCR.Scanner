#!/usr/bin/env python3
"""
Setup script for OCR Scanner application.
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="OCR Scanner",
    version="1.1.0",
    author="Mugisha Prosper",
    author_email="nelsonprox92@gmail.com",
    description="Advanced OCR Scanner with Batch Processing capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MugishaProsper/OCR.Scanner",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics :: Capture :: Scanners",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-qt>=4.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "ocr-scanner=ocr_scanner.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ocr_scanner": ["assets/*", "config/*"],
    },
)