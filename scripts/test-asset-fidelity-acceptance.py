#!/usr/bin/env python3
"""Behavioral acceptance tests for Design Arc's selected-asset fidelity gate."""

from __future__ import annotations

from collections.abc import Callable
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib


REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = REPO_ROOT / "scripts/validate-asset-fidelity.py"


def png_bytes(width: int, height: int, rgb: tuple[int, int, int]) -> bytes:
    """Return a deterministic opaque RGB PNG without external dependencies."""

    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    rows = b"".join(b"\x00" + bytes(rgb) * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows, 9))
        + chunk(b"IEND", b"")
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def app_html(asset_id: str, asset_path: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Design Arc asset proof</title>
  <style>
    body {{ margin: 0; background: #11130f; color: #f3ead8; font: 18px sans-serif; }}
    main {{ padding: 24px; }}
    [data-design-arc-asset] {{ display: block; width: 320px; height: 160px; object-fit: fill; }}
    @media (max-width: 600px) {{
      [data-design-arc-asset] {{ width: 240px; height: 120px; }}
    }}
  </style>
</head>
<body>
  <nav aria-label="Primary"><a href="#review">Review</a></nav>
  <main id="review">
    <img data-design-arc-asset="{asset_id}" src="{asset_path}" alt="Evidence-backed onboarding journey">
    <label for="email">Email</label>
    <input id="email" name="email" type="email">
    <label><input id="consent" type="checkbox"> Consent</label>
    <button id="continue" type="button">Continue</button>
    <output id="status" aria-label="Ready">Ready</output>
  </main>
</body>
</html>
"""


def manifest_for(root: Path, selected: str = "platform") -> dict[str, object]:
    assets = root / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    platform_path = assets / "platform-journey.png"
    stitch_path = assets / "stitch-journey.png"
    platform_path.write_bytes(png_bytes(64, 32, (243, 234, 216)))
    stitch_path.write_bytes(png_bytes(64, 32, (255, 90, 60)))

    selected_id = f"{selected}.journey"
    selected_path = f"assets/{selected}-journey.png"
    (root / "index.html").write_text(app_html(selected_id, selected_path), encoding="utf-8")

    def asset(set_name: str, path: Path) -> dict[str, object]:
        return {
            "id": f"{set_name}.journey",
            "path": f"assets/{set_name}-journey.png",
            "sha256": sha256(path),
            "media_type": "image/png",
            "required": True,
            "source_references": ["index.html"],
            "selector": f'[data-design-arc-asset="{set_name}.journey"]',
            "alt": "Evidence-backed onboarding journey",
            "render": {
                "desktop": {"width": 320, "height": 160, "tolerance": 1},
                "mobile": {"width": 240, "height": 120, "tolerance": 1},
            },
        }

    return {
        "schema": "design-arc.asset-fidelity/v1",
        "active_platform": {"name": "codex", "native_image_generation": True},
        "stitch_invoked": selected == "stitch",
        "selection": {
            "design": selected,
            "hybrid_approved": False,
            "asset_ids": [selected_id],
        },
        "asset_sets": {
            "platform": [asset("platform", platform_path)],
            "stitch": [asset("stitch", stitch_path)] if selected == "stitch" else [],
        },
        "implementation_sources": ["index.html"],
        "semantic_requirements": [
            {"kind": "navigation", "selector": "nav", "element": "nav", "name": "Primary"},
            {"kind": "label", "selector": 'label[for="email"]', "element": "label", "name": "Email"},
            {"kind": "control", "selector": "#email", "element": "input", "name": "Email", "focusable": True},
            {"kind": "control", "selector": "#continue", "element": "button", "name": "Continue", "focusable": True},
            {"kind": "state", "selector": "#consent", "element": "input", "name": "Consent", "focusable": True},
            {"kind": "status", "selector": "#status", "element": "output", "name": "Ready"},
        ],
        "viewports": {
            "desktop": {"width": 1280, "height": 720},
            "mobile": {"width": 390, "height": 844},
        },
    }


def write_manifest(root: Path, manifest: dict[str, object]) -> Path:
    path = root / "design-arc-assets.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def run_validator(
    root: Path,
    manifest: dict[str, object],
    *,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    manifest_path = write_manifest(root, manifest)
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(manifest_path)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=environment,
        timeout=45,
    )


class AssetFidelityAcceptanceTests(unittest.TestCase):
    def test_platform_selection_matches_exact_asset_on_desktop_and_mobile(self) -> None:
        """Removing browser rendering or either viewport proof must break this pass."""
        with tempfile.TemporaryDirectory(prefix="design-arc-platform-") as temp:
            root = Path(temp)
            result = run_validator(root, manifest_for(root, "platform"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: asset fidelity matches approved proposal at desktop and mobile viewports", result.stdout)

    def test_stitch_selection_uses_exported_stitch_asset_without_platform_substitute(self) -> None:
        """Accepting a platform substitute for a Stitch selection must break this pass."""
        with tempfile.TemporaryDirectory(prefix="design-arc-stitch-") as temp:
            root = Path(temp)
            result = run_validator(root, manifest_for(root, "stitch"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("selected stitch.journey rendered at desktop", result.stdout)
        self.assertIn("selected stitch.journey rendered at mobile", result.stdout)

    def test_explicit_hybrid_selection_renders_both_provenance_bound_assets(self) -> None:
        """Disallowing an explicitly approved hybrid or silently dropping either set must fail."""
        with tempfile.TemporaryDirectory(prefix="design-arc-hybrid-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "stitch")
            manifest["selection"] = {
                "design": "hybrid",
                "hybrid_approved": True,
                "asset_ids": ["platform.journey", "stitch.journey"],
            }
            html = (root / "index.html").read_text(encoding="utf-8")
            html = html.replace(
                '<img data-design-arc-asset="stitch.journey"',
                '<img data-design-arc-asset="platform.journey" src="assets/platform-journey.png" '
                'alt="Evidence-backed onboarding journey">\n'
                '    <img data-design-arc-asset="stitch.journey"',
            )
            (root / "index.html").write_text(html, encoding="utf-8")
            result = run_validator(root, manifest)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("selected platform.journey rendered at desktop", result.stdout)
        self.assertIn("selected stitch.journey rendered at mobile", result.stdout)

    def test_selection_and_provenance_violations_are_rejected(self) -> None:
        """Removing set binding or hybrid approval must make these manifests fail."""
        cases: list[tuple[str, Callable[[dict[str, object]], None], str]] = [
            (
                "platform-selects-stitch",
                lambda value: value["selection"].update(
                    {"design": "platform", "asset_ids": ["stitch.journey"]}
                ),
                "platform selection may use only platform assets",
            ),
            (
                "stitch-selects-platform",
                lambda value: value["selection"].update({"asset_ids": ["platform.journey"]}),
                "stitch selection may use only stitch assets",
            ),
            (
                "hybrid-without-approval",
                lambda value: value["selection"].update(
                    {"design": "hybrid", "hybrid_approved": False, "asset_ids": ["platform.journey", "stitch.journey"]}
                ),
                "hybrid selection requires explicit approval",
            ),
        ]
        for label, mutate, expected in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory(prefix=f"design-arc-{label}-") as temp:
                root = Path(temp)
                manifest = manifest_for(root, "stitch")
                mutate(manifest)
                result = run_validator(root, manifest)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(expected, result.stderr)

    def test_missing_unused_broken_and_substituted_selected_assets_are_rejected(self) -> None:
        """Weakening file, hash, or source checks must make at least one case pass incorrectly."""
        cases = ("missing", "unused", "substituted", "stitch-not-preserved")
        for label in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory(prefix=f"design-arc-{label}-") as temp:
                root = Path(temp)
                manifest = manifest_for(root, "platform")
                if label == "missing":
                    (root / "assets/platform-journey.png").unlink()
                    expected = "required selected asset is unavailable"
                elif label == "unused":
                    (root / "index.html").write_text(
                        app_html("platform.journey", "assets/not-selected.png"), encoding="utf-8"
                    )
                    expected = "selected asset is not referenced by implementation source"
                elif label == "substituted":
                    (root / "assets/platform-journey.png").write_bytes(png_bytes(64, 32, (1, 2, 3)))
                    expected = "selected asset hash does not match approved asset"
                else:
                    manifest["stitch_invoked"] = True
                    expected = "Stitch invocation requires a preserved Stitch asset set"
                result = run_validator(root, manifest)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(expected, result.stderr)

    def test_required_raster_is_blocked_without_native_image_generation(self) -> None:
        """Allowing a raster substitute on a non-image runtime must break this rejection."""
        with tempfile.TemporaryDirectory(prefix="design-arc-raster-block-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "platform")
            manifest["active_platform"] = {"name": "claude-code", "native_image_generation": False}
            result = run_validator(root, manifest)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("required raster asset is blocked because claude-code lacks native image generation", result.stderr)

    def test_broken_or_absent_selected_asset_is_rejected_by_the_browser(self) -> None:
        """Removing load and DOM-presence checks must make one runtime mutation pass."""
        for label in ("broken", "absent"):
            with self.subTest(label=label), tempfile.TemporaryDirectory(prefix=f"design-arc-runtime-{label}-") as temp:
                root = Path(temp)
                manifest = manifest_for(root, "platform")
                if label == "broken":
                    asset_path = root / "assets/platform-journey.png"
                    asset_path.write_bytes(b"not a decodable image")
                    manifest["asset_sets"]["platform"][0]["sha256"] = sha256(asset_path)
                    expected = "selected platform.journey is broken in the running application at desktop"
                else:
                    html = (root / "index.html").read_text(encoding="utf-8")
                    start = html.index('    <img data-design-arc-asset="platform.journey"')
                    end = html.index("\n", start)
                    html = html[:start] + "    <!-- assets/platform-journey.png remains approved -->" + html[end:]
                    (root / "index.html").write_text(html, encoding="utf-8")
                    expected = "selected platform.journey is absent from running application at desktop"
                result = run_validator(root, manifest)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(expected, result.stderr)

    def test_unapproved_runtime_mixing_references_are_rejected(self) -> None:
        """Dropping the unselected-set source scan must allow this forbidden mixture."""
        with tempfile.TemporaryDirectory(prefix="design-arc-mixed-source-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "stitch")
            manifest["selection"] = {
                "design": "platform",
                "hybrid_approved": False,
                "asset_ids": ["platform.journey"],
            }
            html = (root / "index.html").read_text(encoding="utf-8")
            html = html.replace(
                '<img data-design-arc-asset="stitch.journey"',
                '<img data-design-arc-asset="platform.journey" src="assets/platform-journey.png" '
                'alt="Evidence-backed onboarding journey">\n'
                '    <img data-design-arc-asset="stitch.journey"',
            )
            (root / "index.html").write_text(html, encoding="utf-8")
            result = run_validator(root, manifest)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("unselected stitch asset is referenced by implementation source", result.stderr)

    def test_flattened_semantic_control_is_rejected_in_the_running_app(self) -> None:
        """Treating visual text as a semantic button must break this rejection."""
        with tempfile.TemporaryDirectory(prefix="design-arc-semantic-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "platform")
            html = (root / "index.html").read_text(encoding="utf-8")
            html = html.replace(
                '<button id="continue" type="button">Continue</button>',
                '<img id="continue" src="assets/platform-journey.png" alt="Continue">',
            )
            (root / "index.html").write_text(html, encoding="utf-8")
            result = run_validator(root, manifest)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("semantic control #continue must render as button", result.stderr)

    def test_required_control_must_remain_keyboard_focusable(self) -> None:
        """Dropping actual focus verification must allow this disabled control."""
        with tempfile.TemporaryDirectory(prefix="design-arc-focus-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "platform")
            html = (root / "index.html").read_text(encoding="utf-8")
            html = html.replace(
                '<button id="continue" type="button">Continue</button>',
                '<button id="continue" type="button" disabled>Continue</button>',
            )
            (root / "index.html").write_text(html, encoding="utf-8")
            result = run_validator(root, manifest)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("semantic control #continue is not focusable at desktop", result.stderr)

    def test_asset_hidden_at_mobile_viewport_cannot_match_the_proposal(self) -> None:
        """Dropping either viewport inspection must break this rejection."""
        with tempfile.TemporaryDirectory(prefix="design-arc-mobile-hidden-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "platform")
            html = (root / "index.html").read_text(encoding="utf-8")
            html = html.replace(
                "[data-design-arc-asset] { width: 240px; height: 120px; }",
                "[data-design-arc-asset] { display: none; width: 240px; height: 120px; }",
            )
            (root / "index.html").write_text(html, encoding="utf-8")
            result = run_validator(root, manifest)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("selected platform.journey is not visibly rendered at mobile", result.stderr)

    def test_missing_supported_browser_fails_with_a_clear_action(self) -> None:
        """Silently skipping browser proof when no browser exists must break this rejection."""
        with tempfile.TemporaryDirectory(prefix="design-arc-no-browser-") as temp:
            root = Path(temp)
            environment = dict(os.environ)
            environment["DESIGN_ARC_BROWSER"] = str(root / "missing-browser")
            result = run_validator(root, manifest_for(root, "platform"), environment=environment)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("DESIGN_ARC_BROWSER does not name an executable Chrome or Chromium browser", result.stderr)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AssetFidelityAcceptanceTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("PASS: Design Arc asset-fidelity browser acceptance suite")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
