#!/bin/sh
# Exercise the documented two-plugin baseline to Design Arc migration in isolation.

set -eu

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(CDPATH= cd "$script_dir/.." && pwd)
codex_bin=${CODEX_BIN:-codex}
baseline_sha=babedca266da243326dc7ad60c22706b9cd0c422
task_temp_dir=$(mktemp -d "${TMPDIR:-/tmp}/design-arc-migration-smoke.XXXXXX")
baseline_checkout="$task_temp_dir/baseline"
current_checkout="$task_temp_dir/current"
codex_home="$task_temp_dir/codex-home"

cleanup() {
  [ -n "$task_temp_dir" ] && [ -d "$task_temp_dir" ] && rm -rf "$task_temp_dir"
}

fail() {
  printf '%s\n' "FAIL: $*" >&2
  exit 1
}

trap cleanup EXIT HUP INT TERM

command -v "$codex_bin" >/dev/null 2>&1 || fail "Codex CLI is unavailable: $codex_bin"
mkdir "$codex_home"
git clone --quiet --no-local "$repo_root" "$baseline_checkout"
git -C "$baseline_checkout" checkout --quiet --detach "$baseline_sha"
git clone --quiet --no-local "$repo_root" "$current_checkout"
git -C "$repo_root" diff --binary --no-ext-diff HEAD -- . > "$task_temp_dir/current-worktree.diff"
if [ -s "$task_temp_dir/current-worktree.diff" ]
then
  git -C "$current_checkout" apply "$task_temp_dir/current-worktree.diff"
fi

CODEX_HOME="$codex_home" "$codex_bin" --version > "$task_temp_dir/codex-version.txt"
CODEX_HOME="$codex_home" "$codex_bin" plugin marketplace add "$baseline_checkout" --json > "$task_temp_dir/legacy-marketplace-add.json"
CODEX_HOME="$codex_home" "$codex_bin" plugin add fb-ux@fb-ux-marketplace --json > "$task_temp_dir/fb-ux-add.json"
CODEX_HOME="$codex_home" "$codex_bin" plugin add apple-guidelines-stitch@fb-ux-marketplace --json > "$task_temp_dir/apple-guidelines-stitch-add.json"
CODEX_HOME="$codex_home" "$codex_bin" plugin list --available --json > "$task_temp_dir/before-migration.json"

CODEX_HOME="$codex_home" "$codex_bin" plugin remove fb-ux@fb-ux-marketplace --json > "$task_temp_dir/fb-ux-remove.json"
CODEX_HOME="$codex_home" "$codex_bin" plugin remove apple-guidelines-stitch@fb-ux-marketplace --json > "$task_temp_dir/apple-guidelines-stitch-remove.json"
CODEX_HOME="$codex_home" "$codex_bin" plugin marketplace remove fb-ux-marketplace --json > "$task_temp_dir/legacy-marketplace-remove.json"
CODEX_HOME="$codex_home" "$codex_bin" plugin marketplace add "$current_checkout" --json > "$task_temp_dir/design-arc-marketplace-add.json"
CODEX_HOME="$codex_home" "$codex_bin" plugin add design-arc@design-arc-marketplace --json > "$task_temp_dir/design-arc-add.json"
CODEX_HOME="$codex_home" "$codex_bin" plugin list --available --json > "$task_temp_dir/after-migration.json"
CODEX_HOME="$codex_home" "$codex_bin" plugin marketplace list --json > "$task_temp_dir/marketplaces-after.json"
CODEX_HOME="$codex_home" "$codex_bin" debug prompt-input 'Use $design-arc setup.' > "$task_temp_dir/prompt-input-after.json"

python3 - "$baseline_checkout" "$current_checkout" "$codex_home" "$task_temp_dir" "$baseline_sha" <<'PY'
import json
from pathlib import Path
import subprocess
import sys

baseline, current, codex_home, temporary_dir = (Path(path).resolve() for path in sys.argv[1:5])
expected_baseline = sys.argv[5]


