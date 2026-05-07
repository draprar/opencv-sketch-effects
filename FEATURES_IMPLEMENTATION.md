# 🚀 Feature Implementation Guide - Tracify

Ten dokument zawiera szczegółowe instrukcje implementacji wszystkich zaplanowanych feature'ów.

## ✅ Implemented Features

### 1. **Configuration System** (`config.py`)
**Status**: ✅ IMPLEMENTED
**File**: `src/tracify/config.py`

Kompletny system konfiguracji z:
- TOML-based config file (~/.tracify/config.toml)
- Effect parameters (blur_kernel, thresholds, etc.)
- Export settings (JPEG quality, PNG compression)
- Auto-save/load

**Usage**:
```python
from tracify.config import Config

config = Config()
blur = config.get_effect_params("sketch").get("blur_kernel", 21)
config.set_effect_params("sketch", {"blur_kernel": 25})
config.save()
```

---

## 📝 Ready-to-Implement Features

### 2. **Configurable Effect Parameters (GUI Sliders)**

**Implementation Steps**:

1. **Update `image_processor.py`** - dodaj parametry do funkcji:
```python
def apply_sketch_effect(image: np.ndarray, blur_kernel: int = 21, scale: int = 256) -> np.ndarray:
    # Validate blur_kernel is odd
    if blur_kernel % 2 == 0:
        blur_kernel += 1
    blurred_image = cv2.GaussianBlur(inverted_image, (blur_kernel, blur_kernel), 0)
    sketch_image = cv2.divide(gray_image, denominator, scale=scale)
    return sketch_image

def apply_contour_effect(image: np.ndarray, threshold1: int = 50, threshold2: int = 150) -> np.ndarray:
    edges = cv2.Canny(gray_image, threshold1, threshold2)
    return edges
```

2. **Update `main.py`** - dodaj parameter panel:
```python
def _create_parameters_panel(self, parent):
    """Create parameters panel for effect customization."""
    params_frame = ttk.Labelframe(parent, text="Effect Parameters")
    params_frame.grid(row=3, column=0, sticky=(E, W), pady=10)

    # Sketch effect parameters
    self.blur_kernel_var = ttk.IntVar(value=21)
    ttk.Label(params_frame, text="Blur Strength:").grid(row=0, column=0)
    ttk.Scale(
        params_frame,
        from_=1,
        to=51,
        variable=self.blur_kernel_var,
        command=self._on_param_change,
    ).grid(row=0, column=1)

    # Contour effect parameters
    self.threshold1_var = ttk.IntVar(value=50)
    self.threshold2_var = ttk.IntVar(value=150)
    # ... similar sliders

def _apply_effect_with_params(self):
    """Apply effect with current parameters."""
    effect = self.effect_var.get()
    if effect == "Sketch Effect":
        blur = self.blur_kernel_var.get()
        if blur % 2 == 0:  # Ensure odd
            blur += 1
        result = apply_sketch_effect(self.original_image, blur_kernel=blur)
    elif effect == "Contour Effect":
        result = apply_contour_effect(
            self.original_image,
            threshold1=self.threshold1_var.get(),
            threshold2=self.threshold2_var.get(),
        )
```

**Estimated Time**: 2-3 hours
**Priority**: HIGH
**Test**: Manual GUI testing + unit tests with different params

---

### 3. **Undo/Redo Stack**

**Implementation**:

```python
# In main.py TracifyApp.__init__:
self.history: list[np.ndarray] = []
self.history_index: int = -1
self.max_history: int = 10  # Limit memory usage

def _add_to_history(self, image: np.ndarray) -> None:
    """Add image to history stack."""
    # Remove any redo history
    self.history = self.history[: self.history_index + 1]

    # Add new state
    self.history.append(image.copy())

    # Limit history size
    if len(self.history) > self.max_history:
        self.history.pop(0)
    else:
        self.history_index += 1

    self._update_undo_redo_buttons()

def undo(self) -> None:
    """Undo last operation."""
    if self.history_index > 0:
        self.history_index -= 1
        self.processed_image = self.history[self.history_index].copy()
        self._display_image(self.processed_image)
        self._update_undo_redo_buttons()

def redo(self) -> None:
    """Redo undone operation."""
    if self.history_index < len(self.history) - 1:
        self.history_index += 1
        self.processed_image = self.history[self.history_index].copy()
        self._display_image(self.processed_image)
        self._update_undo_redo_buttons()

def _update_undo_redo_buttons(self) -> None:
    """Update undo/redo button states."""
    self.undo_btn.config(state="normal" if self.history_index > 0 else "disabled")
    self.redo_btn.config(
        state="normal" if self.history_index < len(self.history) - 1 else "disabled"
    )

# Add buttons to control panel:
self.undo_btn = ttk.Button(control_frame, text="Undo", command=self.undo, state="disabled")
self.redo_btn = ttk.Button(control_frame, text="Redo", command=self.redo, state="disabled")
```

