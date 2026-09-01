#!/bin/sh
# Verify the canonical Design Arc package identity and marketplace layout.

set -eu

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(CDPATH= cd "$script_dir/.." && pwd)
plugin_path="$repo_root/plugins/design-arc"
plugin_manifest="$plugin_path/.codex-plugin/plugin.json"
skill_path="$plugin_path/skills/design-arc/SKILL.md"
metadata_path="$plugin_path/skills/design-arc/agents/openai.yaml"
marketplace_manifest="$repo_root/.agents/plugins/marketplace.json"
directory_logo="$repo_root/assets/design-arc-directory-logo.png"
directory_logo_master="$repo_root/assets/design-arc-directory-logo.svg"
plugin_logo="$plugin_path/assets/design-arc-directory-logo.png"
codex_skills_dir=${CODEX_SKILLS_DIR:-"$HOME/.codex/skills"}
plugin_validator="$codex_skills_dir/.system/plugin-creator/scripts/validate_plugin.py"
skill_validator="$codex_skills_dir/.system/skill-creator/scripts/quick_validate.py"

fail() {
  printf '%s\n' "FAIL: $*" >&2
  exit 1
}

for required_file in "$plugin_manifest" "$skill_path" "$metadata_path" "$marketplace_manifest" "$directory_logo_master" "$directory_logo" "$plugin_logo"
do
  [ -f "$required_file" ] || fail "missing Design Arc identity file: ${required_file#"$repo_root/"}"
done

[ -s "$directory_logo" ] || fail 'Plugin Directory logo must not be empty'
[ -s "$plugin_logo" ] || fail 'packaged plugin logo must not be empty'

python3 - "$directory_logo_master" "$directory_logo" "$plugin_logo" "${DESIGN_ARC_ICON_RENDERER:-magick}" <<'PY'
import hashlib
import math
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import deque
from itertools import combinations
from pathlib import Path

master_path, directory_path, plugin_path = map(Path, sys.argv[1:4])
renderer = sys.argv[4]

