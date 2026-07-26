from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
DATA_DIR = ROOT / "data"
PHOTOS_DIR = ROOT / "photos"
OUTPUT_DIR = ROOT / "output"

DEFAULT_GITHUB_USER = "avivashishta"
DEFAULT_HANDLE = "avivashishta"
DEFAULT_PHOTO_CANDIDATES = [
    "avatar.jpg",
    "avatar.jpeg",
    "photo.jpg",
    "photo.jpeg",
    "profile.jpg",
    "profile.jpeg",
    "portrait.jpg",
    "portrait.jpeg",
    "image.jpg",
    "image.jpeg",
]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def get_output_paths(root: Optional[Path] = None) -> dict[str, Path]:
    base = (root or ROOT).resolve()
    output_dir = base / "output"
    return {
        "dir": output_dir,
        "heatmap": output_dir / "contrib-heatmap.svg",
        "ascii": output_dir / "avi-ascii.svg",
        "info_card": output_dir / "info-card.svg",
        "prepared_photo": base / "source-prepped.png",
        "contributions": base / "data" / "contributions.json",
    }


def get_github_user() -> str:
    return os.environ.get("GITHUB_USER", DEFAULT_GITHUB_USER)


def get_info_card_rows() -> list[tuple[str, str, str, str]]:
    accent = "#58a6ff"
    green = "#3fb950"
    white = "#e6edf3"
    orange = "#ffa657"
    dim = "#8b949e"

    return [
        (accent, "Now", white, "Building developer tools & open-source libs"),
        (accent, "Prev", white, "Full-stack @ stealth startup · 2 yrs"),
        (accent, "Stack", green, "Python · TypeScript · Rust · Go"),
        (accent, "Editor", white, "Neovim (btw)"),
        (accent, "OS", white, "Arch Linux / macOS"),
        (accent, "Focus", orange, "DX · performance · clean APIs"),
        (accent, "Learning", white, "Zig · WebGPU · distributed systems"),
        (accent, "Contact", accent, "avivashishta.com · hi@avivashishta.com"),
    ]
