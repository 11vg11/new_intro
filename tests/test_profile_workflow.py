import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.fetch_contributions import parse_days
from scripts.run_profile import build_plan
from scripts.config import get_output_paths


class FetchContributionsTests(unittest.TestCase):
    def test_parse_days_uses_data_level_fallback(self) -> None:
        html = (
            "<html><body>"
            "<td data-date='2024-01-01' data-level='3' aria-label='3 contributions'></td>"
            "<td data-date='2024-01-02' data-level='1'></td>"
            "</body></html>"
        )

        days = parse_days(html)

        self.assertEqual(days["2024-01-01"], 3)
        self.assertEqual(days["2024-01-02"], 1)


class RunnerTests(unittest.TestCase):
    def test_build_plan_uses_photo_from_photos_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            scripts_dir = root / "scripts"
            photos_dir = root / "photos"
            scripts_dir.mkdir(parents=True)
            photos_dir.mkdir(parents=True)
            (photos_dir / "avatar.jpg").write_bytes(b"fake-image")

            steps = build_plan(
                SimpleNamespace(photo=None, skip_heatmap=True, skip_info=True, skip_ascii=False),
                root_dir=root,
                scripts_dir=scripts_dir,
                photos_dir=photos_dir,
                prepared_photo_exists=False,
            )

            self.assertTrue(any(label == "prepare portrait photo" for label, _ in steps))


class ConfigTests(unittest.TestCase):
    def test_output_paths_are_grouped_in_output_directory(self) -> None:
        root = Path("/tmp/profile-root")
        output_paths = get_output_paths(root)

        self.assertEqual(output_paths["heatmap"], root / "output" / "contrib-heatmap.svg")
        self.assertEqual(output_paths["ascii"], root / "output" / "avi-ascii.svg")
        self.assertEqual(output_paths["info_card"], root / "output" / "info-card.svg")


if __name__ == "__main__":
    unittest.main()
