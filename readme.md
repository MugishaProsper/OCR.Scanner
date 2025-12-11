# Advanced OCR Scanner with Batch Processing

A professional, comprehensive GUI-based OCR (Optical Character Recognition) scanner built with PyQt5 and Tesseract. Features include single image processing, batch processing capabilities, and multiple export formats.

## Features

✅ **Multiple Input Sources**
- Load images from files (PNG, JPG, JPEG, BMP, TIFF)
- Live camera input with frame capture

✅ **ROI (Region of Interest) Selection**
- Click and drag to select specific areas for OCR
- Visual feedback with green rectangle overlay

✅ **Image Preprocessing**
- Grayscale conversion
- Binary threshold adjustment
- Adaptive threshold
- Noise reduction (denoising)

✅ **OCR Capabilities**
- Extract text from entire image or selected ROI
- Display extracted text in dedicated text area
- Text overlay showing detected text positions on image

✅ **Batch Processing**
- Process multiple images at once
- Apply consistent preprocessing to all images
- Export results to TXT or CSV format
- Progress tracking and cancellation support
- Use ROI settings from single image processing

✅ **User-Friendly Interface**
- Clean, organized GUI with grouped controls
- Tabbed interface for single and batch processing
- Real-time preview and progress tracking
- Easy-to-use buttons and controls

## Prerequisites

Before running the application, ensure you have the following installed:

### 1. Python
- Python 3.7 or higher

