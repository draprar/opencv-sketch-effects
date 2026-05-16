"""Comprehensive tests for main GUI application."""

from pathlib import Path
from unittest.mock import Mock, patch

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
    """Create a sample test image."""
    return np.ones((100, 100, 3), dtype=np.uint8) * 128


@pytest.fixture
def temp_image_file(sample_image: np.ndarray, tmp_path: Path) -> Path:
    """Create a temporary image file."""
    file_path = tmp_path / "test_image.png"
    cv2.imwrite(str(file_path), sample_image)
    return file_path


@pytest.mark.gui
class TestTracifyAppInitialization:
    """Tests for application initialization."""

    @pytest.mark.gui
    def test_app_initializes(self, app: TracifyApp) -> None:
        """Test that app initializes without errors."""
        assert app.original_image is None
        assert app.processed_image is None
        assert app.current_file_path is None
        assert not app.processing

    def test_ui_components_exist(self, app: TracifyApp) -> None:
        """Test that all UI components are created."""
        assert app.load_btn is not None
        assert app.apply_btn is not None
        assert app.save_btn is not None
        assert app.effect_combo is not None
        assert app.image_label is not None
        assert app.progress is not None

    def test_initial_button_states(self, app: TracifyApp) -> None:
        """Test that buttons have correct initial states."""
        assert str(app.load_btn.cget("state")) == "normal"
        assert str(app.apply_btn.cget("state")) == "disabled"
        assert str(app.save_btn.cget("state")) == "disabled"


@pytest.mark.gui
class TestImageLoading:
    """Tests for image loading functionality."""

    @patch("tracify.main.filedialog.askopenfilename")
    @patch("cv2.imread")
    def test_load_valid_image(
        self,
        mock_imread: Mock,
        mock_dialog: Mock,
        app: TracifyApp,
        temp_image_file: Path,
        sample_image: np.ndarray,
    ) -> None:
        """Test loading a valid image."""
        mock_dialog.return_value = str(temp_image_file)
        mock_imread.return_value = sample_image

        app._load_image()

        assert app.original_image is not None
        assert app.current_file_path == temp_image_file
        assert str(app.apply_btn.cget("state")) == "normal"

    @patch("tracify.main.filedialog.askopenfilename")
    def test_load_cancelled(self, mock_dialog: Mock, app: TracifyApp) -> None:
        """Test that cancelling load dialog does nothing."""
        mock_dialog.return_value = ""

        app._load_image()

        assert app.original_image is None
        assert app.current_file_path is None

    @patch("tracify.main.filedialog.askopenfilename")
    @patch("cv2.imread")
    @patch("tracify.main.messagebox.showerror")
    def test_load_corrupted_file(
        self, mock_error: Mock, mock_imread: Mock, mock_dialog: Mock, app: TracifyApp
    ) -> None:
        """Test loading a corrupted file."""
        mock_dialog.return_value = "corrupted.png"
        mock_imread.return_value = None

        app._load_image()

        assert app.original_image is None
        mock_error.assert_called_once()
        assert "Could not read image" in str(mock_error.call_args)

    @patch("tracify.main.filedialog.askopenfilename")
    @patch("cv2.imread")
    @patch("tracify.main.messagebox.showerror")
    def test_load_too_large_image(
        self, mock_error: Mock, mock_imread: Mock, mock_dialog: Mock, app: TracifyApp
    ) -> None:
        """Test loading an image that's too large."""
        huge_image = np.zeros((5000, 5000, 3), dtype=np.uint8)
        mock_dialog.return_value = "huge.png"
        mock_imread.return_value = huge_image

        app._load_image()

        assert app.original_image is None
        mock_error.assert_called_once()
        assert "Too Large" in str(mock_error.call_args)

    @patch("tracify.main.filedialog.askopenfilename")
    @patch("cv2.imread")
    @patch("tracify.main.messagebox.showerror")
    def test_load_invalid_format(
        self, mock_error: Mock, mock_imread: Mock, mock_dialog: Mock, app: TracifyApp
    ) -> None:
        """Test loading an invalid image format."""
        invalid_image = np.zeros((100, 100, 2), dtype=np.uint8)  # 2 channels invalid
        mock_dialog.return_value = "invalid.png"
        mock_imread.return_value = invalid_image

        app._load_image()

        assert app.original_image is None
        mock_error.assert_called_once()

    @patch("tracify.main.filedialog.askopenfilename")
    @patch("tracify.main.messagebox.showerror")
    def test_load_unsupported_extension(
        self, mock_error: Mock, mock_dialog: Mock, app: TracifyApp
    ) -> None:
        """Test loading file with unsupported extension."""
        mock_dialog.return_value = "malicious.exe"

        app._load_image()

        assert app.original_image is None
        mock_error.assert_called_once()
        assert "Unsupported file format" in str(mock_error.call_args)