def read_json(name):
    return json.loads((temporary_dir / name).read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise SystemExit(f"FAIL: {message}")


actual_baseline = subprocess.run(
    ["git", "-C", str(baseline), "rev-parse", "HEAD"],
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()
require(actual_baseline == expected_baseline, "migration fixture must start at the verified public baseline")
version = (temporary_dir / "codex-version.txt").read_text(encoding="utf-8").strip()
require(version.startswith("codex-cli "), "migration smoke must run the real Codex CLI")

before = read_json("before-migration.json")
before_installed = before.get("installed")
require(isinstance(before_installed, list) and len(before_installed) == 2, "baseline must install exactly two legacy plugins")
before_by_id = {plugin.get("pluginId"): plugin for plugin in before_installed}
legacy_ids = {
    "fb-ux@fb-ux-marketplace",
    "apple-guidelines-stitch@fb-ux-marketplace",
}
require(set(before_by_id) == legacy_ids, "baseline installed IDs must be the two legacy plugins")
require(all(plugin.get("enabled") is True for plugin in before_installed), "both baseline plugins must be enabled")
require(before.get("available") == [], "baseline marketplace must have no uninstalled plugin")

for filename, plugin_id in (
    ("fb-ux-add.json", "fb-ux@fb-ux-marketplace"),
    ("apple-guidelines-stitch-add.json", "apple-guidelines-stitch@fb-ux-marketplace"),
    ("fb-ux-remove.json", "fb-ux@fb-ux-marketplace"),
    ("apple-guidelines-stitch-remove.json", "apple-guidelines-stitch@fb-ux-marketplace"),
):
    require(read_json(filename).get("pluginId") == plugin_id, f"{filename} must report {plugin_id}")

legacy_marketplace_remove = read_json("legacy-marketplace-remove.json")
require(legacy_marketplace_remove.get("marketplaceName") == "fb-ux-marketplace", "migration must remove the legacy marketplace")
require(legacy_marketplace_remove.get("installedRoot") is None, "legacy marketplace removal must clear its installed root")

design_marketplace_add = read_json("design-arc-marketplace-add.json")
require(design_marketplace_add.get("marketplaceName") == "design-arc-marketplace", "migration must add the Design Arc marketplace")
require(Path(design_marketplace_add.get("installedRoot", "")).resolve() == current, "new marketplace must use the isolated current checkout")

design_add = read_json("design-arc-add.json")
require(design_add.get("pluginId") == "design-arc@design-arc-marketplace", "migration must install the canonical Design Arc plugin")
require(design_add.get("version") == "1.5.5", "migration must install Design Arc 1.5.5")
installed_path = Path(design_add.get("installedPath", "")).resolve()
require(installed_path.is_dir(), "migrated Design Arc cache must exist")
require(codex_home in installed_path.parents, "migrated plugin cache must stay in the isolated Codex home")

after = read_json("after-migration.json")
after_installed = after.get("installed")
require(isinstance(after_installed, list) and len(after_installed) == 1, "migration must leave exactly one installed plugin")
require(after_installed[0].get("pluginId") == "design-arc@design-arc-marketplace", "migration must leave only Design Arc")
require(after_installed[0].get("enabled") is True, "migrated Design Arc plugin must be enabled")
require(after.get("available") == [], "new marketplace must have no uninstalled plugin")

marketplaces_after = read_json("marketplaces-after.json")
configured_marketplaces = marketplaces_after.get("marketplaces")
require(isinstance(configured_marketplaces, list) and len(configured_marketplaces) == 1, "migration must leave exactly one configured marketplace")
require(configured_marketplaces[0].get("name") == "design-arc-marketplace", "only the Design Arc marketplace may remain configured")

config_text = (codex_home / "config.toml").read_text(encoding="utf-8")
require("fb-ux-marketplace" not in config_text, "legacy marketplace and plugin config must be removed")
require('plugins."design-arc@design-arc-marketplace"' in config_text, "Design Arc must be enabled in isolated config")
require('marketplaces.design-arc-marketplace' in config_text, "Design Arc marketplace must be configured")

legacy_cache_root = codex_home / "plugins/cache/fb-ux-marketplace"
legacy_cache_files = list(legacy_cache_root.rglob("*")) if legacy_cache_root.exists() else []
require(not any(path.is_file() for path in legacy_cache_files), "legacy plugin cache must contain no files after removal")
require(not (legacy_cache_root / "fb-ux").exists(), "fb-ux cache directory must be removed")
require(not (legacy_cache_root / "apple-guidelines-stitch").exists(), "apple-guidelines-stitch cache directory must be removed")

cached_skills = list((codex_home / "plugins/cache").glob("*/design-arc/*/skills/design-arc/SKILL.md"))
require(cached_skills == [installed_path / "skills/design-arc/SKILL.md"], "migration must leave one unique cached Design Arc skill")

prompt_items = read_json("prompt-input-after.json")
developer_text = "\n".join(
    content.get("text", "")
    for item in prompt_items
    if item.get("role") == "developer"
    for content in item.get("content", [])
    if content.get("type") == "input_text"
)
require(developer_text.count("- design-arc:design-arc:") == 1, "post-migration new task must expose exactly one Design Arc skill")
require("- fb-ux:fb-ux:" not in developer_text, "post-migration new task must not expose the legacy FB UX plugin skill")
require("- apple-guidelines-stitch:apple-guidelines-stitch:" not in developer_text, "post-migration new task must not expose the legacy guidelines plugin skill")

for legacy_id in legacy_ids:
    require(legacy_id not in json.dumps(after), f"post-migration active state must not contain {legacy_id}")

print(f"PASS: isolated two-plugin to Design Arc migration ({version})")
PY

printf '%s\n' 'PASS: isolated Design Arc plugin migration smoke'