### 2. Tesseract OCR Engine
- **Windows**: Download from [GitHub Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt install tesseract-ocr`

### 3. Python Packages
Install required packages using pip:

```bash
pip install -r requirements.txt
```

## Installation

### Option 1: Install from Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/Chael250/ocr-scanner.git
cd ocr-scanner

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Option 2: Install from PyPI (Coming Soon)

```bash
pip install ocr-scanner
```

### Option 3: Basic Installation

```bash
# Clone and install dependencies only
git clone https://github.com/Chael250/ocr-scanner.git
cd ocr-scanner
pip install -r requirements.txt
```

### Step 3: Install Tesseract OCR

**Windows:**
1. Download installer from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run installer and note installation path (usually `C:\Program Files\Tesseract-OCR`)
3. Add Tesseract to system PATH or update the code on Windows:

```python
# Add this line at the top of ocr_scanner.py if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr
```

## Usage

### Running the Application

#### If installed with pip:
```bash
ocr-scanner
```

#### If running from source:
```bash
# From project root
python -m src.ocr_scanner.main

# Or using the old file (deprecated)
python ocr-scanner.py
```

#### Using Make (if available):
```bash
make run
```

### Using the Application

#### 1. **Load an Image**
- Click "Load Image" button
- Select an image file from your computer
- Image will appear in the center preview area

#### 2. **Use Camera (Alternative)**
- Click "Start Camera" to activate webcam
- Click "Capture Frame" to capture current frame
- Camera will stop automatically after capture

#### 3. **Select ROI (Optional)**
- Click "Select ROI" button
- Click and drag on the image to select region
- Green rectangle shows selected area
- Click "Clear ROI" to remove selection

#### 4. **Apply Preprocessing (Optional)**
- Select preprocessing method from dropdown:
  - **None**: Original image
  - **Grayscale**: Convert to black and white
  - **Threshold**: Binary threshold (adjustable)
  - **Adaptive Threshold**: Automatic local thresholding
  - **Denoise**: Remove noise from image
- Adjust threshold slider for binary threshold method

#### 5. **Run OCR**
- Click "Run OCR" button
- Extracted text appears in right panel
- Works on entire image or selected ROI

#### 6. **Show Text Overlay**
- Click "Show Text Overlay" after running OCR
- View detected text boxes on image
- Green rectangles show text locations
- Blue text shows extracted words

### Batch Processing

#### 1. **Switch to Batch Processing Tab**
- Click on "Batch Processing" tab
- Access batch processing features

#### 2. **Select Multiple Images**
- Click "Select Images" button
- Choose multiple image files (Ctrl+click or Shift+click)
- Selected files appear in the list

#### 3. **Configure Batch Settings**
- Select preprocessing method from dropdown
- Adjust threshold if using threshold method
- Optionally use ROI from single image tab

#### 4. **Start Batch Processing**
- Click "Start Batch OCR" button
- Monitor progress with progress bar
- Cancel processing if needed

#### 5. **View and Export Results**
- Results appear in the table with filename, status, and extracted text
- Click "Export Results" to save as TXT or CSV file
- Choose export format and location

## Project Structure

```
ocr-scanner/
│
├── src/                          # Source code
│   └── ocr_scanner/             # Main package
│       ├── __init__.py          # Package initialization
│       ├── main.py              # Application entry point
│       ├── config/              # Configuration modules
│       │   ├── __init__.py
│       │   └── settings.py      # Application settings
│       ├── core/                # Core processing modules
│       │   ├── __init__.py
│       │   ├── batch_processor.py    # Batch processing logic
│       │   └── image_processor.py    # Image processing utilities
│       ├── gui/                 # GUI modules
│       │   ├── __init__.py
│       │   ├── main_window.py        # Main application window
│       │   ├── single_image_tab.py   # Single image processing tab
│       │   └── batch_processing_tab.py # Batch processing tab
│       └── utils/               # Utility modules
│           ├── __init__.py
│           ├── export.py             # Export functionality
│           └── image_utils.py        # Image utility functions
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_batch_processor.py
│   └── test_image_processor.py
├── examples/                    # Usage examples
│   ├── basic_usage.py
│   └── batch_processing_example.py
├── docs/                        # Documentation (future)
├── assets/                      # Application assets (future)
├── config/                      # Configuration files (future)
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── setup.py                     # Setup script
├── pyproject.toml              # Modern Python project configuration
├── Makefile                    # Build and development commands
├── LICENSE                     # MIT License
├── MANIFEST.in                 # Package manifest
├── README.md                   # This file
├── images/                     # Sample test images
│   └── image.png
└── ocr-scanner.py             # Legacy entry point (deprecated)
```

## Dependencies

All dependencies are listed in `requirements.txt`:

```
PyQt5==5.15.10
opencv-python==4.8.1.78
pytesseract==0.3.10
Pillow==10.1.0
numpy==1.24.3
```

## Troubleshooting

### Issue: "Tesseract not found"
**Solution**: Ensure Tesseract is installed and added to PATH, or specify path in code:
```python
pytesseract.pytesseract.tesseract_cmd = r'/path/to/tesseract'
```

### Issue: Camera not working
**Solution**: 
- Check camera permissions
- Try changing camera index: `cv2.VideoCapture(1)` instead of `cv2.VideoCapture(0)`
- Ensure no other application is using the camera

### Issue: Poor OCR accuracy
**Solution**:
- Use preprocessing (Threshold or Adaptive Threshold)
- Ensure good image quality and lighting
- Select ROI to focus on specific text area
- Use higher resolution images

### Issue: GUI not displaying properly
**Solution**:
- Update PyQt5: `pip install --upgrade PyQt5`
- Check display scaling settings
- Try running with different Python version

## Tips for Best Results

1. **Image Quality**: Use high-resolution, well-lit images
2. **Preprocessing**: Try different methods for optimal results
3. **ROI Selection**: Focus on specific text areas for better accuracy
4. **Contrast**: Ensure good contrast between text and background
5. **Orientation**: Keep text horizontal for best recognition

## Video Demonstration Requirements

For the assignment submission, your video should show:

1. ✅ Application startup
2. ✅ Loading an image OR starting camera
3. ✅ Selecting ROI (click and drag demonstration)
4. ✅ Applying preprocessing (optional but recommended)
5. ✅ Clicking "Run OCR" button
6. ✅ Extracted text displayed in text area
7. ✅ Text overlay visualization (optional)

**Recommended video length**: 20-40 seconds

## Technical Details

### OCR Engine
- **Tesseract OCR**: Open-source OCR engine developed by Google
- **Language**: Supports 100+ languages (default: English)
- **Accuracy**: Depends on image quality and preprocessing

### GUI Framework
- **PyQt5**: Professional Python GUI framework
- **Layout**: Responsive design with three panels
- **Events**: Mouse events for ROI selection

### Image Processing
- **OpenCV**: Computer vision library for preprocessing
- **PIL/Pillow**: Image handling for Tesseract compatibility
- **NumPy**: Numerical operations on image arrays

## Development

### Setting up Development Environment

```bash
# Clone repository
git clone https://github.com/Chael250/ocr-scanner.git
cd ocr-scanner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
make install-dev
# or
pip install -e ".[dev]"
```

### Development Commands

```bash
# Run tests
make test

# Run linting
make lint

# Format code
make format

# Build package
make build

# Clean build artifacts
make clean
```

### Code Quality

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking
- **pytest** for testing

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Future Enhancements

- [ ] Multi-language support selection
- [x] Export text to file (TXT, CSV, JSON) - **IMPLEMENTED**
- [x] Batch processing multiple images - **IMPLEMENTED**
- [x] Professional project structure - **IMPLEMENTED**
- [x] Comprehensive testing suite - **IMPLEMENTED**
- [x] Development tooling and CI/CD setup - **IMPLEMENTED**
- [ ] Text editing and correction
- [ ] OCR confidence threshold adjustment
- [ ] Image rotation and perspective correction
- [ ] Batch processing with different ROI per image
- [ ] Resume interrupted batch processing
- [ ] Image format conversion during batch processing
- [ ] Plugin system for custom preprocessing
- [ ] Web interface version
- [ ] Docker containerization

---

**Note**: Make sure to test the application before submission and record your video demonstration showing all required features!