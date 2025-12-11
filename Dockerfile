# Multi-stage build for OCR Scanner
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-spa \
    tesseract-ocr-fra \
    tesseract-ocr-deu \
    tesseract-ocr-ita \
    tesseract-ocr-por \
    tesseract-ocr-rus \
    tesseract-ocr-chi-sim \
    tesseract-ocr-chi-tra \
    tesseract-ocr-jpn \
    tesseract-ocr-kor \
    tesseract-ocr-ara \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    libqt5gui5 \
    libqt5core5a \
    libqt5widgets5 \
    qt5-default \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy source code
COPY . .

# Install package in development mode
RUN pip install -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash ocr_user && \
    chown -R ocr_user:ocr_user /app

USER ocr_user

# Set display for GUI applications
ENV DISPLAY=:99

# Expose port for potential web interface
EXPOSE 8080

# Default command
CMD ["python", "-m", "src.ocr_scanner.main"]

# Production stage
FROM base as production

# Copy only necessary files
COPY src/ ./src/
COPY setup.py pyproject.toml MANIFEST.in LICENSE README.md ./

# Install package
RUN pip install .

# Create non-root user
RUN useradd --create-home --shell /bin/bash ocr_user && \
    chown -R ocr_user:ocr_user /app

USER ocr_user

# Set display for GUI applications
ENV DISPLAY=:99

# Expose port for potential web interface
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import ocr_scanner; print('OK')" || exit 1

# Default command
CMD ["ocr-scanner"]