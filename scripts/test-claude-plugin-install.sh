#!/bin/sh
# Install and inspect the Claude Code package without touching the user's profile.

set -eu

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(CDPATH= cd "$script_dir/.." && pwd)
claude_bin=${CLAUDE_BIN:-claude}
task_temp_dir=$(mktemp -d "${TMPDIR:-/tmp}/design-arc-claude-install.XXXXXX")
claude_config_dir="$task_temp_dir/claude-config"
plugin_list="$task_temp_dir/plugin-list.json"
plugin_details="$task_temp_dir/plugin-details.txt"

cleanup() {
  [ -n "$task_temp_dir" ] && [ -d "$task_temp_dir" ] && rm -rf "$task_temp_dir"
}

fail() {
  printf '%s\n' "FAIL: $*" >&2
  exit 1
}

trap cleanup EXIT HUP INT TERM

command -v "$claude_bin" >/dev/null 2>&1 || fail 'Claude Code CLI is unavailable'
mkdir -p "$claude_config_dir"

CLAUDE_CONFIG_DIR="$claude_config_dir" "$claude_bin" plugin marketplace add "$repo_root" --scope user >/dev/null
CLAUDE_CONFIG_DIR="$claude_config_dir" "$claude_bin" plugin install design-arc@design-arc-marketplace --scope user >/dev/null
CLAUDE_CONFIG_DIR="$claude_config_dir" "$claude_bin" plugin list --json > "$plugin_list"
CLAUDE_CONFIG_DIR="$claude_config_dir" "$claude_bin" plugin details design-arc@design-arc-marketplace > "$plugin_details"

python3 - "$plugin_list" "$claude_config_dir" "$repo_root" <<'PY'
from pathlib import Path
import json
import sys

plugin_list = Path(sys.argv[1])
config_root = Path(sys.argv[2]).resolve()
repository_root = Path(sys.argv[3]).resolve()
installed = json.loads(plugin_list.read_text(encoding="utf-8"))
if len(installed) != 1:
    raise SystemExit(f"FAIL: isolated Claude profile has {len(installed)} installed plugins, expected 1")

plugin = installed[0]
expected = {
    "id": "design-arc@design-arc-marketplace",
    "version": "1.5.3",
    "scope": "user",
    "enabled": True,
}
for key, value in expected.items():
    if plugin.get(key) != value:
        raise SystemExit(f"FAIL: isolated Claude plugin {key} is {plugin.get(key)!r}, expected {value!r}")

install_path = Path(plugin.get("installPath", "")).resolve()
try:
    install_path.relative_to(config_root)
except ValueError:
    raise SystemExit(f"FAIL: Claude plugin escaped the task config: {install_path}")

installed_skill = install_path / "skills/design-arc/SKILL.md"
source_skill = repository_root / "claude-plugins/design-arc/skills/design-arc/SKILL.md"
if not installed_skill.is_file():
    raise SystemExit("FAIL: isolated Claude install did not cache the Design Arc skill")
if installed_skill.read_bytes() != source_skill.read_bytes():
    raise SystemExit("FAIL: isolated Claude install cached a different Design Arc skill")
PY

for expected_detail in \
  'design-arc 1.5.3' \
  'Skills (1)  design-arc' \
  'Agents (0)' \
  'Hooks (0)' \
  'MCP servers (0)' \
  'LSP servers (0)'
do
  grep -F "$expected_detail" "$plugin_details" >/dev/null || fail "Claude plugin load inventory omitted: $expected_detail"
done

printf '%s\n' 'PASS: isolated Claude Code Design Arc marketplace install and load smoke'
