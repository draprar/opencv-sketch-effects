"""Integration tests for full workflow scenarios."""

from pathlib import Path

import cv2
import numpy as np
import pytest
import ttkbootstrap as ttk

from tracify.main import TracifyApp


@pytest.fixture
def root() -> ttk.Window:
    """Create a test ttkbootstrap window."""
    window = ttk.Window(themename="darkly")
    yield window
    try:
        window.destroy()
    except Exception:
        pass


@pytest.fixture
def app(root: ttk.Window) -> TracifyApp:
    """Create a TracifyApp instance for testing."""
    return TracifyApp(root)


@pytest.fixture
def sample_image() -> np.ndarray:
    """Create a sample test image with clear features."""
    # Create 200x200 image with distinct regions
    image = np.zeros((200, 200, 3), dtype=np.uint8)
    # White square in center
    image[50:150, 50:150] = 255
    # Red vertical stripe
    image[:, 80:90] = [0, 0, 255]
    # Blue horizontal stripe
    image[80:90, :] = [255, 0, 0]
    return image


@pytest.fixture
def temp_image_file(sample_image: np.ndarray, tmp_path: Path) -> Path:
    """Create a temporary image file."""
    file_path = tmp_path / "test_image.png"
    cv2.imwrite(str(file_path), sample_image)
    return file_path


@pytest.mark.gui
class TestFullWorkflow:
    """Test complete workflows from load to save."""

    def test_load_apply_grayscale_save(
        self, app: TracifyApp, temp_image_file: Path, tmp_path: Path
    ) -> None:
        """Test full workflow: load → grayscale → save."""
        # Simulate loading
        image = cv2.imread(str(temp_image_file))
        assert image is not None

        app.original_image = image
        app.current_file_path = temp_image_file

        # Apply grayscale effect
        app.effect_var.set("Grayscale")
        app._process_image("Grayscale")

        assert app.processed_image is not None
        assert app.processed_image.shape == (200, 200)
        assert app.processed_image.dtype == np.uint8

        # Save the result
        save_path = tmp_path / "output_grayscale.png"
        success = cv2.imwrite(str(save_path), app.processed_image)
        assert success
        assert save_path.exists()

        # Verify saved file can be loaded
        loaded = cv2.imread(str(save_path), cv2.IMREAD_GRAYSCALE)
        assert loaded is not None
        assert np.array_equal(loaded, app.processed_image)

    def test_load_apply_sketch_save(
        self, app: TracifyApp, temp_image_file: Path, tmp_path: Path
    ) -> None:
        """Test full workflow: load → sketch → save."""
        image = cv2.imread(str(temp_image_file))
        app.original_image = image
        app.current_file_path = temp_image_file

        # Apply sketch effect
        app.effect_var.set("Sketch Effect")
        app._process_image("Sketch Effect")

        assert app.processed_image is not None
        assert app.processed_image.shape == (200, 200)

        # Save and verify
        save_path = tmp_path / "output_sketch.png"
        success = cv2.imwrite(str(save_path), app.processed_image)
        assert success
        assert save_path.exists()

        # Verify file size is reasonable
        file_size = save_path.stat().st_size
        assert file_size > 100  # Should have some content

    def test_load_apply_contour_save(
        self, app: TracifyApp, temp_image_file: Path, tmp_path: Path
    ) -> None:
        """Test full workflow: load → contour → save."""
        image = cv2.imread(str(temp_image_file))
        app.original_image = image

        app.effect_var.set("Contour Effect")
        app._process_image("Contour Effect")

        assert app.processed_image is not None

        # Contour should detect edges in our test image
        edges_detected = np.any(app.processed_image > 0)
        assert edges_detected, "Contour effect should detect edges"

        save_path = tmp_path / "output_contour.png"
        success = cv2.imwrite(str(save_path), app.processed_image)
        assert success

    def test_load_apply_tattoo_save(
        self, app: TracifyApp, temp_image_file: Path, tmp_path: Path
    ) -> None:
        """Test full workflow: load → tattoo → save."""
        image = cv2.imread(str(temp_image_file))
        app.original_image = image

        app.effect_var.set("Tattoo Calc Effect")
        app._process_image("Tattoo Calc Effect")

        assert app.processed_image is not None
        # Binary image check
        assert np.all((app.processed_image == 0) | (app.processed_image == 255))

        save_path = tmp_path / "output_tattoo.png"
        success = cv2.imwrite(str(save_path), app.processed_image)
        assert success

    def test_sequential_effects(self, app: TracifyApp, temp_image_file: Path) -> None:
        """Test applying multiple effects sequentially."""
        image = cv2.imread(str(temp_image_file))
        app.original_image = image

        effects = ["Grayscale", "Sketch Effect", "Contour Effect", "Tattoo Calc Effect"]

        for effect in effects:
            app.effect_var.set(effect)
            app._process_image(effect)
            assert app.processed_image is not None
            # Each effect should produce valid output
            assert app.processed_image.size > 0

    def test_reload_and_reprocess(self, app: TracifyApp, temp_image_file: Path) -> None:
        """Test loading, processing, then loading again."""
        # First load and process
        image = cv2.imread(str(temp_image_file))
        app.original_image = image
        app._process_image("Grayscale")
        first_result = app.processed_image.copy()

        # Load same image again
        app.original_image = image
        app.processed_image = None
        app._process_image("Grayscale")
        second_result = app.processed_image

        # Results should be identical
        assert np.array_equal(first_result, second_result)

    def test_large_but_valid_image(self, app: TracifyApp, tmp_path: Path) -> None:
        """Test processing a large (but within limits) image."""
        # Create 3000x3000 image (below 4096 limit)
        large_image = np.random.randint(0, 255, (3000, 3000, 3), dtype=np.uint8)
        large_path = tmp_path / "large_image.png"
        cv2.imwrite(str(large_path), large_image)

        loaded = cv2.imread(str(large_path))
        app.original_image = loaded

        # Should process without errors
        app._process_image("Grayscale")
        assert app.processed_image is not None
        assert app.processed_image.shape == (3000, 3000)

    def test_various_formats(self, tmp_path: Path) -> None:
        """Test loading and saving different image formats."""
        from tracify.image_processor import convert_to_grayscale

        # Create test image
        test_image = np.ones((100, 100, 3), dtype=np.uint8) * 128

        formats = [".png", ".jpg", ".bmp"]
        for fmt in formats:
            # Save in format
            save_path = tmp_path / f"test{fmt}"
            cv2.imwrite(str(save_path), test_image)

            # Load and process
            loaded = cv2.imread(str(save_path))
            assert loaded is not None

            result = convert_to_grayscale(loaded)
            assert result is not None

            # Save processed
            output_path = tmp_path / f"output{fmt}"
            success = cv2.imwrite(str(output_path), result)
            assert success


