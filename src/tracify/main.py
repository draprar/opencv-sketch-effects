"""Main GUI application for Tracify using tkinter and ttkbootstrap."""

import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import cv2
import numpy as np
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from ttkbootstrap.constants import CENTER, E, N, S, W

from .image_processor import (
    ImageTooLargeError,
    InvalidImageError,
    apply_contour_effect,
    apply_sketch_effect,
    apply_tattoo_calc_effect,
    convert_to_grayscale,
)


class TracifyApp:
    """Main application window for image processing with Tracify."""

    def __init__(self, root: ttk.Window) -> None:
        """Initialize the Tracify application.

        Args:
            root: The root ttkbootstrap window.
        """
        self.root = root
        self.root.title("Tracify - Image Sketch Effects")
        self.root.geometry("900x700")

        # State variables
        self.original_image: np.ndarray | None = None
        self.processed_image: np.ndarray | None = None
        self.current_file_path: Path | None = None
        self.processing = False

        # UI Components
        self._init_ui()

    def _init_ui(self) -> None:
        """Set up the user interface components."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.grid(row=0, column=0, sticky=(N, S, E, W))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Control panel at top
        self._create_control_panel(main_frame)

        # Image display area
        self._create_image_display(main_frame)

        # Progress bar (initially hidden)
        self.progress = ttk.Progressbar(
            main_frame, mode="indeterminate", bootstyle="info"
        )
        self.progress.grid(row=2, column=0, sticky=(E, W), pady=(10, 0))
        self.progress.grid_remove()  # Hide initially

    def _create_control_panel(self, parent: ttk.Frame) -> None:
        """Create the control panel with buttons and effect selector.

        Args:
            parent: The parent frame to add controls to.
        """
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=0, column=0, sticky=(E, W), pady=(0, 20))

        # Load button
        self.load_btn = ttk.Button(
            control_frame,
            text="Load Image",
            command=self._load_image,
            bootstyle="primary",
            width=15,
        )
        self.load_btn.grid(row=0, column=0, padx=5)

        # Effect selector
        ttk.Label(control_frame, text="Effect:").grid(row=0, column=1, padx=5)
        self.effect_var = ttk.StringVar(value="Sketch Effect")
        self.effect_combo = ttk.Combobox(
            control_frame,
            textvariable=self.effect_var,
            values=[
                "Grayscale",
                "Sketch Effect",
                "Contour Effect",
                "Tattoo Calc Effect",
            ],
            state="readonly",
            width=20,
        )
        self.effect_combo.grid(row=0, column=2, padx=5)

        # Apply button
        self.apply_btn = ttk.Button(
            control_frame,
            text="Apply Effect",
            command=self._apply_effect,
            bootstyle="success",
            width=15,
            state="disabled",
        )
        self.apply_btn.grid(row=0, column=3, padx=5)

        # Save button
        self.save_btn = ttk.Button(
            control_frame,
            text="Save Image",
            command=self._save_image,
            bootstyle="warning",
            width=15,
            state="disabled",
        )
        self.save_btn.grid(row=0, column=4, padx=5)

    def _create_image_display(self, parent: ttk.Frame) -> None:
        """Create the image display area.

        Args:
            parent: The parent frame to add display to.
        """
        display_frame = ttk.Labelframe(parent, text="Image Preview")
        display_frame.grid(row=1, column=0, sticky=(N, S, E, W), padx=10, pady=10)
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)

        self.image_label = ttk.Label(
            display_frame, text="No Image Loaded", anchor=CENTER, bootstyle="secondary"
        )
        self.image_label.grid(row=0, column=0, sticky=(N, S, E, W), padx=10, pady=10)

    def _load_image(self) -> None:
        """Open file dialog and load an image."""
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("All Files", "*.*"),
            ],
        )

        if not file_path:
            return

        try:
            # Validate file extension before loading
            ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise InvalidImageError(
                    f"Unsupported file format: {file_ext}\n"
                    f"Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
                )

            # Load image using OpenCV
            image = cv2.imread(file_path)

            if image is None:
                raise InvalidImageError(
                    "Could not read image file. File may be corrupted or unsupported format."
                )

            # Validate image
            from .image_processor import validate_image

            validate_image(image)

            self.original_image = image
            self.current_file_path = Path(file_path)
            self.processed_image = None

            # Display the image
            self._display_image(image)

            # Enable apply button
            self.apply_btn.config(state="normal")
            self.save_btn.config(state="disabled")

        except ImageTooLargeError as e:
            messagebox.showerror(
                "Image Too Large",
                f"{str(e)}\n\nPlease use an image editing tool to resize it first.",
            )
        except InvalidImageError as e:
            messagebox.showerror("Invalid Image", str(e))
        except Exception as e:
            messagebox.showerror("Error Loading Image", f"Unexpected error: {str(e)}")

    def _apply_effect(self) -> None:
        """Apply the selected effect to the loaded image in a background thread."""
        if self.original_image is None or self.processing:
            return

        effect = self.effect_var.get()

        # Disable buttons during processing
        self._set_processing(True)

        # Run processing in background thread
        thread = threading.Thread(target=self._process_image, args=(effect,), daemon=True)
        thread.start()

    def _process_image(self, effect: str) -> None:
        """Process image with selected effect (runs in background thread).

        Args:
            effect: The name of the effect to apply.
        """
        try:
            # Ensure original_image is not None
            if self.original_image is None:
                raise ValueError("No image loaded")

            # Apply the selected effect
            if effect == "Grayscale":
                result = convert_to_grayscale(self.original_image)
            elif effect == "Sketch Effect":
                result = apply_sketch_effect(self.original_image)
            elif effect == "Contour Effect":
                result = apply_contour_effect(self.original_image)
            elif effect == "Tattoo Calc Effect":
                result = apply_tattoo_calc_effect(self.original_image)
            else:
                raise ValueError(f"Unknown effect: {effect}")

            self.processed_image = result

            # Update UI in main thread
            self.root.after(0, self._on_processing_complete, result, None)

        except Exception as e:
            # Report error in main thread
            self.root.after(0, self._on_processing_complete, None, e)

    def _on_processing_complete(
        self, result: np.ndarray | None, error: Exception | None
    ) -> None:
        """Handle completion of image processing.

        Args:
            result: The processed image, or None if there was an error.
            error: The exception if processing failed, or None if successful.
        """
        self._set_processing(False)

        if error:
            messagebox.showerror(
                "Processing Error", f"Failed to apply effect: {str(error)}"
            )
            return

        if result is not None:
            self._display_image(result)
            self.save_btn.config(state="normal")

    def _save_image(self) -> None:
        """Save the processed image to a file."""
        if self.processed_image is None:
            return

        # Suggest filename based on original
        initial_file = "processed_image.png"
        if self.current_file_path:
            initial_file = (
                f"{self.current_file_path.stem}_processed{self.current_file_path.suffix}"
            )

        save_path = filedialog.asksaveasfilename(
            title="Save Processed Image",
            initialfile=initial_file,
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg"),
                ("BMP Image", "*.bmp"),
                ("All Files", "*.*"),
            ],
        )

        if not save_path:
            return

        try:
            success = cv2.imwrite(save_path, self.processed_image)
            if not success:
                raise OSError("Failed to write image file")

            messagebox.showinfo("Success", f"Image saved to:\n{save_path}")

        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save image: {str(e)}")

    def _display_image(self, image: np.ndarray) -> None:
        """Convert OpenCV image to PhotoImage and display it.

        Args:
            image: The image to display (OpenCV format).
        """
        # Convert BGR to RGB for display
        if len(image.shape) == 2:  # Grayscale
            display_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:  # Color
            display_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert to PIL Image
        pil_image = Image.fromarray(display_image)

        # Resize to fit display area (max 800x500)
        pil_image.thumbnail((800, 500), Image.Resampling.LANCZOS)

        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(pil_image)

        # Update label
        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo  # type: ignore[attr-defined]  # Keep reference to prevent GC

    def _set_processing(self, processing: bool) -> None:
        """Enable or disable UI elements during processing.

        Args:
            processing: True if processing is starting, False if ending.
        """
        self.processing = processing

        if processing:
            self.load_btn.config(state="disabled")
            self.apply_btn.config(state="disabled")
            self.save_btn.config(state="disabled")
            self.progress.grid()
            self.progress.start()
        else:
            self.load_btn.config(state="normal")
            self.apply_btn.config(state="normal" if self.original_image else "disabled")
            self.save_btn.config(state="normal" if self.processed_image else "disabled")
            self.progress.stop()
            self.progress.grid_remove()


def main() -> None:
    """Main entry point for the Tracify application."""
    root = ttk.Window(themename="darkly")
    TracifyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