**Estimated Time**: 1-2 hours
**Priority**: HIGH
**Memory**: ~480MB for 10 images @ 4096x4096 (acceptable)

---

### 4. **Export Options Dialog**

**Implementation**:

```python
def _save_image_with_options(self) -> None:
    """Save image with export options dialog."""
    if self.processed_image is None:
        return

    # Create dialog
    dialog = ttk.Toplevel(self.root)
    dialog.title("Export Options")
    dialog.geometry("400x300")

    # Format selection
    format_var = ttk.StringVar(value="png")
    ttk.Label(dialog, text="Format:").pack()
    ttk.Radiobutton(dialog, text="PNG", variable=format_var, value="png").pack()
    ttk.Radiobutton(dialog, text="JPEG", variable=format_var, value="jpg").pack()

    # Quality slider (for JPEG)
    quality_var = ttk.IntVar(value=95)
    ttk.Label(dialog, text="JPEG Quality (1-100):").pack()
    ttk.Scale(dialog, from_=1, to=100, variable=quality_var).pack()

    # Resize option
    resize_var = ttk.BooleanVar(value=False)
    ttk.Checkbutton(dialog, text="Resize before export", variable=resize_var).pack()

    width_var = ttk.IntVar(value=1920)
    height_var = ttk.IntVar(value=1080)
    ttk.Label(dialog, text="Width:").pack()
    ttk.Entry(dialog, textvariable=width_var).pack()
    ttk.Label(dialog, text="Height:").pack()
    ttk.Entry(dialog, textvariable=height_var).pack()

    def do_export():
        save_path = filedialog.asksaveasfilename(
            defaultextension=f".{format_var.get()}",
            filetypes=[(f"{format_var.get().upper()}", f"*.{format_var.get()}")],
        )
        if not save_path:
            return

        image_to_save = self.processed_image.copy()

        # Resize if requested
        if resize_var.get():
            image_to_save = cv2.resize(
                image_to_save, (width_var.get(), height_var.get()), interpolation=cv2.INTER_LANCZOS4
            )

        # Save with options
        if format_var.get() == "jpg":
            cv2.imwrite(save_path, image_to_save, [cv2.IMWRITE_JPEG_QUALITY, quality_var.get()])
        else:  # PNG
            cv2.imwrite(save_path, image_to_save, [cv2.IMWRITE_PNG_COMPRESSION, 6])

        messagebox.showinfo("Success", f"Exported to {save_path}")
        dialog.destroy()

    ttk.Button(dialog, text="Export", command=do_export).pack()
```

**Estimated Time**: 2 hours
**Priority**: MEDIUM

---

### 5. **Batch Processing**

**Implementation**:

```python
def _batch_process(self) -> None:
    """Process multiple images in a folder."""
    # Select input folder
    input_folder = filedialog.askdirectory(title="Select folder with images")
    if not input_folder:
        return

    # Select output folder
    output_folder = filedialog.askdirectory(title="Select output folder")
    if not output_folder:
        return

    # Get effect to apply
    effect = self.effect_var.get()

    # Find all images
    input_path = Path(input_folder)
    image_files = []
    for ext in ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tiff"]:
        image_files.extend(input_path.glob(ext))

    if not image_files:
        messagebox.showwarning("No Images", "No images found in selected folder")
        return

    # Create progress dialog
    progress_dialog = ttk.Toplevel(self.root)
    progress_dialog.title("Batch Processing")
    progress_label = ttk.Label(progress_dialog, text="Processing...")
    progress_label.pack(padx=20, pady=10)
    progress_bar = ttk.Progressbar(progress_dialog, maximum=len(image_files), mode="determinate")
    progress_bar.pack(padx=20, pady=10, fill="x")

    def process_batch():
        for i, img_file in enumerate(image_files):
            try:
                # Load image
                image = cv2.imread(str(img_file))
                if image is None:
                    continue

                # Apply effect
                if effect == "Grayscale":
                    result = convert_to_grayscale(image)
                elif effect == "Sketch Effect":
                    result = apply_sketch_effect(image)
                elif effect == "Contour Effect":
                    result = apply_contour_effect(image)
                elif effect == "Tattoo Calc Effect":
                    result = apply_tattoo_calc_effect(image)

                # Save result
                output_path = Path(output_folder) / f"{img_file.stem}_processed{img_file.suffix}"
                cv2.imwrite(str(output_path), result)

                # Update progress
                progress_bar["value"] = i + 1
                progress_label["text"] = f"Processing {i+1}/{len(image_files)}: {img_file.name}"
                self.root.update()

            except Exception as e:
                print(f"Error processing {img_file}: {e}")

        progress_dialog.destroy()
        messagebox.showinfo("Complete", f"Processed {len(image_files)} images")

    # Run in thread
    thread = threading.Thread(target=process_batch, daemon=True)
    thread.start()

# Add batch button to control panel:
self.batch_btn = ttk.Button(control_frame, text="Batch Process", command=self._batch_process)
```