@pytest.mark.gui
class TestEdgeCaseWorkflows:
    """Test edge cases in full workflows."""

    def test_process_1x1_image(self, app: TracifyApp, tmp_path: Path) -> None:
        """Test processing minimum size image."""
        tiny = np.array([[[100, 100, 100]]], dtype=np.uint8)
        tiny_path = tmp_path / "tiny.png"
        cv2.imwrite(str(tiny_path), tiny)

        loaded = cv2.imread(str(tiny_path))
        app.original_image = loaded

        # All effects should work
        for effect in ["Grayscale", "Sketch Effect", "Contour Effect", "Tattoo Calc Effect"]:
            app._process_image(effect)
            assert app.processed_image is not None
            assert app.processed_image.shape[0] == 1
            assert app.processed_image.shape[1] == 1

    def test_all_black_image(self, app: TracifyApp, tmp_path: Path) -> None:
        """Test processing all-black image."""
        black = np.zeros((100, 100, 3), dtype=np.uint8)
        black_path = tmp_path / "black.png"
        cv2.imwrite(str(black_path), black)

        loaded = cv2.imread(str(black_path))
        app.original_image = loaded

        app._process_image("Sketch Effect")
        assert app.processed_image is not None
        # Should not crash, even if result is all dark

    def test_all_white_image(self, app: TracifyApp, tmp_path: Path) -> None:
        """Test processing all-white image."""
        white = np.ones((100, 100, 3), dtype=np.uint8) * 255
        white_path = tmp_path / "white.png"
        cv2.imwrite(str(white_path), white)

        loaded = cv2.imread(str(white_path))
        app.original_image = loaded

        app._process_image("Sketch Effect")
        assert app.processed_image is not None
        # Should handle division edge case
        assert not np.any(np.isnan(app.processed_image))
        assert not np.any(np.isinf(app.processed_image))
