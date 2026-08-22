#!/usr/bin/env python3
"""Behavioral acceptance tests for Design Arc's selected-asset fidelity gate."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import contextmanager
import base64
import functools
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import signal
import struct
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import zlib


REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = REPO_ROOT / "scripts/validate-asset-fidelity.py"
JPEG_FIXTURE = base64.b64decode(
    "/9j/4AAQSkZJRgABAQAASABIAAD/4QBMRXhpZgAATU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAAAQKADAAQAAAABAAAAIAAAAAD/7QA4UGhvdG9zaG9wIDMuMAA4QklNBAQAAAAAAAA4QklNBCUAAAAAABDUHYzZjwCyBOmACZjs+EJ+/8AAEQgAIABAAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQYHCAkKC//EALUQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+v/EAB8BAAMBAQEBAQEBAQEAAAAAAAABAgMEBQYHCAkKC//EALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXETIjKBCBRCkaGxwQkjM1LwFWJy0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/bAEMAAQEBAQEBAgEBAgICAgICAwICAgIDBAMDAwMDBAUEBAQEBAQFBQUFBQUFBQYGBgYGBgcHBwcHCAgICAgICAgICP/bAEMBAQEBAgICAwICAwgFBQUICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICP/dAAQABP/aAAwDAQACEQMRAD8A/tYooor8nPsAooooAKKKKACiiigD/9D+1iiiivyc+wCiiigAooooAKKKKAP/2Q=="
)


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
    nav {{ height: 40px; }}
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
                "desktop": {"x": 24, "y": 64, "width": 320, "height": 160, "tolerance": 1},
                "mobile": {"x": 24, "y": 64, "width": 240, "height": 120, "tolerance": 1},
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
    evidence_output: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    manifest_path = write_manifest(root, manifest)
    command = [sys.executable, str(VALIDATOR), str(manifest_path)]
    if evidence_output is not None:
        command.extend(["--evidence-output", str(evidence_output)])
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=environment,
        timeout=45,
    )


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        return


@contextmanager
def serve_directory(root: Path):
    handler = functools.partial(QuietHandler, directory=str(root))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def install_hybrid_app(root: Path, manifest: dict[str, object]) -> None:
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
    stitch = manifest["asset_sets"]["stitch"][0]
    stitch["render"]["desktop"]["y"] = 224
    stitch["render"]["mobile"]["y"] = 184


def process_is_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


class AssetFidelityAcceptanceTests(unittest.TestCase):
    def test_platform_selection_matches_exact_asset_on_desktop_and_mobile(self) -> None:
        """Removing browser rendering or either viewport proof must break this pass."""
        with tempfile.TemporaryDirectory(prefix="design-arc-platform-") as temp:
            root = Path(temp)
            result = run_validator(root, manifest_for(root, "platform"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: asset fidelity matches approved proposal at desktop and mobile viewports", result.stdout)

    def test_browser_native_reference_sampling_accepts_real_jpeg_asset(self) -> None:
        """Decoding approved references as PNG-only must break this browser-supported JPEG."""
        with tempfile.TemporaryDirectory(prefix="design-arc-jpeg-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "platform")
            jpeg = root / "assets/platform-journey.jpg"
            jpeg.write_bytes(JPEG_FIXTURE)
            asset = manifest["asset_sets"]["platform"][0]
            asset.update(
                {
                    "path": "assets/platform-journey.jpg",
                    "sha256": sha256(jpeg),
                    "media_type": "image/jpeg",
                }
            )
            html = (root / "index.html").read_text(encoding="utf-8")
            html = html.replace("assets/platform-journey.png", "assets/platform-journey.jpg")
            (root / "index.html").write_text(html, encoding="utf-8")
            result = run_validator(root, manifest)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("selected platform.journey rendered at mobile", result.stdout)

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
            install_hybrid_app(root, manifest)
            result = run_validator(root, manifest)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("selected platform.journey rendered at desktop", result.stdout)
        self.assertIn("selected stitch.journey rendered at mobile", result.stdout)

    def test_runtime_rejects_same_path_asset_from_a_second_live_origin(self) -> None:
        """Comparing only a URL path must allow this wrong-origin substitution."""
        with tempfile.TemporaryDirectory(prefix="design-arc-wrong-origin-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "platform")
            with serve_directory(root) as foreign_origin:
                html = (root / "index.html").read_text(encoding="utf-8")
                html = html.replace(
                    'src="assets/platform-journey.png"',
                    f'src="{foreign_origin}/assets/platform-journey.png"',
                    1,
                )
                (root / "index.html").write_text(html, encoding="utf-8")
                result = run_validator(root, manifest)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("selected platform.journey loaded from an unapproved origin at desktop", result.stderr)

    def test_acceptance_viewports_cannot_be_self_declared(self) -> None:
        """Trusting manifest viewport values must allow these weaker proofs."""
        cases = (
            ("desktop", {"width": 1024, "height": 720}, "desktop viewport must be exactly 1280x720"),
            ("mobile", {"width": 400, "height": 800}, "mobile viewport must be exactly 390x844"),
        )
        for viewport, dimensions, expected in cases:
            with self.subTest(viewport=viewport), tempfile.TemporaryDirectory(prefix=f"design-arc-{viewport}-") as temp:
                root = Path(temp)
                manifest = manifest_for(root, "platform")
                manifest["viewports"][viewport] = dimensions
                result = run_validator(root, manifest)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(expected, result.stderr)

    def test_hybrid_selection_cannot_omit_a_required_asset(self) -> None:
        """Skipping required-set completeness for hybrids must allow this omission."""
        with tempfile.TemporaryDirectory(prefix="design-arc-hybrid-omission-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "stitch")
            install_hybrid_app(root, manifest)
            second = root / "assets/platform-supporting.png"
            second.write_bytes(png_bytes(32, 16, (10, 20, 30)))
            required_asset = dict(manifest["asset_sets"]["platform"][0])
            required_asset.update(
                {
                    "id": "platform.supporting",
                    "path": "assets/platform-supporting.png",
                    "sha256": sha256(second),
                    "selector": '[data-design-arc-asset="platform.supporting"]',
                }
            )
            manifest["asset_sets"]["platform"].append(required_asset)
            result = run_validator(root, manifest)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("hybrid selection omits a required asset: platform.supporting", result.stderr)

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

    def test_selected_asset_requires_its_exact_stable_id_in_implementation_source(self) -> None:
        """A selector rewritten around an unapproved marker must not replace source-level ID proof."""
        with tempfile.TemporaryDirectory(prefix="design-arc-stable-asset-id-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "platform")
            html = (root / "index.html").read_text(encoding="utf-8")
            html = html.replace('data-design-arc-asset="platform.journey"', 'data-design-arc-asset="not-approved-id"')
            (root / "index.html").write_text(html, encoding="utf-8")
            manifest["asset_sets"]["platform"][0]["selector"] = '[data-design-arc-asset="not-approved-id"]'
            result = run_validator(root, manifest)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(
            "selected asset stable ID is not referenced by implementation source: platform.journey",
            result.stderr,
        )

    def test_comment_only_stable_id_does_not_bind_the_live_rendered_asset(self) -> None:
        """A source comment must not bind an approved ID to a differently marked live asset."""
        with tempfile.TemporaryDirectory(prefix="design-arc-comment-only-asset-id-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "platform")
            html = (root / "index.html").read_text(encoding="utf-8")
            html = html.replace(
                '<img data-design-arc-asset="platform.journey"',
                '<!-- platform.journey uses assets/platform-journey.png -->\n'
                '    <img data-design-arc-asset="not-approved-id"',
            )
            (root / "index.html").write_text(html, encoding="utf-8")
            manifest["asset_sets"]["platform"][0]["selector"] = (
                '[data-design-arc-asset="not-approved-id"]'
            )
            result = run_validator(root, manifest)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(
            "selected platform.journey live asset marker does not match approved stable ID at desktop",
            result.stderr,
        )

    def test_responsive_live_asset_marker_must_match_at_mobile(self) -> None:
        """Checking the stable marker only at desktop must allow this mobile-only drift."""
        with tempfile.TemporaryDirectory(prefix="design-arc-mobile-asset-id-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "platform")
            html = (root / "index.html").read_text(encoding="utf-8")
            html = html.replace(
                "</body>",
                """<script>