**Estimated Time**: 3 hours
**Priority**: HIGH

---

### 6. **Keyboard Shortcuts**

**Implementation**:

```python
# In TracifyApp.__init__:
def _setup_keyboard_shortcuts(self) -> None:
    """Setup keyboard shortcuts."""
    self.root.bind("<Control-o>", lambda e: self._load_image())
    self.root.bind("<Control-s>", lambda e: self._save_image())
    self.root.bind("<Control-z>", lambda e: self.undo())
    self.root.bind("<Control-y>", lambda e: self.redo())
    self.root.bind("<Control-Shift-Z>", lambda e: self.redo())  # Alternative redo
    self.root.bind("<Control-q>", lambda e: self.root.quit())
    self.root.bind("<Control-b>", lambda e: self._batch_process())

    # Show shortcuts in menu or tooltip
    self.shortcuts_info = """
    Keyboard Shortcuts:
    Ctrl+O - Load Image
    Ctrl+S - Save Image
    Ctrl+Z - Undo
    Ctrl+Y - Redo
    Ctrl+B - Batch Process
    Ctrl+Q - Quit
    """
```

**Estimated Time**: 30 minutes
**Priority**: MEDIUM

---

### 7. **Drag & Drop Support**

**Implementation**:

```python
# In TracifyApp.__init__:
def _setup_drag_drop(self) -> None:
    """Setup drag and drop for image files."""
    try:
        from tkinterdnd2 import TkinterDnD, DND_FILES

        # Note: Requires tkinterdnd2 package
        # Add to pyproject.toml: "tkinterdnd2>=0.3.0"

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self._on_drop)

    except ImportError:
        # tkinterdnd2 not available, skip drag&drop
        pass

def _on_drop(self, event) -> None:
    """Handle dropped files."""
    files = self.root.tk.splitlist(event.data)
    if files:
        file_path = files[0]
        # Validate it's an image
        if Path(file_path).suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}:
            self._load_image_from_path(file_path)

def _load_image_from_path(self, file_path: str) -> None:
    """Load image from given path."""
    try:
        allowed_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in allowed_extensions:
            raise InvalidImageError(f"Unsupported file format: {file_ext}")

        image = cv2.imread(file_path)
        if image is None:
            raise InvalidImageError("Could not read image file")

        from .image_processor import validate_image
        validate_image(image)

        self.original_image = image
        self.current_file_path = Path(file_path)
        self.processed_image = None

        self._display_image(image)
        self.apply_btn.config(state="normal")
        self.save_btn.config(state="disabled")

    except (ImageTooLargeError, InvalidImageError) as e:
        messagebox.showerror("Error", str(e))
```

**Estimated Time**: 1 hour (if using tkinterdnd2)
**Priority**: LOW (nice-to-have)
**Note**: Requires additional dependency

---

### 8. **Before/After Comparison View**

**Implementation**:

