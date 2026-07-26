#!/usr/bin/env python3
"""Run the profile-generation workflow with a single command."""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

try:
    from .config import DEFAULT_PHOTO_CANDIDATES, IMAGE_EXTENSIONS, PHOTOS_DIR, SCRIPTS_DIR, ROOT
except ImportError:  # pragma: no cover - direct script execution
    from config import DEFAULT_PHOTO_CANDIDATES, IMAGE_EXTENSIONS, PHOTOS_DIR, SCRIPTS_DIR, ROOT


def resolve_python() -> str:
    """Choose a Python interpreter that can run the portrait pipeline."""
    if os.environ.get("PYTHON"):
        return os.environ["PYTHON"]

    candidates: List[str] = []
    for candidate in [
        "/usr/bin/python3",
        "/usr/bin/python",
        shutil.which("python3"),
        sys.executable,
    ]:
        if candidate and candidate not in candidates:
            candidates.append(candidate)

    for candidate in [
        ROOT / ".venv" / "bin" / "python",
        ROOT / ".venv" / "bin" / "python3",
        ROOT / ".venv_real" / "bin" / "python",
        ROOT / ".venv_real" / "bin" / "python3",
    ]:
        if candidate.exists() and str(candidate) not in candidates:
            candidates.append(str(candidate))

    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)

        try:
            subprocess.run(
                [candidate, "-c", "import PIL, numpy, cv2; from rembg import remove"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            continue

        return candidate

    return candidates[0] if candidates else sys.executable


def ensure_optional_portrait_dependencies() -> None:
    """Fail fast if the portrait pipeline dependencies are missing."""
    try:
        import PIL  # noqa: F401
        import numpy  # noqa: F401
        import cv2  # noqa: F401
        from rembg import remove  # noqa: F401
    except ImportError as exc:
        print("[run_profile] Optional portrait dependencies are missing:")
        print(f"  - {exc}")
        print("  Install them with:")
        print("    python3 -m pip install pillow numpy opencv-python rembg")
        raise


def find_photo(args, *, photos_dir: Optional[Path] = None) -> Optional[Path]:
    """Locate a portrait image from an explicit path or the photos directory."""
    photos_dir = photos_dir or PHOTOS_DIR

    if args.photo:
        candidate = Path(args.photo).expanduser()
        if candidate.exists():
            return candidate
        print(f"[run_profile] Photo not found: {candidate}")
        return None

    if not photos_dir.exists():
        return None

    explicit_names = [Path(name) for name in DEFAULT_PHOTO_CANDIDATES]
    for candidate in explicit_names:
        path = photos_dir / candidate
        if path.exists() and path.is_file():
            return path

    candidates = sorted(
        p for p in photos_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )
    return candidates[0] if candidates else None


def build_plan(args, *, prepared_photo_exists: bool = False, root_dir: Optional[Path] = None, scripts_dir: Optional[Path] = None, photos_dir: Optional[Path] = None) -> List[Tuple[str, List[str]]]:
    """Build the ordered list of steps to run for the requested workflow."""
    root_dir = root_dir or ROOT
    scripts_dir = scripts_dir or SCRIPTS_DIR
    photos_dir = photos_dir or PHOTOS_DIR
    python = resolve_python()
    steps: List[Tuple[str, List[str]]] = []

    if not args.skip_heatmap:
        steps.append(("fetch contribution data", [python, str(scripts_dir / "fetch_contributions.py")]))
        steps.append(("render heatmap", [python, str(scripts_dir / "render_heatmap_svg.py")]))

    if not args.skip_info:
        steps.append(("generate info card", [python, str(scripts_dir / "make_info_card.py")]))

    if not args.skip_ascii:
        photo = find_photo(args, photos_dir=photos_dir)
        if photo is not None:
            steps.append(("prepare portrait photo", [python, str(scripts_dir / "prep_photo.py"), str(photo)]))
            steps.append(("generate ASCII portrait", [python, str(scripts_dir / "make_ascii_svg.py")]))
        elif prepared_photo_exists:
            steps.append(("generate ASCII portrait", [python, str(scripts_dir / "make_ascii_svg.py")]))
        else:
            print("[run_profile] No portrait image found. Add one to the photos/ folder or pass --photo path/to/photo.jpg.")

    return steps


def run_steps(steps: Sequence[Tuple[str, List[str]]], *, username: Optional[str], root_dir: Optional[Path] = None) -> int:
    """Execute the selected steps in order."""
    env = os.environ.copy()
    if username:
        env["GITHUB_USER"] = username

    for label, command in steps:
        print(f"[{label}]")
        completed = subprocess.run(command, cwd=root_dir or ROOT, env=env, check=False)
        if completed.returncode != 0:
            print(f"[run_profile] Failed: {label}")
            return completed.returncode

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the GitHub profile art assets")
    parser.add_argument("--username", help="GitHub username to scrape (defaults to GITHUB_USER or the built-in value)")
    parser.add_argument("--photo", help="Path to a portrait image to prepare for ASCII generation")
    parser.add_argument("--skip-heatmap", action="store_true", help="Skip contribution data and heatmap generation")
    parser.add_argument("--skip-info", action="store_true", help="Skip the info-card generation")
    parser.add_argument("--skip-ascii", action="store_true", help="Skip the ASCII portrait generation")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    prepared_photo_exists = (ROOT / "source-prepped.png").exists()
    steps = build_plan(args, prepared_photo_exists=prepared_photo_exists)

    if not steps:
        print("[run_profile] Nothing to run. Use the default workflow or pass --skip-* flags to select a subset.")
        return 0

    print(f"[run_profile] Python: {resolve_python()}")
    return run_steps(steps, username=args.username)


if __name__ == "__main__":
    raise SystemExit(main())
