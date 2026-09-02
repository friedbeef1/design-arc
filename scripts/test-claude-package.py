#!/usr/bin/env python3
"""Contract checks for the self-contained Claude Code Design Arc package."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_ROOT = REPO_ROOT / "claude-plugins/design-arc"
PLUGIN_MANIFEST = PACKAGE_ROOT / ".claude-plugin/plugin.json"
MARKETPLACE_MANIFEST = REPO_ROOT / ".claude-plugin/marketplace.json"
SKILL = PACKAGE_ROOT / "skills/design-arc/SKILL.md"
GRAPH_VALIDATOR = PACKAGE_ROOT / "skills/design-arc/scripts/validate-graph-record.py"
GRAPH_SCHEMA = PACKAGE_ROOT / "skills/design-arc/references/graph-record.schema.json"
VALID_GRAPH = REPO_ROOT / "scripts/fixtures/graph-records/valid.json"
COMPOSER = REPO_ROOT / "scripts/compose-design-arc-skills.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(*command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def require_success(result: subprocess.CompletedProcess[str], message: str) -> None:
    if result.returncode != 0:
        raise AssertionError(
            f"{message}: {result.stdout.strip()} {result.stderr.strip()}".strip()
        )


def test_claude_manifest_is_strictly_valid_and_skill_only() -> None:
    """A Claude install must expose one self-contained, skills-only plugin."""
    claude = shutil.which("claude")
    require(claude is not None, "Claude CLI is unavailable")
    result = run(claude, "plugin", "validate", "--strict", str(PACKAGE_ROOT))
    require_success(result, "Claude plugin manifest must pass strict validation")

    manifest = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
    require(manifest.get("name") == "design-arc", "Claude plugin name must be design-arc")
    require(manifest.get("version") == "1.5.4", "Claude plugin must ship 1.5.4")
    require(
        manifest.get("description") == "Alpha: outcome-led UI journey design for Claude Code.",
        "Claude plugin must identify itself as Alpha",
    )
    require(manifest.get("skills") == "./skills/", "Claude plugin must expose its skills directory")
    require(
        not ({"mcpServers", "agents", "hooks"} & set(manifest)),
        "Claude plugin must not declare MCP servers, agents, or hooks",
    )


def test_claude_marketplace_is_strictly_valid_and_routes_to_the_package() -> None:
    """The marketplace must route the Design Arc ID to its Claude package."""
    claude = shutil.which("claude")
    require(claude is not None, "Claude CLI is unavailable")
    result = run(claude, "plugin", "validate", "--strict", str(MARKETPLACE_MANIFEST))
    require_success(result, "Claude marketplace manifest must pass strict validation")

    marketplace = json.loads(MARKETPLACE_MANIFEST.read_text(encoding="utf-8"))
    require(marketplace.get("name") == "design-arc-marketplace", "Claude marketplace name drifted")
    require(
        marketplace.get("plugins") == [
            {
                "name": "design-arc",
                "source": "./claude-plugins/design-arc",
                "description": "Alpha: outcome-led UI journey design for Claude Code.",
                "version": "1.5.4",
                "author": {"name": "James Yeang"},
                "category": "productivity",
            }
        ],
        "Claude marketplace must expose exactly the Design Arc Claude package",
    )


def test_claude_skill_is_generated_with_local_graph_assets_and_entry_guidance() -> None:
    """A packaged Claude skill must retain its invocation contract and local validator."""
    result = run(sys.executable, str(COMPOSER), "--platform", "claude", "--check")
    require_success(result, "Claude generated skill must be current and contained")
    require(GRAPH_SCHEMA.is_file(), "Claude skill must bundle the graph schema")
    result = run(sys.executable, str(GRAPH_VALIDATOR), str(VALID_GRAPH), "project-alpha", "review-001")
    require_success(result, "Claude packaged graph validator must accept a valid graph")

    skill = SKILL.read_text(encoding="utf-8")
    for expected in (
        "argument-hint: \"[setup|mode|graph] [options]\"",
        "user-invocable: true",
        "/design-arc:design-arc setup",
        "/design-arc:design-arc mode",
        "/design-arc:design-arc graph",
        "natural-language request",
        "separately authorized",
    ):
        require(expected in skill, f"Claude skill is missing required guidance: {expected}")


def main() -> int:
    test_claude_manifest_is_strictly_valid_and_skill_only()
    print("PASS: Claude manifest is strictly valid and skills-only")
    test_claude_marketplace_is_strictly_valid_and_routes_to_the_package()
    print("PASS: Claude marketplace is strictly valid and routes to the package")
    test_claude_skill_is_generated_with_local_graph_assets_and_entry_guidance()
    print("PASS: Claude skill is generated with local graph assets and entry guidance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