@pytest.mark.gui
class TestEffectApplication:
    """Tests for applying effects."""

    def test_apply_effect_without_image(self, app: TracifyApp) -> None:
        """Test that applying effect without loaded image does nothing."""
        app._apply_effect()
        assert app.processed_image is None

    def test_apply_grayscale_effect(self, app: TracifyApp, sample_image: np.ndarray) -> None:
        """Test applying grayscale effect."""
        app.original_image = sample_image
        app.effect_var.set("Grayscale")

        # Call _process_image directly (synchronous for testing)
        app._process_image("Grayscale")

        assert app.processed_image is not None
        assert app.processed_image.shape == (100, 100)

    def test_apply_sketch_effect(self, app: TracifyApp, sample_image: np.ndarray) -> None:
        """Test applying sketch effect."""
        app.original_image = sample_image
        app.effect_var.set("Sketch Effect")

        app._process_image("Sketch Effect")

        assert app.processed_image is not None
        assert app.processed_image.shape == (100, 100)

    def test_apply_contour_effect(self, app: TracifyApp, sample_image: np.ndarray) -> None:
        """Test applying contour effect."""
        app.original_image = sample_image
        app.effect_var.set("Contour Effect")

        app._process_image("Contour Effect")

        assert app.processed_image is not None
        assert app.processed_image.shape == (100, 100)

    def test_apply_tattoo_effect(self, app: TracifyApp, sample_image: np.ndarray) -> None:
        """Test applying tattoo calc effect."""
        app.original_image = sample_image
        app.effect_var.set("Tattoo Calc Effect")

        app._process_image("Tattoo Calc Effect")

        assert app.processed_image is not None
        assert app.processed_image.shape == (100, 100)
        # Should be binary
        assert np.all((app.processed_image == 0) | (app.processed_image == 255))

    def test_apply_unknown_effect_shows_error(
        self, app: TracifyApp, sample_image: np.ndarray
    ) -> None:
        """Test that unknown effect shows error via callback."""
        app.original_image = sample_image

        # Call process_image which will handle error via callback
        app._process_image("Unknown Effect")

        # The error should be passed to the processing complete callback
        # We can't easily test the callback without running mainloop,
        # but we can verify the processed_image is None
        assert app.processed_image is None

    def test_processing_enables_save_button(
        self, app: TracifyApp, sample_image: np.ndarray
    ) -> None:
        """Test that successful processing enables save button."""
        app.original_image = sample_image
        app._process_image("Grayscale")

        # Simulate completion callback
        app._on_processing_complete(app.processed_image, None)

        assert str(app.save_btn.cget("state")) == "normal"

    def test_processing_error_shows_message(self, app: TracifyApp) -> None:
        """Test that processing error shows error message."""
        with patch("tracify.main.messagebox.showerror") as mock_error:
            error = ValueError("Test error")
            app._on_processing_complete(None, error)

            mock_error.assert_called_once()
            assert "Processing Error" in str(mock_error.call_args)