if (matchMedia('(max-width: 600px)').matches) {
  document.querySelector('[data-design-arc-asset]').setAttribute(
    'data-design-arc-asset', 'not-approved-id'
  );
}
</script>
</body>""",
            )
            (root / "index.html").write_text(html, encoding="utf-8")
            manifest["asset_sets"]["platform"][0]["selector"] = (
                'img[src="assets/platform-journey.png"]'
            )
            result = run_validator(root, manifest)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("PASS: selected platform.journey rendered at desktop", result.stdout)
        self.assertIn(
            "selected platform.journey live asset marker does not match approved stable ID at mobile",
            result.stderr,
        )

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
                    html = html[:start] + "    <!-- platform.journey uses assets/platform-journey.png -->" + html[end:]
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

    def test_runtime_rejects_dynamically_composed_unselected_assets(self) -> None:
        """Static source scans must not miss known assets loaded or rendered only at runtime."""
        cases = ("live-image", "removed-image", "css-background")
        for label in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory(
                prefix=f"design-arc-runtime-mixed-{label}-"
            ) as temp:
                root = Path(temp)
                manifest = manifest_for(root, "stitch")
                manifest["selection"] = {
                    "design": "platform",
                    "hybrid_approved": False,
                    "asset_ids": ["platform.journey"],
                }
                if label == "live-image":
                    runtime_use = """
