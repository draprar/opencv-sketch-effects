"""Image processing functions for Tracify application.

This module provides various image processing effects including:
- Grayscale conversion
- Sketch effect
- Contour detection
- Tattoo template generation

All functions validate input images and handle edge cases appropriately.
"""

from typing import Any

import cv2
import numpy as np


class InvalidImageError(ValueError):
    """Raised when an invalid image is provided."""


class ImageTooLargeError(ValueError):
    """Raised when an image exceeds maximum allowed dimensions."""


def validate_image(image: Any, max_dimension: int = 4096) -> None:
    """Validate that an image meets requirements for processing.

    Args:
        image: The image to validate (should be np.ndarray).
        max_dimension: Maximum allowed width or height in pixels.

    Raises:
        InvalidImageError: If image is None, empty, has wrong dimensions, channels, or dtype.
        ImageTooLargeError: If image dimensions exceed max_dimension.
    """
    if image is None or (isinstance(image, np.ndarray) and image.size == 0):
        raise InvalidImageError("Image is None or empty")

    if not isinstance(image, np.ndarray):
        raise InvalidImageError("Image must be a numpy ndarray")

    if image.ndim not in [2, 3]:
        raise InvalidImageError(f"Image must be 2D or 3D, got {image.ndim}D")

    if image.ndim == 3 and image.shape[2] not in [1, 3]:
        raise InvalidImageError(f"Image must have 1 or 3 channels, got {image.shape[2]} channels")

    if image.dtype != np.uint8:
        raise InvalidImageError(f"Image must be uint8, got {image.dtype}")

    height, width = image.shape[:2]
    if height > max_dimension or width > max_dimension:
        raise ImageTooLargeError(
            f"Image size ({width}x{height}) exceeds maximum allowed dimension "
            f"({max_dimension}x{max_dimension}). Please resize your image."
        )


def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert an input image to grayscale.

    Args:
        image: Input image in BGR format (3 channels) or already grayscale (1 channel).

    Returns:
        Grayscale image as 2D numpy array.

    Raises:
        InvalidImageError: If image is invalid.
    """
    validate_image(image)

    # If already grayscale, return as-is
    if image.ndim == 2:
        return image

    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def apply_sketch_effect(image: np.ndarray) -> np.ndarray:
    """Convert an image into a sketch-like representation.

    Uses Gaussian blur and division to create a pencil sketch effect.
    Handles potential division by zero by clamping denominator.

    Args:
        image: Input image in BGR format.

    Returns:
        Sketch-like grayscale image.

    Raises:
        InvalidImageError: If image is invalid.
    """
    validate_image(image)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inverted_image = cv2.bitwise_not(gray_image)
    blurred_image = cv2.GaussianBlur(inverted_image, (21, 21), 0)

    # Prevent division by zero by clamping minimum value to 1
    denominator = np.maximum(255 - blurred_image, 1)
    sketch_image = cv2.divide(gray_image, denominator, scale=256)

    return sketch_image


def apply_contour_effect(image: np.ndarray) -> np.ndarray:
    """Extract contours from an image using Canny edge detection.

    Args:
        image: Input image in BGR format.

    Returns:
        Binary edge map showing detected contours.

    Raises:
        InvalidImageError: If image is invalid.
    """
    validate_image(image)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray_image, 50, 150)

    return edges


def apply_tattoo_calc_effect(image: np.ndarray) -> np.ndarray:
    """Generate a high-contrast binary image suitable for tattoo templates.

    Uses Otsu's method for adaptive thresholding to handle various lighting conditions.

    Args:
        image: Input image in BGR format.

    Returns:
        Binary image (only values 0 or 255).

    Raises:
        InvalidImageError: If image is invalid.
    """
    validate_image(image)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Use Otsu's thresholding for better adaptive results
    _, binary_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return binary_image