```python
def _show_comparison(self) -> None:
    """Show before/after comparison in split view."""
    if self.original_image is None or self.processed_image is None:
        messagebox.showwarning("No Images", "Load and process an image first")
        return

    # Create comparison window
    comp_window = ttk.Toplevel(self.root)
    comp_window.title("Before / After Comparison")
    comp_window.geometry("1200x600")

    # Create frames for before and after
    before_frame = ttk.Labelframe(comp_window, text="Before (Original)")
    before_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    after_frame = ttk.Labelframe(comp_window, text="After (Processed)")
    after_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

    # Display images
    before_label = ttk.Label(before_frame)
    before_label.pack(fill="both", expand=True)

    after_label = ttk.Label(after_frame)
    after_label.pack(fill="both", expand=True)

    # Convert and display before
    before_rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
    before_pil = Image.fromarray(before_rgb)
    before_pil.thumbnail((550, 550), Image.Resampling.LANCZOS)
    before_photo = ImageTk.PhotoImage(before_pil)
    before_label.configure(image=before_photo)
    before_label.image = before_photo

    # Convert and display after
    if len(self.processed_image.shape) == 2:
        after_rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_GRAY2RGB)
    else:
        after_rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
    after_pil = Image.fromarray(after_rgb)
    after_pil.thumbnail((550, 550), Image.Resampling.LANCZOS)
    after_photo = ImageTk.PhotoImage(after_pil)
    after_label.configure(image=after_photo)
    after_label.image = after_photo

# Add comparison button:
self.compare_btn = ttk.Button(control_frame, text="Compare", command=self._show_comparison, state="disabled")
```

**Estimated Time**: 1.5 hours
**Priority**: MEDIUM

---

### 9. **Logging System**

**Implementation**:

```python
# Create src/tracify/logger.py:
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "tracify") -> logging.Logger:
    """Setup application logger with file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create logs directory
    log_dir = Path.home() / ".tracify" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "tracify.log"

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# In main.py:
from .logger import setup_logger

logger = setup_logger()

# Use throughout code:
logger.info(f"Loading image: {file_path}")
logger.error(f"Failed to process image: {e}")
logger.warning(f"Image size exceeds recommended: {width}x{height}")
```

**Estimated Time**: 1 hour
**Priority**: HIGH

---

### 10. **Performance & Memory Profiling Tests**

**Implementation**:

```python
# tests/test_performance.py
import time
import numpy as np
import pytest
from tracify.image_processor import apply_sketch_effect, apply_contour_effect

@pytest.mark.slow
def test_sketch_effect_performance():
    """Test sketch effect performance on large image."""
    image = np.ones((4096, 4096, 3), dtype=np.uint8) * 128

    start = time.perf_counter()
    result = apply_sketch_effect(image)
    duration = time.perf_counter() - start

    assert result.shape == (4096, 4096)
    assert duration < 5.0, f"Processing took {duration:.2f}s, expected <5s"

@pytest.mark.slow
def test_batch_performance():
    """Test batch processing performance."""
    images = [np.ones((1920, 1080, 3), dtype=np.uint8) * (i * 10) for i in range(10)]

    start = time.perf_counter()
    for img in images:
        apply_sketch_effect(img)
    duration = time.perf_counter() - start

    assert duration < 10.0, f"Batch took {duration:.2f}s for 10 images"

# Add to pyproject.toml:
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
]
```

**Estimated Time**: 2 hours
**Priority**: MEDIUM

---

## 📦 Dependencies to Add

Add to `pyproject.toml`:

```toml
dependencies = [
    # ... existing ...
    "tomli>=2.0.1;python_version<'3.11'",  # For config
    "tomli-w>=1.0.0",  # For writing TOML
]

[dependency-groups]
dev = [
    # ... existing ...
    "tkinterdnd2>=0.3.0",  # Optional: for drag&drop
    "memory-profiler>=0.61.0",  # For memory tests
]
```

---

## 🎯 Implementation Priority Order

**Week 1 (High Priority)**:
1. ✅ Configuration System (DONE)
2. Configurable Effect Parameters with GUI sliders
3. Undo/Redo Stack
4. Logging System
5. Keyboard Shortcuts

**Week 2 (Medium Priority)**:
6. Batch Processing
7. Export Options Dialog
8. Before/After Comparison
9. Performance Tests

**Week 3 (Low Priority/Polish)**:
10. Drag & Drop (optional dependency)
11. Memory Profiling Tests
12. Documentation updates

---

## ✅ Testing Strategy

For each feature:
1. Unit tests in `tests/test_*.py`
2. Integration tests for GUI features
3. Manual testing checklist
4. Performance benchmarks where applicable

---

## 📝 Notes

- All features maintain backward compatibility
- Config file is optional (defaults work without it)
- GUI remains responsive during long operations (threading)
- Memory-conscious (history stack limited to 10 items)
- Cross-platform compatible (Windows/macOS/Linux)

---

**Status**: Ready for implementation
**Last Updated**: 2026-05-07
**Maintainer**: Development Team
