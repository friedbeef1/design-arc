#!/bin/sh
# Verify a fresh isolated Codex task discovers exactly the Design Arc plugin and skill.

set -eu

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(CDPATH= cd "$script_dir/.." && pwd)
codex_bin=${CODEX_BIN:-codex}
task_temp_dir=$(mktemp -d "${TMPDIR:-/tmp}/design-arc-plugin-smoke.XXXXXX")
checkout_path="$task_temp_dir/checkout"
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
git clone --quiet --no-local "$repo_root" "$checkout_path"
git -C "$repo_root" diff --binary --no-ext-diff HEAD -- . > "$task_temp_dir/current-worktree.diff"
if [ -s "$task_temp_dir/current-worktree.diff" ]
then
  git -C "$checkout_path" apply "$task_temp_dir/current-worktree.diff"
fi

CODEX_HOME="$codex_home" "$codex_bin" --version > "$task_temp_dir/codex-version.txt"
CODEX_HOME="$codex_home" "$codex_bin" plugin marketplace add "$checkout_path" --json > "$task_temp_dir/marketplace-add.json"
CODEX_HOME="$codex_home" "$codex_bin" plugin list --available --json > "$task_temp_dir/available.json"
CODEX_HOME="$codex_home" "$codex_bin" plugin add design-arc@design-arc-marketplace --json > "$task_temp_dir/design-arc-add.json"
CODEX_HOME="$codex_home" "$codex_bin" plugin list --available --json > "$task_temp_dir/installed.json"
CODEX_HOME="$codex_home" "$codex_bin" debug prompt-input 'Use $design-arc to audit this journey.' > "$task_temp_dir/prompt-input.json"

python3 - "$checkout_path" "$codex_home" "$task_temp_dir" <<'PY'
import json
from pathlib import Path
import re
import subprocess
import sys

checkout, codex_home, temporary_dir = (Path(path).resolve() for path in sys.argv[1:])


