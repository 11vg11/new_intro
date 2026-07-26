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

import sys
import os
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
    import cv2
    from rembg import remove
except ImportError as e:
    print(f"[prep_photo] Missing dependency: {e}")
    print("Run:  pip install pillow numpy opencv-python rembg")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
OUTPUT_PATH = Path(__file__).parent.parent / "source-prepped.png"
TARGET_WIDTH = 512          # resize to this width before ASCII conversion
CLAHE_CLIP_LIMIT = 3.0      # aggressiveness of local contrast boost
CLAHE_TILE_GRID = (8, 8)    # CLAHE grid size


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

    # Step 1 — Background removal
    rgba = remove_background(img_bytes)

    # Step 2 — Composite on white, then to grayscale NumPy array
    rgb = composite_on_white(rgba)
    gray_np = cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2GRAY)

    # Step 3 — CLAHE contrast boost
    print("[prep_photo] Applying CLAHE contrast enhancement …")
    enhanced = apply_clahe(gray_np)

    # Step 4 — Resize to target width, preserve aspect ratio
    h, w = enhanced.shape
    new_h = int(TARGET_WIDTH * h / w)
    resized = cv2.resize(enhanced, (TARGET_WIDTH, new_h), interpolation=cv2.INTER_LANCZOS4)

    # Step 5 — Save
    result = Image.fromarray(resized)
    result.save(OUTPUT_PATH)
    print(f"[prep_photo] ✓ Saved → {OUTPUT_PATH}  ({TARGET_WIDTH}×{new_h})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {Path(__file__).name} <input-photo.jpg>")
        sys.exit(1)
    process(sys.argv[1])
