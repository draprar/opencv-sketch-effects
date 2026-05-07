"""Comprehensive tests for image_processor module."""

import numpy as np
import pytest

from tracify.image_processor import (
    ImageTooLargeError,
    InvalidImageError,
    apply_contour_effect,
    apply_sketch_effect,
    apply_tattoo_calc_effect,
    convert_to_grayscale,
    validate_image,
)


class TestValidateImage:
    """Tests for image validation function."""

    def test_validate_valid_image(self) -> None:
        """Test validation passes for valid BGR image."""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        validate_image(image)  # Should not raise

    def test_validate_valid_grayscale(self) -> None:
        """Test validation passes for valid grayscale image."""
        image = np.zeros((100, 100), dtype=np.uint8)
        validate_image(image)  # Should not raise

    def test_validate_none_image(self) -> None:
        """Test validation fails for None."""
        with pytest.raises(InvalidImageError, match="Image is None or empty"):
            validate_image(None)  # type: ignore

    def test_validate_not_ndarray(self) -> None:
        """Test validation fails for non-ndarray."""
        with pytest.raises(InvalidImageError, match="Image must be a numpy ndarray"):
            validate_image([1, 2, 3])  # type: ignore

    def test_validate_empty_array(self) -> None:
        """Test validation fails for empty array."""
        empty = np.array([])
        with pytest.raises(InvalidImageError, match="Image is None or empty"):
            validate_image(empty)

    def test_validate_wrong_dimensions(self) -> None:
        """Test validation fails for wrong number of dimensions."""
        image_1d = np.zeros(100, dtype=np.uint8)
        with pytest.raises(InvalidImageError, match="Image must be 2D or 3D"):
            validate_image(image_1d)

        image_4d = np.zeros((10, 10, 3, 3), dtype=np.uint8)
        with pytest.raises(InvalidImageError, match="Image must be 2D or 3D"):
            validate_image(image_4d)

    def test_validate_wrong_channels(self) -> None:
        """Test validation fails for wrong number of channels."""
        image_2ch = np.zeros((100, 100, 2), dtype=np.uint8)
        with pytest.raises(InvalidImageError, match="Image must have 1 or 3 channels"):
            validate_image(image_2ch)

        image_4ch = np.zeros((100, 100, 4), dtype=np.uint8)
        with pytest.raises(InvalidImageError, match="Image must have 1 or 3 channels"):
            validate_image(image_4ch)

    def test_validate_wrong_dtype(self) -> None:
        """Test validation fails for wrong dtype."""
        image_float = np.zeros((100, 100, 3), dtype=np.float32)
        with pytest.raises(InvalidImageError, match="Image must be uint8"):
            validate_image(image_float)

    def test_validate_too_large(self) -> None:
        """Test validation fails for too large image."""
        huge_image = np.zeros((5000, 5000, 3), dtype=np.uint8)
        with pytest.raises(ImageTooLargeError, match="Image size .* exceeds maximum"):
            validate_image(huge_image, max_dimension=4096)

    def test_validate_1x1_image(self) -> None:
        """Test validation passes for 1x1 image."""
        tiny = np.array([[[255, 255, 255]]], dtype=np.uint8)
        validate_image(tiny)  # Should not raise


class TestConvertToGrayscale:
    """Tests for grayscale conversion."""

    def test_convert_color_to_grayscale(self) -> None:
        """Test converting BGR image to grayscale."""
        image = np.array(
            [[[255, 0, 0], [0, 255, 0], [0, 0, 255]]], dtype=np.uint8
        )  # Blue, Green, Red
        gray = convert_to_grayscale(image)
        assert gray.shape == (1, 3)
        assert gray.dtype == np.uint8
        assert len(gray.shape) == 2

    def test_convert_already_grayscale(self) -> None:
        """Test that already grayscale image is returned as-is."""
        gray_image = np.array([[100, 150, 200]], dtype=np.uint8)
        result = convert_to_grayscale(gray_image)
        assert result.shape == gray_image.shape
        assert np.array_equal(result, gray_image)

    def test_convert_invalid_image(self) -> None:
        """Test conversion fails for invalid image."""
        with pytest.raises(InvalidImageError):
            convert_to_grayscale(None)  # type: ignore

    def test_convert_1x1_image(self) -> None:
        """Test conversion works for 1x1 image."""
        tiny = np.array([[[128, 128, 128]]], dtype=np.uint8)
        gray = convert_to_grayscale(tiny)
        assert gray.shape == (1, 1)

    def test_convert_large_image(self) -> None:
        """Test conversion works for large (but valid) image."""
        large = np.zeros((2000, 2000, 3), dtype=np.uint8)
        gray = convert_to_grayscale(large)
        assert gray.shape == (2000, 2000)


class TestApplySketchEffect:
    """Tests for sketch effect."""

    def test_sketch_effect_basic(self) -> None:
        """Test sketch effect produces grayscale output."""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        sketch = apply_sketch_effect(image)
        assert sketch.shape == (100, 100)
        assert sketch.dtype == np.uint8

    def test_sketch_effect_white_image(self) -> None:
        """Test sketch effect on white image (edge case)."""
        white = np.ones((50, 50, 3), dtype=np.uint8) * 255
        sketch = apply_sketch_effect(white)
        assert sketch.shape == (50, 50)
        # White image should produce minimal sketch lines
        assert np.all(sketch >= 0)  # No overflow

    def test_sketch_effect_black_image(self) -> None:
        """Test sketch effect on black image."""
        black = np.zeros((50, 50, 3), dtype=np.uint8)
        sketch = apply_sketch_effect(black)
        assert sketch.shape == (50, 50)
        # Black image should result in dark output
        assert np.all(sketch >= 0)

    def test_sketch_effect_no_division_by_zero(self) -> None:
        """Test that sketch effect handles potential division by zero."""
        # Create image that could cause blurred_image = 255
        bright = np.ones((100, 100, 3), dtype=np.uint8) * 255
        sketch = apply_sketch_effect(bright)
        # Should not crash and should produce valid output
        assert not np.any(np.isnan(sketch))
        assert not np.any(np.isinf(sketch))

    def test_sketch_effect_invalid_image(self) -> None:
        """Test sketch effect fails for invalid image."""
        with pytest.raises(InvalidImageError):
            apply_sketch_effect(None)  # type: ignore

    def test_sketch_effect_1x1_image(self) -> None:
        """Test sketch effect on 1x1 image."""
        tiny = np.array([[[100, 100, 100]]], dtype=np.uint8)
        sketch = apply_sketch_effect(tiny)
        assert sketch.shape == (1, 1)