for path in (directory_path, plugin_path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise SystemExit(f"{path.name} must be a PNG image")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (1024, 1024):
        raise SystemExit(f"{path.name} must be exactly 1024x1024, got {width}x{height}")

if hashlib.sha256(directory_path.read_bytes()).digest() != hashlib.sha256(plugin_path.read_bytes()).digest():
    raise SystemExit("repository and packaged plugin logos must be byte-identical")

root = ET.parse(master_path).getroot()
svg = "{http://www.w3.org/2000/svg}"
if root.get("width") != "1024" or root.get("height") != "1024" or root.get("viewBox") != "0 0 1024 1024":
    raise SystemExit("SVG master must use the canonical 1024x1024 canvas")

backgrounds = [node for node in root.findall(f"{svg}rect") if node.get("data-part") == "background"]
stages = [node for node in root.findall(f"{svg}path") if node.get("data-part", "").startswith("stage-")]
endpoints = [node for node in root.findall(f"{svg}circle") if node.get("data-part") == "endpoint"]
if len(backgrounds) != 1 or backgrounds[0].get("x", "0") != "0" or backgrounds[0].get("y", "0") != "0" or backgrounds[0].get("width") != "1024" or backgrounds[0].get("height") != "1024":
    raise SystemExit("SVG master must contain one full-bleed background")
if backgrounds[0].get("rx") is not None or backgrounds[0].get("ry") is not None:
    raise SystemExit("SVG background must remain a square without rounded corners")
if backgrounds[0].get("fill") != "#11130f":
    raise SystemExit("SVG background must use the canonical charcoal fill")
if len(stages) != 3 or [node.get("data-part") for node in stages] != ["stage-1", "stage-2", "stage-3"]:
    raise SystemExit("SVG master must contain exactly three separate journey stages")
if len(endpoints) != 1:
    raise SystemExit("SVG master must contain exactly one coral endpoint")
if any(node.get("fill") != "#f3ead8" for node in stages):
    raise SystemExit("all journey stages must use the canonical ivory fill")
if endpoints[0].get("fill") != "#ff5a3c":
    raise SystemExit("journey endpoint must use the canonical coral fill")
if any(node.get("stroke") not in (None, "none") for node in root.iter()):
    raise SystemExit("SVG master must not use outlines")
for forbidden in ("linearGradient", "radialGradient", "filter", "text"):
    if root.findall(f".//{svg}{forbidden}"):
        raise SystemExit(f"SVG master must not contain {forbidden}")


def stage_points(node):
    commands = re.findall(r"[A-Za-z]", node.get("d", ""))
    numbers = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", node.get("d", ""))]
    if commands != ["M", "L", "L", "L", "L", "L", "Z"] or len(numbers) != 12:
        raise SystemExit(f"{node.get('data-part')} must use the canonical six-point directional contour")
    points = list(zip(numbers[::2], numbers[1::2]))
    if any(not (0 <= coordinate <= 1024) for point in points for coordinate in point):
        raise SystemExit(f"{node.get('data-part')} must stay inside the SVG canvas")
    return points


geometry = []
for node in stages:
    points = stage_points(node)
    top_left, top_right, nose, bottom_right, bottom_left, tail = points
    width = max(x for x, _ in points) - min(x for x, _ in points)
    height = max(y for _, y in points) - min(y for _, y in points)
    left_thickness = bottom_left[1] - top_left[1]
    right_thickness = bottom_right[1] - top_right[1]
    if width < 2.5 * height:
        raise SystemExit(f"{node.get('data-part')} must remain broad and shallow")
    if left_thickness < 1.25 * right_thickness:
        raise SystemExit(f"{node.get('data-part')} must taper visibly toward its leading edge")
    if nose[0] - max(top_right[0], bottom_right[0]) < 48:
        raise SystemExit(f"{node.get('data-part')} must have a directional leading nose")
    if min(top_left[0], bottom_left[0]) - tail[0] < 24:
        raise SystemExit(f"{node.get('data-part')} must have a directional trailing cut")
    if top_left[1] - top_right[1] < 30 or bottom_left[1] - bottom_right[1] < 30:
        raise SystemExit(f"{node.get('data-part')} must rise from left to right")
    geometry.append(
        {
            "points": points,
            "width": width,
            "height": height,
            "center_x": (min(x for x, _ in points) + max(x for x, _ in points)) / 2,
            "center_y": (min(y for _, y in points) + max(y for _, y in points)) / 2,
        }
    )

if not all(left["center_x"] < right["center_x"] and left["center_y"] > right["center_y"] for left, right in zip(geometry, geometry[1:])):
    raise SystemExit("journey stages must rise in order from lower-left to upper-right")
if not all(left["width"] - right["width"] >= 60 and left["height"] > right["height"] for left, right in zip(geometry, geometry[1:])):
    raise SystemExit("journey stages must become progressively smaller")

endpoint = endpoints[0]
try:
    endpoint_x = float(endpoint.get("cx", ""))
    endpoint_y = float(endpoint.get("cy", ""))
    endpoint_radius = float(endpoint.get("r", ""))
except ValueError as exc:
    raise SystemExit("journey endpoint must use deterministic numeric circle geometry") from exc
final = geometry[-1]
endpoint_ratio = (2 * endpoint_radius) / final["width"]
if not 0.22 <= endpoint_ratio <= 0.36:
    raise SystemExit("journey endpoint must remain approximately one-third the final-stage width")
if endpoint_x <= max(x for x, _ in final["points"]) or endpoint_y + endpoint_radius >= min(y for _, y in final["points"]):
    raise SystemExit("journey endpoint must sit beyond and above the final stage")

renderer_path = shutil.which(renderer)
if renderer_path is None:
    raise SystemExit(f"selected SVG renderer is unavailable: {renderer}")
with tempfile.TemporaryDirectory(prefix="design-arc-icon-identity-") as temporary:
    rendered = Path(temporary) / "rendered.png"
    render = subprocess.run(
        [renderer_path, "-background", "none", str(master_path), "-strip", f"PNG32:{rendered}"],
        capture_output=True,
        check=False,
    )
    if render.returncode != 0:
        raise SystemExit(f"selected SVG renderer failed: {render.stderr.decode('utf-8', errors='replace').strip()}")
    if rendered.read_bytes() != directory_path.read_bytes():
        raise SystemExit("tracked PNGs must be byte-identical to the selected renderer's SVG output")

small_render = subprocess.run(
    [renderer_path, "-background", "none", str(master_path), "-filter", "Lanczos", "-resize", "32x32!", "-depth", "8", "RGBA:-"],
    capture_output=True,
    check=False,
)
if small_render.returncode != 0 or len(small_render.stdout) != 32 * 32 * 4:
    raise SystemExit("selected SVG renderer must produce a 32x32 RGBA raster")

ivory = (0xF3, 0xEA, 0xD8)
pixels = set()
for index in range(32 * 32):
    red, green, blue, alpha = small_render.stdout[index * 4 : index * 4 + 4]
    if alpha >= 200 and sum((channel - target) ** 2 for channel, target in zip((red, green, blue), ivory)) <= 45**2:
        pixels.add((index % 32, index // 32))

components = []
while pixels:
    start = pixels.pop()
    component = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                neighbor = (x + dx, y + dy)
                if neighbor in pixels:
                    pixels.remove(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
    if len(component) >= 3:
        components.append(component)
if len(components) != 3:
    raise SystemExit(f"32px raster must contain exactly three ivory stage components, got {len(components)}")

raster_geometry = []
for component in components:
    xs = [point[0] for point in component]
    ys = [point[1] for point in component]
    raster_geometry.append((sum(xs) / len(xs), sum(ys) / len(ys), len(component)))
raster_geometry.sort(key=lambda item: item[1], reverse=True)
if not all(left[0] < right[0] and left[1] > right[1] and left[2] > right[2] for left, right in zip(raster_geometry, raster_geometry[1:])):
    raise SystemExit("32px stage components must rise rightward and become progressively smaller")
minimum_gap = min(
    min(math.hypot(x1 - x2, y1 - y2) for x1, y1 in left for x2, y2 in right) - 1
    for left, right in combinations(components, 2)
)
if minimum_gap < 2:
    raise SystemExit(f"32px stage separation must be at least 2px, got {minimum_gap:.3f}px")
print(
    "PASS: deterministic icon color, geometry, renderer parity, and "
    f"32px three-stage raster ({minimum_gap:.3f}px minimum gap)"
)
PY

[ ! -e "$repo_root/plugins/fb-ux" ] || fail 'legacy fb-ux package remains active in the repository tree'
[ ! -e "$repo_root/plugins/apple-guidelines-stitch" ] || fail 'legacy apple-guidelines-stitch package remains active in the repository tree'

[ -f "$plugin_validator" ] || fail 'plugin validator is unavailable'
[ -f "$skill_validator" ] || fail 'skill validator is unavailable'
python3 "$plugin_validator" "$plugin_path"
python3 "$skill_validator" "$(dirname "$skill_path")"

python3 - "$plugin_manifest" "$marketplace_manifest" "$metadata_path" <<'PY'
import json
import sys
from pathlib import Path

plugin_path, marketplace_path, metadata_path = map(Path, sys.argv[1:])
plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
metadata = metadata_path.read_text(encoding="utf-8")

expected_plugin = {
    "name": "design-arc",
    "version": "1.5.3",
    "description": "Live: outcome-led UI journey design for Codex.",
    "skills": "./skills/",
    "author": {"name": "James Yeang"},
    "repository": "https://github.com/friedbeef1/design-arc",
    "license": "MIT",
    "keywords": ["ux", "journey-design", "outcomes", "evidence"],
    "interface": {
        "displayName": "Design Arc",
        "shortDescription": "Evidence-backed UI journeys",
        "longDescription": "Turn vague product feedback into a complete, evidence-backed design direction. Design Arc confirms the outcome, audits the real journey, grounds recommendations in current platform guidance and optional product benchmarks, and checks every important state before frontend implementation.",
        "developerName": "James Yeang",
        "category": "Productivity",
        "capabilities": ["Outcome-led journey design", "Evidence-grounded validation"],
        "composerIcon": "./assets/design-arc-directory-logo.png",
        "logo": "./assets/design-arc-directory-logo.png",
        "defaultPrompt": [
            "$design-arc Help me make our onboarding less confusing.",
            "$design-arc Audit how customers complete checkout and propose a better complete journey.",
            "$design-arc Redesign account recovery so people can get back in without weakening security.",
        ],
    },
}
if plugin != expected_plugin:
    raise SystemExit("Design Arc manifest must match the canonical identity contract")

expected_marketplace = {
    "name": "design-arc-marketplace",
    "interface": {"displayName": "Design Arc"},
    "plugins": [
        {
            "name": "design-arc",
            "source": {"source": "local", "path": "./plugins/design-arc"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        }
    ],
}
if marketplace != expected_marketplace:
    raise SystemExit("marketplace must expose exactly the canonical Design Arc entry")

expected_metadata = '''interface:
  display_name: "Design Arc"
  short_description: "Turn ambiguous UI feedback into complete, evidence-grounded journeys"
  default_prompt: "$design-arc Help me make this product journey less confusing."
'''
if metadata != expected_metadata:
    raise SystemExit("Design Arc agent metadata must match the canonical identity contract")
PY

printf '%s\n' 'PASS: Design Arc identity'
