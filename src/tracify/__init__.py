"""Tracify - Image sketch effects application.

A playful GUI app for converting images to sketch effects, contours, and tattoo stencils.
"""

__version__ = "0.1.0"
__author__ = "Walery"

from .image_processor import (
    ImageTooLargeError,
    InvalidImageError,
    apply_contour_effect,
    apply_sketch_effect,
    apply_tattoo_calc_effect,
    convert_to_grayscale,
    validate_image,
)

__all__ = [
    "InvalidImageError",
    "ImageTooLargeError",
    "validate_image",
    "convert_to_grayscale",
    "apply_sketch_effect",
    "apply_contour_effect",
    "apply_tattoo_calc_effect",
]