const image = document.createElement('img');
image.setAttribute('data-design-arc-asset', assetId);
image.src = assetPath;
image.alt = 'Unapproved Stitch journey';
document.body.append(image);
"""
                elif label == "removed-image":
                    runtime_use = """
const image = document.createElement('img');
image.setAttribute('data-design-arc-asset', assetId);
image.src = assetPath;
image.alt = 'Unapproved Stitch journey';
document.body.append(image);
window.addEventListener('load', () => image.remove(), {once: true});
"""
                else:
                    runtime_use = """
const panel = document.createElement('div');
panel.style.cssText = 'width:64px;height:32px;background-size:cover';
panel.style.backgroundImage = 'url("' + assetPath + '")';
document.body.append(panel);
"""
                script = """<script>
const assetPath = ['assets', 'stitch-journey.png'].join('/');
const assetId = ['stitch', 'journey'].join('.');
""" + runtime_use + """</script>
"""
                html = app_html("platform.journey", "assets/platform-journey.png")
                html = html.replace("</body>", script + "</body>")
                (root / "index.html").write_text(html, encoding="utf-8")
                result = run_validator(root, manifest)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(
                    "unselected known asset stitch.journey is loaded or rendered "
                    "in running application at desktop",
                    result.stderr,
                )

    def test_hybrid_runtime_rejects_known_asset_outside_the_approved_selection(self) -> None:
        """Hybrid approval must not authorize known assets omitted from its explicit selection."""
        with tempfile.TemporaryDirectory(prefix="design-arc-hybrid-unselected-runtime-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "stitch")
            install_hybrid_app(root, manifest)
            optional_path = root / "assets/platform-optional.png"
            optional_path.write_bytes(png_bytes(32, 16, (48, 120, 210)))
            manifest["asset_sets"]["platform"].append(
                {
                    "id": "platform.optional",
                    "path": "assets/platform-optional.png",
                    "sha256": sha256(optional_path),
                    "media_type": "image/png",
                    "required": False,
                }
            )
            html = (root / "index.html").read_text(encoding="utf-8")
            html = html.replace(
                "</body>",
                """<script>
