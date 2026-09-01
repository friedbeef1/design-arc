#!/usr/bin/env python3
"""Contract checks for the self-contained Google Antigravity Design Arc package."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
EXTENSION_MANIFEST = REPO_ROOT / "gemini-extension.json"
SKILL = REPO_ROOT / "skills/design-arc/SKILL.md"
GRAPH_VALIDATOR = REPO_ROOT / "skills/design-arc/scripts/validate-graph-record.py"
GRAPH_SCHEMA = REPO_ROOT / "skills/design-arc/references/graph-record.schema.json"
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


def test_antigravity_manifest_is_a_root_skills_only_extension() -> None:
    """Antigravity installs one stable, root-contained Design Arc extension."""
    manifest = json.loads(EXTENSION_MANIFEST.read_text(encoding="utf-8"))
    require(manifest.get("name") == "design-arc", "Antigravity extension name must be design-arc")
    require(manifest.get("version") == "1.5.3", "Antigravity extension must ship 1.5.3")
    require(
        manifest.get("description") == "Alpha: outcome-led UI journey design for Google Antigravity.",
        "Antigravity extension description drifted",
    )
    require(
        not ({"agents", "hooks", "mcpServers"} & set(manifest)),
        "Antigravity extension must not declare agents, hooks, or MCP servers",
    )


def test_antigravity_skill_is_generated_and_self_contained() -> None:
    """The root package must compose its exact skill with local graph assets."""
    result = run(sys.executable, str(COMPOSER), "--platform", "antigravity", "--check")
    require_success(result, "Antigravity generated skill must be current and contained")
    require(GRAPH_SCHEMA.is_file(), "Antigravity skill must bundle the graph schema")
    result = run(sys.executable, str(GRAPH_VALIDATOR), str(VALID_GRAPH), "project-alpha", "review-001")
    require_success(result, "Antigravity packaged graph validator must accept a valid graph")

    skill = SKILL.read_text(encoding="utf-8")
    for expected in (
        "name: design-arc",
        "user-invocable: true",
        "Google Antigravity entry point",
        "`/design-arc`",
        "`.gemini/design-arc/reviews/<review_id>/`",
        "`runtime: antigravity`",
        "separately authorized",
    ):
        require(expected in skill, f"Antigravity skill is missing required guidance: {expected}")


def main() -> int:
    test_antigravity_manifest_is_a_root_skills_only_extension()
    print("PASS: Antigravity manifest is a root skills-only extension")
    test_antigravity_skill_is_generated_and_self_contained()
    print("PASS: Antigravity skill is generated and self-contained")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