def read_json(name):
    return json.loads((temporary_dir / name).read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise SystemExit(f"FAIL: {message}")


version = (temporary_dir / "codex-version.txt").read_text(encoding="utf-8").strip()
require(version.startswith("codex-cli "), "install smoke must run the real Codex CLI")

marketplace = json.loads((checkout / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
require(marketplace.get("name") == "design-arc-marketplace", "marketplace technical ID must be design-arc-marketplace")
require(marketplace.get("interface", {}).get("displayName") == "Design Arc", "marketplace display name must be Design Arc")
require(
    marketplace.get("plugins") == [
        {
            "name": "design-arc",
            "source": {"source": "local", "path": "./plugins/design-arc"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        }
    ],
    "fresh checkout must expose exactly one canonical marketplace entry",
)

marketplace_add = read_json("marketplace-add.json")
require(marketplace_add.get("marketplaceName") == "design-arc-marketplace", "Codex must add the Design Arc marketplace")
require(Path(marketplace_add.get("installedRoot", "")).resolve() == checkout, "Codex must add the isolated checkout")

available = read_json("available.json")
require(available.get("installed") == [], "isolated Codex home must begin without installed plugins")
available_plugins = available.get("available")
require(isinstance(available_plugins, list) and len(available_plugins) == 1, "fresh marketplace must expose exactly one available plugin")
available_plugin = available_plugins[0]
require(available_plugin.get("pluginId") == "design-arc@design-arc-marketplace", "available plugin ID must be canonical")
require(available_plugin.get("name") == "design-arc", "available plugin name must be design-arc")
require(available_plugin.get("enabled") is False, "available plugin must not be enabled before installation")
require(available_plugin.get("installPolicy") == "AVAILABLE", "available plugin must report AVAILABLE installation policy")
require(available_plugin.get("authPolicy") == "ON_INSTALL", "available plugin must report ON_INSTALL authentication policy")
require(
    Path(available_plugin.get("source", {}).get("path", "")).resolve() == (checkout / "plugins/design-arc").resolve(),
    "marketplace must resolve the isolated Design Arc source",
)

install = read_json("design-arc-add.json")
require(install.get("pluginId") == "design-arc@design-arc-marketplace", "Codex must install the canonical plugin")
require(install.get("name") == "design-arc", "install result must name design-arc")
require(install.get("version") == "1.5.5", "install result must report version 1.5.5")
installed_path = Path(install.get("installedPath", "")).resolve()
require(installed_path.is_dir(), "Codex must report an installed plugin cache directory")
require(codex_home in installed_path.parents, "installed plugin cache must stay inside the isolated Codex home")

installed = read_json("installed.json")
installed_plugins = installed.get("installed")
require(isinstance(installed_plugins, list) and len(installed_plugins) == 1, "isolated Codex home must contain exactly one installed plugin")
installed_plugin = installed_plugins[0]
require(installed_plugin.get("pluginId") == "design-arc@design-arc-marketplace", "only Design Arc may be installed")
require(installed_plugin.get("enabled") is True, "Design Arc must be enabled")
require(installed.get("available") == [], "no second marketplace plugin may remain available")

manifest = json.loads((installed_path / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
require(manifest.get("interface", {}).get("displayName") == "Design Arc", "installed plugin display name must be Design Arc")
require(manifest.get("skills") == "./skills/", "installed plugin must expose its skills directory")
require(
    manifest.get("mcpServers", {}).get("stitch", {}).get("env_http_headers") == {"X-Goog-Api-Key": "STITCH_API_KEY"},
    "installed Stitch connection must reference the user's secure STITCH_API_KEY environment value",
)
installed_skill = installed_path / "skills/design-arc/SKILL.md"
skill_text = installed_skill.read_text(encoding="utf-8")
require(skill_text.startswith("---\nname: design-arc\n"), "installed embedded skill must load with name: design-arc")
installed_validator = installed_skill.parent / "scripts/validate-graph-record.py"
require(installed_validator.is_file(), "installed embedded skill must bundle its graph validator")
installed_validation = subprocess.run(
    [
        sys.executable,
        str(installed_validator),
        str(checkout / "scripts/fixtures/graph-records/valid.json"),
        "project-alpha",
        "review-001",
    ],
    text=True,
    capture_output=True,
    check=False,
)
require(installed_validation.returncode == 0, "installed graph validator must accept a valid isolated fixture")
require("PASS: usable graph record" in installed_validation.stdout, "installed graph validator must execute from the plugin cache")

cached_skills = list((codex_home / "plugins/cache").glob("*/design-arc/*/skills/design-arc/SKILL.md"))
require(cached_skills == [installed_skill], "isolated cache must contain one unique Design Arc skill")
legacy_cached = list((codex_home / "plugins/cache").glob("*/fb-ux/*/skills/fb-ux/SKILL.md"))
legacy_cached += list((codex_home / "plugins/cache").glob("*/apple-guidelines-stitch/*/skills/apple-guidelines-stitch/SKILL.md"))
require(not legacy_cached, "isolated cache must contain no legacy plugin skill")

prompt_items = read_json("prompt-input.json")
require(isinstance(prompt_items, list), "Codex prompt input must be a JSON list")
developer_text = "\n".join(
    content.get("text", "")
    for item in prompt_items
    if item.get("role") == "developer"
    for content in item.get("content", [])
    if content.get("type") == "input_text"
)
def discovers_exact_skill(text, expected_path, description):
    prefix = "- design-arc:design-arc: "
    entries = [line for line in text.splitlines() if line.startswith(prefix)]
    if len(entries) != 1:
        return False
    match = re.fullmatch(re.escape(prefix + description) + r" \(file: (.+)\)", entries[0])
    if not match:
        return False
    path = Path(match.group(1))
    if not path.is_absolute():
        # Current Codex abbreviates cache paths using the declared skill-root table.
        roots = re.findall(r"^- `(r\d+)` = `([^`]+)`$", text, re.MULTILINE)
        matches = [root for alias, root in roots if alias == path.parts[0]]
        if len(matches) != 1 or not Path(matches[0]).is_absolute():
            return False
        if ".." in path.parts:
            return False
        path = Path(matches[0]).joinpath(*path.parts[1:])
    return path.resolve() == expected_path.resolve()


description = skill_text.splitlines()[2].removeprefix('description: ')
absolute_entry = f"- design-arc:design-arc: {description} (file: {installed_skill})"
alias_root = f"- `r42` = `{installed_skill.parent}`"
alias_entry = f"- design-arc:design-arc: {description} (file: r42/SKILL.md)"
# Regression and negative cases exercise the same resolver used for the real prompt.
require(discovers_exact_skill(absolute_entry, installed_skill, description), "absolute skill discovery regression")
require(discovers_exact_skill(alias_root + "\n" + alias_entry, installed_skill, description), "aliased skill discovery regression")
for invalid_prompt in (
    "",
    absolute_entry + "\n" + absolute_entry,
    alias_entry,
    alias_root + "\n" + alias_root + "\n" + alias_entry,
    alias_root + "\n" + alias_entry.replace("r42/", "r99/"),
    alias_root + "\n" + alias_entry.replace("SKILL.md", "wrong.md"),
    alias_root + "\n" + alias_entry.replace("r42/", "r42/../"),
    absolute_entry.replace(description, "wrong description"),
):
    require(not discovers_exact_skill(invalid_prompt, installed_skill, description), "invalid skill discovery must fail closed")
require(discovers_exact_skill(developer_text, installed_skill, description), "a new task must expose exactly one cached design-arc skill")
require("- fb-ux:fb-ux:" not in developer_text, "new-task plugin skills must not expose fb-ux")
require("- apple-guidelines-stitch:apple-guidelines-stitch:" not in developer_text, "new-task plugin skills must not expose apple-guidelines-stitch")

user_text = "\n".join(
    content.get("text", "")
    for item in prompt_items
    if item.get("role") == "user"
    for content in item.get("content", [])
    if content.get("type") == "input_text"
)
require("Use $design-arc to audit this journey." in user_text, "new-task proof must include the canonical invocation")

for legacy_id in ("fb-ux@fb-ux-marketplace", "apple-guidelines-stitch@fb-ux-marketplace"):
    require(legacy_id not in json.dumps(installed), f"active plugin state must not contain {legacy_id}")

print(f"PASS: isolated fresh install, bundled graph validation, and new-task skill discovery ({version})")
PY

printf '%s\n' 'PASS: isolated Design Arc plugin installation smoke'