const optionalPath = ['assets', 'platform-optional.png'].join('/');
const optionalId = ['platform', 'optional'].join('.');
const optionalImage = document.createElement('img');
optionalImage.setAttribute('data-design-arc-asset', optionalId);
optionalImage.src = optionalPath;
optionalImage.alt = 'Unapproved optional platform asset';
document.body.append(optionalImage);
</script>
</body>""",
            )
            (root / "index.html").write_text(html, encoding="utf-8")
            result = run_validator(root, manifest)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(
            "unselected known asset platform.optional is loaded or rendered "
            "in running application at desktop",
            result.stderr,
        )

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

    def test_manifest_cannot_self_approve_inert_or_nonexistent_semantics(self) -> None:
        """Trusting manifest element names must allow invalid anchors and invented status tags."""
        cases = ("inert-anchor", "invented-status", "inert-navigation")
        for label in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory(prefix=f"design-arc-{label}-") as temp:
                root = Path(temp)
                manifest = manifest_for(root, "platform")
                html = (root / "index.html").read_text(encoding="utf-8")
                if label == "inert-anchor":
                    html = html.replace(
                        '<button id="continue" type="button">Continue</button>',
                        '<a id="continue">Continue</a>',
                    )
                    control = next(item for item in manifest["semantic_requirements"] if item["selector"] == "#continue")
                    control["element"] = "a"
                    control.pop("focusable", None)
                    expected = "semantic control #continue must be an interactive native control"
                elif label == "invented-status":
                    html = html.replace(
                        '<output id="status" aria-label="Ready">Ready</output>',
                        '<status id="status" aria-label="Ready">Ready</status>',
                    )
                    status = next(item for item in manifest["semantic_requirements"] if item["selector"] == "#status")
                    status["element"] = "status"
                    expected = "semantic status #status must use a native status element"
                else:
                    html = html.replace(
                        '<nav aria-label="Primary"><a href="#review">Review</a></nav>',
                        '<nav aria-label="Primary">Primary</nav>',
                    )
                    expected = "semantic navigation nav has no focusable navigation target at desktop"
                (root / "index.html").write_text(html, encoding="utf-8")
                result = run_validator(root, manifest)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(expected, result.stderr)

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
        self.assertIn("semantic control #continue must be an interactive native control", result.stderr)

    def test_offscreen_native_control_cannot_decoy_for_visible_flattened_control(self) -> None:
        """A focusable native decoy must not satisfy semantics while a raster substitute is visible."""
        with tempfile.TemporaryDirectory(prefix="design-arc-semantic-decoy-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "platform")
            html = (root / "index.html").read_text(encoding="utf-8")
            html = html.replace(
                '<button id="continue" type="button">Continue</button>',
                '<button id="continue" type="button" style="position:fixed;left:-10000px;top:-10000px">Continue</button>'
                '<img src="assets/platform-journey.png" alt="Continue" style="width:120px;height:40px">',
            )
            (root / "index.html").write_text(html, encoding="utf-8")
            result = run_validator(root, manifest)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(
            "semantic control #continue is not visibly rendered at desktop",
            result.stderr,
        )

    def test_pointer_transparent_flattened_substitute_cannot_cover_native_control(self) -> None:
        """Visual coverage must notice a flattened substitute even when it ignores pointer input."""
        with tempfile.TemporaryDirectory(prefix="design-arc-semantic-covered-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "platform")
            html = (root / "index.html").read_text(encoding="utf-8")
            html = html.replace(
                '<button id="continue" type="button">Continue</button>',
                '<span style="position:relative;display:inline-block">'
                '<button id="continue" type="button">Continue</button>'
                '<img src="assets/platform-journey.png" alt="" '
                'style="position:absolute;inset:0;width:100%;height:100%;z-index:2;pointer-events:none">'
                '</span>',
            )
            (root / "index.html").write_text(html, encoding="utf-8")
            result = run_validator(root, manifest)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(
            "semantic control #continue is not visibly rendered at desktop",
            result.stderr,
        )

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

    def test_screenshot_pixels_reject_pointer_transparent_occlusion(self) -> None:
        """DOM visibility and center hit-testing alone must allow this fully painted overlay."""
        with tempfile.TemporaryDirectory(prefix="design-arc-screenshot-overlay-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "platform")
            html = (root / "index.html").read_text(encoding="utf-8")
            html = html.replace(
                "</body>",
                '<div style="position:fixed;left:24px;top:64px;width:320px;height:160px;'
                'background:#000;z-index:99;pointer-events:none"></div></body>',
            )
            (root / "index.html").write_text(html, encoding="utf-8")
            result = run_validator(root, manifest)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("selected platform.journey screenshot coverage is below 90% at desktop", result.stderr)

    def test_application_cannot_spoof_reference_pixels_with_canvas_monkey_patch(self) -> None:
        """Computing expected colors in the application realm must falsely approve this overlay."""
        with tempfile.TemporaryDirectory(prefix="design-arc-canvas-spoof-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "platform")
            html = (root / "index.html").read_text(encoding="utf-8")
            spoof = """<script>