@pytest.mark.gui
class TestImageSaving:
    """Tests for saving processed images."""

    def test_save_without_processed_image(self, app: TracifyApp) -> None:
        """Test that saving without processed image does nothing."""
        with patch("tracify.main.filedialog.asksaveasfilename") as mock_dialog:
            app._save_image()
            mock_dialog.assert_not_called()

    @patch("tracify.main.filedialog.asksaveasfilename")
    @patch("cv2.imwrite")
    @patch("tracify.main.messagebox.showinfo")
    def test_save_successful(
        self,
        mock_info: Mock,
        mock_imwrite: Mock,
        mock_dialog: Mock,
        app: TracifyApp,
        sample_image: np.ndarray,
        tmp_path: Path,
    ) -> None:
        """Test successful image save."""
        save_path = tmp_path / "saved.png"
        mock_dialog.return_value = str(save_path)
        mock_imwrite.return_value = True

        app.processed_image = sample_image
        app._save_image()

        mock_imwrite.assert_called_once()
        mock_info.assert_called_once()
        assert "Success" in str(mock_info.call_args)

    @patch("tracify.main.filedialog.asksaveasfilename")
    def test_save_cancelled(self, mock_dialog: Mock, app: TracifyApp) -> None:
        """Test that cancelling save dialog does nothing."""
        mock_dialog.return_value = ""
        app.processed_image = np.zeros((100, 100), dtype=np.uint8)

        with patch("cv2.imwrite") as mock_imwrite:
            app._save_image()
            mock_imwrite.assert_not_called()

    @patch("tracify.main.filedialog.asksaveasfilename")
    @patch("cv2.imwrite")
    @patch("tracify.main.messagebox.showerror")
    def test_save_failure(
        self,
        mock_error: Mock,
        mock_imwrite: Mock,
        mock_dialog: Mock,
        app: TracifyApp,
        tmp_path: Path,
    ) -> None:
        """Test handling of save failure."""
        save_path = tmp_path / "failed.png"
        mock_dialog.return_value = str(save_path)
        mock_imwrite.return_value = False

        app.processed_image = np.zeros((100, 100), dtype=np.uint8)
        app._save_image()

        mock_error.assert_called_once()
        assert "Save Error" in str(mock_error.call_args)


@pytest.mark.gui
class TestDisplayImage:
    """Tests for image display functionality."""

    def test_display_grayscale_image(self, app: TracifyApp, sample_image: np.ndarray) -> None:
        """Test displaying a grayscale image."""
        gray = cv2.cvtColor(sample_image, cv2.COLOR_BGR2GRAY)
        app._display_image(gray)
        # Just ensure no errors occur

    def test_display_color_image(self, app: TracifyApp, sample_image: np.ndarray) -> None:
        """Test displaying a color image."""
        app._display_image(sample_image)
        # Just ensure no errors occur

    def test_display_large_image_is_resized(self, app: TracifyApp) -> None:
        """Test that large images are resized for display."""
        large_image = np.ones((2000, 2000, 3), dtype=np.uint8) * 128
        app._display_image(large_image)
        # Image should be displayed without error


@pytest.mark.gui
class TestProcessingState:
    """Tests for processing state management."""

    def test_set_processing_true_disables_buttons(self, app: TracifyApp) -> None:
        """Test that setting processing=True disables buttons."""
        app.original_image = np.zeros((100, 100, 3), dtype=np.uint8)
        app._set_processing(True)

        assert str(app.load_btn.cget("state")) == "disabled"
        assert str(app.apply_btn.cget("state")) == "disabled"
        assert str(app.save_btn.cget("state")) == "disabled"
        assert app.processing is True

    def test_set_processing_false_enables_buttons(self, app: TracifyApp) -> None:
        """Test that setting processing=False enables appropriate buttons."""
        app.original_image = np.zeros((100, 100, 3), dtype=np.uint8)
        app.processed_image = np.zeros((100, 100), dtype=np.uint8)
        app._set_processing(False)

        assert str(app.load_btn.cget("state")) == "normal"
        assert str(app.apply_btn.cget("state")) == "normal"
        assert str(app.save_btn.cget("state")) == "normal"
        assert app.processing is False


@pytest.mark.gui
class TestEdgeCases:
    """Edge case tests for the application."""

    def test_1x1_image_processing(self, app: TracifyApp) -> None:
        """Test processing a 1x1 pixel image."""
        tiny = np.array([[[100, 100, 100]]], dtype=np.uint8)
        app.original_image = tiny

        app._process_image("Grayscale")
        assert app.processed_image is not None
        assert app.processed_image.shape == (1, 1)

    def test_suggested_filename_with_original(self, app: TracifyApp, tmp_path: Path) -> None:
        """Test that suggested filename is based on original."""
        app.current_file_path = tmp_path / "test.png"
        app.processed_image = np.zeros((100, 100), dtype=np.uint8)

        with patch("tracify.main.filedialog.asksaveasfilename") as mock_dialog:
            mock_dialog.return_value = ""
            app._save_image()

            # Check that initialfile argument contains "_processed"
            call_kwargs = mock_dialog.call_args[1]
            assert "_processed" in call_kwargs["initialfile"]
