#!/usr/bin/env python3
"""Contract tests for deterministic, self-contained Design Arc skills."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPOSER = REPO_ROOT / "scripts/compose-design-arc-skills.py"
CODEX_SKILL = REPO_ROOT / "plugins/design-arc/skills/design-arc/SKILL.md"
ANTIGRAVITY_SKILL = REPO_ROOT / "skills/design-arc/SKILL.md"
CLAUDE_SKILL = REPO_ROOT / "claude-plugins/design-arc/skills/design-arc/SKILL.md"
VERSION_FILE = REPO_ROOT / "shared/design-arc/VERSION"
CODEX_STITCH_ONBOARDING_HEADING = "## Codex-only external connection onboarding"

composer_spec = importlib.util.spec_from_file_location("design_arc_composer", COMPOSER)
if composer_spec is None or composer_spec.loader is None:
    raise RuntimeError("unable to load the Design Arc composer")
composer_module = importlib.util.module_from_spec(composer_spec)
composer_spec.loader.exec_module(composer_module)
external_references = composer_module.external_references


def run_composer(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(COMPOSER), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def require(result: subprocess.CompletedProcess[str], message: str) -> None:
    if result.returncode != 0:
        raise AssertionError(f"{message}: {result.stderr.strip()}")


def test_shared_source_composes_each_approved_skill() -> None:
    """A shared-methodology change must regenerate every exact adapter artifact."""
    for platform, approved_skill in {
        "codex": CODEX_SKILL,
        "claude": REPO_ROOT / "claude-plugins/design-arc/skills/design-arc/SKILL.md",
        "antigravity": ANTIGRAVITY_SKILL,
    }.items():
        with tempfile.TemporaryDirectory(prefix="design-arc-composition-") as temporary:
            output = Path(temporary) / "SKILL.md"
            result = run_composer("--platform", platform, "--output", str(output))
            require(result, f"{platform} composition failed")
            if output.read_bytes() != approved_skill.read_bytes():
                raise AssertionError(f"{platform} composition changed the approved skill artifact")


def test_composition_is_deterministic_and_targets_each_adapter_path() -> None:
    """A platform must always resolve to its one declared package destination."""
    for platform in ("codex", "claude", "antigravity"):
        with tempfile.TemporaryDirectory(prefix="design-arc-composition-") as temporary:
            first = Path(temporary) / "first.md"
            second = Path(temporary) / "second.md"
            for output in (first, second):
                result = run_composer("--platform", platform, "--output", str(output))
                require(result, f"{platform} composition failed")
            if first.read_bytes() != second.read_bytes():
                raise AssertionError(f"{platform} composition was not deterministic")

    for platform, expected in {
        "codex": "plugins/design-arc/skills/design-arc/SKILL.md",
        "claude": "claude-plugins/design-arc/skills/design-arc/SKILL.md",
        "antigravity": "skills/design-arc/SKILL.md",
    }.items():
        result = run_composer("--describe", "--platform", platform)
        require(result, f"{platform} composition description failed")
        description = json.loads(result.stdout)
        if description["output"] != expected:
            raise AssertionError(f"{platform} output path drifted from {expected}")
        if description["methodology"] != "shared/design-arc/methodology.md":
            raise AssertionError("platform composition bypassed the canonical methodology")


def test_antigravity_composes_directly_from_the_canonical_methodology() -> None:
    """Antigravity must not inherit Claude-specific composition behavior."""
    original_methodology_for = composer_module.methodology_for

    def reject_claude_dependency(platform: str) -> str:
        if platform == "claude":
            raise AssertionError("Antigravity composition delegated to the Claude adapter")
        return original_methodology_for(platform)

    composer_module.methodology_for = reject_claude_dependency
    try:
        antigravity_methodology = composer_module.methodology_for("antigravity")
    finally:
        composer_module.methodology_for = original_methodology_for

    if not antigravity_methodology.startswith("# Design Arc\n"):
        raise AssertionError("Antigravity did not compose from the canonical methodology")
    if ".gemini/design-arc.yaml" not in antigravity_methodology:
        raise AssertionError("Antigravity direct composition omitted its project state path")


def test_codex_only_stitch_onboarding_stays_platform_isolated() -> None:
    if CODEX_STITCH_ONBOARDING_HEADING not in CODEX_SKILL.read_text(encoding="utf-8"):
        raise AssertionError("Codex composition omitted its Stitch onboarding overlay")
    for path in (CLAUDE_SKILL, ANTIGRAVITY_SKILL):
        if CODEX_STITCH_ONBOARDING_HEADING in path.read_text(encoding="utf-8"):
            raise AssertionError(f"Codex Stitch onboarding leaked into {path}")


def test_check_enforces_version_parity_and_package_containment() -> None:
    """A release mismatch or a reference outside its package is unsafe to install."""
    for platform in ("codex", "claude", "antigravity"):
        result = run_composer("--check", "--platform", platform)
        require(result, f"{platform} composition check failed")
        report = json.loads(result.stdout)
        if report["version"] != "1.5.5" or VERSION_FILE.read_text(encoding="utf-8").strip() != "1.5.5":
            raise AssertionError(f"{platform} package version is not the shared 1.5.5 release")
        if report["external_references"]:
            raise AssertionError(f"{platform} skill escapes its package root: {report['external_references']}")


def test_package_check_rejects_markdown_links_that_escape_the_skill_root() -> None:
    """A packaged skill must not regain a shared-source dependency by a link."""
    with tempfile.TemporaryDirectory(prefix="design-arc-package-root-") as temporary:
        package_root = Path(temporary) / "plugin"
        package_root.mkdir()
        references = external_references(
            "Read the [shared methodology](../../../shared/design-arc/methodology.md).\n",
            package_root,
        )
        if references != ["../../../shared/design-arc/methodology.md"]:
            raise AssertionError("package containment check accepted an escaping Markdown link")


def main() -> int:
    test_shared_source_composes_each_approved_skill()
    print("PASS: shared methodology composes every approved adapter skill")
    test_composition_is_deterministic_and_targets_each_adapter_path()
    print("PASS: composition is deterministic with stable adapter paths")
    test_antigravity_composes_directly_from_the_canonical_methodology()
    print("PASS: Antigravity composes directly from the canonical methodology")
    test_codex_only_stitch_onboarding_stays_platform_isolated()
    print("PASS: Codex-only Stitch onboarding stays platform isolated")
    test_check_enforces_version_parity_and_package_containment()
    print("PASS: composition check enforces version parity and package containment")
    test_package_check_rejects_markdown_links_that_escape_the_skill_root()
    print("PASS: package containment rejects escaping Markdown links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