CanvasRenderingContext2D.prototype.getImageData = function () {
  return {data: new Uint8ClampedArray([0, 0, 0, 255])};
};
</script>"""
            html = html.replace("</head>", spoof + "</head>")
            html = html.replace(
                "</body>",
                '<div style="position:fixed;left:24px;top:64px;width:320px;height:160px;'
                'background:#000;z-index:99;pointer-events:none"></div></body>',
            )
            (root / "index.html").write_text(html, encoding="utf-8")
            result = run_validator(root, manifest)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("selected platform.journey screenshot coverage is below 90% at desktop", result.stderr)

    def test_success_retains_real_screenshot_hashes_and_asset_coverage(self) -> None:
        """Removing screenshot capture or content comparison must erase this proof result."""
        with tempfile.TemporaryDirectory(prefix="design-arc-screenshot-proof-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "platform")
            evidence = root / "browser-proof.json"
            result = run_validator(root, manifest, evidence_output=evidence)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            proof = json.loads(evidence.read_text(encoding="utf-8"))
        self.assertEqual(set(proof["viewports"]), {"desktop", "mobile"})
        boundary = proof["reference_trust_boundary"]
        self.assertTrue(boundary["separate_application_origin"])
        self.assertTrue(boundary["independent_browser_profile"])
        self.assertFalse(boundary["application_content_served"])
        for viewport in ("desktop", "mobile"):
            self.assertRegex(proof["viewports"][viewport]["screenshot_sha256"], r"^[0-9a-f]{64}$")
            self.assertGreaterEqual(
                proof["viewports"][viewport]["assets"]["platform.journey"]["pixel_coverage"],
                0.9,
            )

    def test_evidence_output_cannot_alias_any_validation_input(self) -> None:
        """Evidence output must fail closed before overwriting a source or asset, including symlink aliases."""
        for label in ("source", "asset-symlink"):
            with self.subTest(label=label), tempfile.TemporaryDirectory(prefix=f"design-arc-evidence-alias-{label}-") as temp:
                root = Path(temp)
                manifest = manifest_for(root, "platform")
                manifest_path = write_manifest(root, manifest)
                source_path = root / "index.html"
                asset_path = root / "assets/platform-journey.png"
                protected = (manifest_path, source_path, asset_path)
                before = {path: path.read_bytes() for path in protected}
                if label == "source":
                    evidence_output = source_path
                else:
                    evidence_output = root / "browser-proof.json"
                    evidence_output.symlink_to(asset_path)
                result = run_validator(root, manifest, evidence_output=evidence_output)
                after = {path: path.read_bytes() for path in protected}
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("evidence output aliases a validation input", result.stderr)
                self.assertEqual(before, after, "validator changed a protected input before rejecting the alias")

    def test_missing_supported_browser_fails_with_a_clear_action(self) -> None:
        """Silently skipping browser proof when no browser exists must break this rejection."""
        with tempfile.TemporaryDirectory(prefix="design-arc-no-browser-") as temp:
            root = Path(temp)
            environment = dict(os.environ)
            environment["DESIGN_ARC_BROWSER"] = str(root / "missing-browser")
            result = run_validator(root, manifest_for(root, "platform"), environment=environment)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("DESIGN_ARC_BROWSER does not name an executable Chrome or Chromium browser", result.stderr)

    def test_enter_stage_failure_cleans_live_browser_process_and_profile(self) -> None:
        """Raising during DevTools connection must not leak the launched process or profile."""
        with tempfile.TemporaryDirectory(prefix="design-arc-enter-cleanup-") as temp:
            root = Path(temp)
            manifest = manifest_for(root, "platform")
            pid_path = root / "fake-browser.pid"
            profile_path = root / "fake-browser.profile"
            fake_browser = root / "fake-browser.py"
            fake_browser.write_text(
                f"""#!{sys.executable}
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from pathlib import Path
import sys

port = int(next(value.split('=', 1)[1] for value in sys.argv if value.startswith('--remote-debugging-port=')))
profile = next(value.split('=', 1)[1] for value in sys.argv if value.startswith('--user-data-dir='))
Path(os.environ['DESIGN_ARC_FAKE_PID']).write_text(str(os.getpid()), encoding='utf-8')
Path(os.environ['DESIGN_ARC_FAKE_PROFILE']).write_text(profile, encoding='utf-8')

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass
    def do_GET(self):
        body = json.dumps([{{'type': 'page', 'webSocketDebuggerUrl': 'ws://127.0.0.1:1/devtools/page/fail'}}]).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

HTTPServer(('127.0.0.1', port), Handler).serve_forever()
""",
                encoding="utf-8",
            )
            fake_browser.chmod(0o755)
            environment = dict(os.environ)
            environment.update(
                {
                    "DESIGN_ARC_BROWSER": str(fake_browser),
                    "DESIGN_ARC_FAKE_PID": str(pid_path),
                    "DESIGN_ARC_FAKE_PROFILE": str(profile_path),
                }
            )
            result = run_validator(root, manifest, environment=environment)
            pid = int(pid_path.read_text(encoding="utf-8"))
            launched_profile = Path(profile_path.read_text(encoding="utf-8"))
            time.sleep(0.2)
            alive = process_is_alive(pid)
            profile_exists = launched_profile.exists()
            if alive:
                os.kill(pid, signal.SIGTERM)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("Connection refused", result.stderr)
        self.assertFalse(alive, "browser process leaked after __enter__ failure")
        self.assertFalse(profile_exists, "browser profile leaked after __enter__ failure")


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AssetFidelityAcceptanceTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("PASS: Design Arc asset-fidelity browser acceptance suite")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
