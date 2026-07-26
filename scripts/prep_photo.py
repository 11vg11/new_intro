#!/usr/bin/env python3
"""
prep_photo.py — Prepare a portrait photo for ASCII conversion.

Steps:
  1. Remove background with rembg (isolates the subject).
  2. Boost local contrast with OpenCV CLAHE so face highlights/shadows
     map cleanly to the ASCII density ramp.
  3. Composite the result on pure white so the background → spaces.

Usage:
    python scripts/prep_photo.py <input-photo.jpg>

Output:
    source-prepped.png  (grayscale, 512 px wide, white background)
"""

import hashlib
import sys
from pathlib import Path

try:
    from .config import OUTPUT_DIR
except ImportError:  # pragma: no cover - direct script execution
    from config import OUTPUT_DIR

try:
    from PIL import Image
    import numpy as np
    import cv2
    from rembg import remove
except ImportError as e:
    print(f"[prep_photo] Missing dependency: {e}")
    print("Run:  pip install pillow numpy opencv-python rembg")
    sys.exit(1)

# Configuration
OUTPUT_PATH = Path(__file__).parent.parent / "source-prepped.png"
TARGET_WIDTH = 512
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CLAHE_CLIP_LIMIT = 3.0
CLAHE_TILE_GRID = (8, 8)


def remove_background(img_bytes: bytes) -> Image.Image:
    """Use rembg to strip background; return RGBA PIL image."""
    print("[prep_photo] Removing background with rembg …")
    result_bytes = remove(img_bytes)
    return Image.open(__import__("io").BytesIO(result_bytes)).convert("RGBA")


def apply_clahe(gray_np: np.ndarray) -> np.ndarray:
    """Apply CLAHE to a single-channel uint8 array."""
    clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=CLAHE_TILE_GRID)
    return clahe.apply(gray_np)


def composite_on_white(rgba: Image.Image) -> Image.Image:
    """Flatten RGBA onto a white background."""
    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    white.paste(rgba, mask=rgba.split()[3])   # use alpha channel as mask
    return white.convert("RGB")


def process(input_path: str) -> None:
    src = Path(input_path)
    if not src.exists():
        print(f"[prep_photo] ERROR: file not found — {src}")
        sys.exit(1)

    print(f"[prep_photo] Reading {src} …")
    img_bytes = src.read_bytes()

    if OUTPUT_PATH.exists():
        current_hash = hashlib.sha256(img_bytes).hexdigest()
        existing_hash_path = OUTPUT_PATH.with_suffix(".sha256")
        if existing_hash_path.exists() and existing_hash_path.read_text(encoding="utf-8") == current_hash:
            print(f"[prep_photo] ✓ Existing prepared image is up to date — {OUTPUT_PATH}")
            return

    rgba = remove_background(img_bytes)
    rgb = composite_on_white(rgba)
    gray_np = cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2GRAY)

    print("[prep_photo] Applying CLAHE contrast enhancement …")
    enhanced = apply_clahe(gray_np)

    h, w = enhanced.shape
    new_h = int(TARGET_WIDTH * h / w)
    resized = cv2.resize(enhanced, (TARGET_WIDTH, new_h), interpolation=cv2.INTER_LANCZOS4)

    result = Image.fromarray(resized)
    result.save(OUTPUT_PATH)
    OUTPUT_PATH.with_suffix(".sha256").write_text(hashlib.sha256(img_bytes).hexdigest(), encoding="utf-8")
    print(f"[prep_photo] ✓ Saved → {OUTPUT_PATH}  ({TARGET_WIDTH}×{new_h})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {Path(__file__).name} <input-photo.jpg>")
        sys.exit(1)
    process(sys.argv[1])
