# Image Transformer
![CI](https://github.com/draprar/opencv-sketch-effects/actions/workflows/python-app.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Code style](https://img.shields.io/badge/code%20style-ruff-261230)

![Screenshot](media/screenshot.png)

Python desktop image-processing application for turning images into clean reference visuals for tracing, sketching, and tattoo prep. Built with Python's standard-library GUI toolkit (tkinter) and OpenCV.

## Features

- Sketch effect: converts images into sketch-like drawings with realistic pencil appearance
- Contour detection: highlights edges and contours for tracing and technical use
- Tattoo template generation: creates high-contrast binary images using adaptive thresholding
- Grayscale conversion: quick conversion to grayscale
- Visual progress feedback during processing
- Comprehensive error validation with user-friendly messages

## Requirements

- Python 3.11 or higher
- `numpy`, `opencv-python`, `pillow`, `ttkbootstrap`


## Installation

1. Clone the repository:
   ```
   git clone https://github.com/draprar/opencv-sketch-effects.git
   cd opencv-sketch-effects
   ```

2. Install dependencies using uv:
   ```
   uv sync
   ```

3. Run the application:
   ```
   uv run tracify
   ```

## Usage

Load an image, select an effect from the dropdown menu, adjust parameters as needed, apply the effect, and save the result. Supported formats: PNG, JPG, JPEG, BMP, TIFF. Maximum image size: 4096×4096 pixels.

## Project Structure

```
├── .github/
│   └── workflows/
│       └── python-app.yml
├── src/
│   └── tracify/
│       ├── __init__.py
│       ├── config.py
│       ├── image_processor.py
│       └── main.py
├── tests/
│   ├── test_image_processor.py
│   ├── test_integration.py
│   └── test_main.py
├── media/
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
└── uv.lock
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
