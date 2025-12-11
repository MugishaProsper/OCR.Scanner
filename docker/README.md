# Docker Setup for OCR Scanner

This directory contains Docker configuration for running OCR Scanner in containerized environments.

## Quick Start

### Development Environment

```bash
# Build and run development container
docker-compose up ocr-scanner-dev

# Or run interactively
docker-compose run --rm ocr-scanner-dev bash
```

### Production Environment

```bash
# Build and run production container
docker-compose up ocr-scanner-prod
```

### Headless Processing

```bash
# Run batch processing without GUI
docker-compose up ocr-scanner-headless
```

## Building Images

### Development Image

```bash
docker build --target development -t ocr-scanner:dev .
```

### Production Image

```bash
docker build --target production -t ocr-scanner:prod .
```

## Running Containers

### With GUI Support (Linux)

```bash
# Allow X11 forwarding
xhost +local:docker

# Run with GUI
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $(pwd)/data:/app/data \
  ocr-scanner:dev
```

### Headless Mode

```bash
# Run without GUI for batch processing
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  ocr-scanner:prod \
  python -m examples.batch_processing_example /app/data/results.txt /app/data/images/*.png
```

### Web Interface (Future)

```bash
# Run with web interface
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  ocr-scanner:prod \
  python -m ocr_scanner.web.app
```

## Environment Variables

- `DISPLAY`: X11 display for GUI applications
- `QT_X11_NO_MITSHM`: Disable shared memory for Qt applications
- `TESSERACT_CMD`: Path to Tesseract executable (default: auto-detected)
- `OCR_LANGUAGE`: Default OCR language (default: eng)
- `LOG_LEVEL`: Logging level (default: INFO)

## Volume Mounts

- `/app/data`: Application data directory
- `/app/config`: Configuration files
- `/app/plugins`: Custom plugins directory
- `/app/logs`: Log files

## Supported Languages

The Docker image includes Tesseract language packs for:

- English (eng)
- Spanish (spa)
- French (fra)
- German (deu)
- Italian (ita)
- Portuguese (por)
- Russian (rus)
- Chinese Simplified (chi_sim)
- Chinese Traditional (chi_tra)
- Japanese (jpn)
- Korean (kor)
- Arabic (ara)

## Troubleshooting

### GUI Issues

If you encounter GUI issues:

1. Ensure X11 forwarding is enabled:
   ```bash
   xhost +local:docker
   ```

2. Check DISPLAY variable:
   ```bash
   echo $DISPLAY
   ```

3. For WSL2/Windows, use X11 server like VcXsrv or Xming

### Permission Issues

If you encounter permission issues:

1. Check file ownership:
   ```bash
   ls -la data/
   ```

2. Fix permissions:
   ```bash
   sudo chown -R $USER:$USER data/
   ```

### Memory Issues

For large batch processing:

1. Increase Docker memory limit
2. Use smaller batch sizes
3. Enable swap if needed

## Development

### Building Custom Images

```bash
# Build with custom base image
docker build --build-arg BASE_IMAGE=python:3.10-slim -t ocr-scanner:custom .

# Build with additional languages
docker build --build-arg EXTRA_LANGUAGES="tesseract-ocr-hin tesseract-ocr-tha" -t ocr-scanner:multilang .
```

### Debugging

```bash
# Run with debug mode
docker run -it --rm \
  -e LOG_LEVEL=DEBUG \
  -v $(pwd):/app \
  ocr-scanner:dev \
  python -m ocr_scanner.main --debug
```

### Testing

```bash
# Run tests in container
docker run --rm \
  -v $(pwd):/app \
  ocr-scanner:dev \
  python -m pytest tests/ -v
```