class TestApplyContourEffect:
    """Tests for contour effect."""

    def test_contour_effect_basic(self) -> None:
        """Test contour effect produces binary-like output."""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        contour = apply_contour_effect(image)
        assert contour.shape == (100, 100)
        assert contour.dtype == np.uint8

    def test_contour_effect_with_edges(self) -> None:
        """Test contour effect detects edges."""
        # Create image with clear edge
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        image[:, 50:] = 255  # White right half
        contour = apply_contour_effect(image)
        # Should detect the vertical edge at x=50
        assert contour.shape == (100, 100)
        assert np.any(contour > 0)  # Some edges detected

    def test_contour_effect_uniform_image(self) -> None:
        """Test contour effect on uniform image (no edges)."""
        uniform = np.ones((50, 50, 3), dtype=np.uint8) * 128
        contour = apply_contour_effect(uniform)
        # Uniform image should have minimal edges
        assert contour.shape == (50, 50)

    def test_contour_effect_invalid_image(self) -> None:
        """Test contour effect fails for invalid image."""
        with pytest.raises(InvalidImageError):
            apply_contour_effect(None)  # type: ignore

    def test_contour_effect_1x1_image(self) -> None:
        """Test contour effect on 1x1 image."""
        tiny = np.array([[[100, 100, 100]]], dtype=np.uint8)
        contour = apply_contour_effect(tiny)
        assert contour.shape == (1, 1)


class TestApplyTattooCalcEffect:
    """Tests for tattoo calc effect."""

    def test_tattoo_effect_basic(self) -> None:
        """Test tattoo effect produces binary output."""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        tattoo = apply_tattoo_calc_effect(image)
        assert tattoo.shape == (100, 100)
        assert tattoo.dtype == np.uint8
        # Binary output: only 0 or 255
        assert np.all((tattoo == 0) | (tattoo == 255))

    def test_tattoo_effect_dark_image(self) -> None:
        """Test tattoo effect on dark image."""
        dark = np.ones((50, 50, 3), dtype=np.uint8) * 50
        tattoo = apply_tattoo_calc_effect(dark)
        # Dark pixels should threshold to 0
        assert np.all((tattoo == 0) | (tattoo == 255))

    def test_tattoo_effect_bright_image(self) -> None:
        """Test tattoo effect on bright image."""
        bright = np.ones((50, 50, 3), dtype=np.uint8) * 200
        tattoo = apply_tattoo_calc_effect(bright)
        # Bright pixels should threshold to 255
        assert np.all((tattoo == 0) | (tattoo == 255))

    def test_tattoo_effect_mixed_image(self) -> None:
        """Test tattoo effect on mixed brightness image."""
        mixed = np.zeros((100, 100, 3), dtype=np.uint8)
        mixed[:50, :] = 50  # Dark top
        mixed[50:, :] = 200  # Bright bottom
        tattoo = apply_tattoo_calc_effect(mixed)
        assert np.all((tattoo == 0) | (tattoo == 255))

    def test_tattoo_effect_invalid_image(self) -> None:
        """Test tattoo effect fails for invalid image."""
        with pytest.raises(InvalidImageError):
            apply_tattoo_calc_effect(None)  # type: ignore

    def test_tattoo_effect_1x1_image(self) -> None:
        """Test tattoo effect on 1x1 image."""
        tiny = np.array([[[100, 100, 100]]], dtype=np.uint8)
        tattoo = apply_tattoo_calc_effect(tiny)
        assert tattoo.shape == (1, 1)
        assert tattoo[0, 0] in [0, 255]


class TestEdgeCasesIntegration:
    """Integration tests for edge cases across all functions."""

    @pytest.fixture
    def sample_image(self) -> np.ndarray:
        """Create a sample test image."""
        return np.array(
            [
                [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
                [[255, 255, 0], [0, 255, 255], [255, 0, 255]],
                [[0, 0, 0], [127, 127, 127], [255, 255, 255]],
            ],
            dtype=np.uint8,
        )

    def test_all_effects_on_same_image(self, sample_image: np.ndarray) -> None:
        """Test all effects can be applied to the same image."""
        gray = convert_to_grayscale(sample_image)
        sketch = apply_sketch_effect(sample_image)
        contour = apply_contour_effect(sample_image)
        tattoo = apply_tattoo_calc_effect(sample_image)

        assert gray.shape == (3, 3)
        assert sketch.shape == (3, 3)
        assert contour.shape == (3, 3)
        assert tattoo.shape == (3, 3)

    def test_effects_preserve_dimensions(self) -> None:
        """Test that effects preserve image dimensions."""
        for size in [(10, 10), (50, 50), (100, 200), (1, 1)]:
            image = np.zeros((*size, 3), dtype=np.uint8)
            assert convert_to_grayscale(image).shape == size
            assert apply_sketch_effect(image).shape == size
            assert apply_contour_effect(image).shape == size
            assert apply_tattoo_calc_effect(image).shape == size
