#!/usr/bin/env python3
"""Mutation tests for Google Antigravity runtime and visualization contracts."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKER = REPO_ROOT / "scripts/check-antigravity-runtime-contracts.py"
ANTIGRAVITY_SKILL = REPO_ROOT / "skills/design-arc/SKILL.md"


MUTATIONS = {
    "Antigravity invocation": (
        "Use `/design-arc` to begin a Design Arc journey review.",
        "Use `$design-arc` to begin a Design Arc journey review.",
    ),
    "new setup confirmation": (
        "On new Google Antigravity setup, propose every missing preference and obtain explicit confirmation before creating `.gemini/design-arc.yaml`.",
        "On new Google Antigravity setup, create `.gemini/design-arc.yaml` before asking the user.",
    ),
    "existing Antigravity preferences": (
        "When `.gemini/design-arc.yaml` already exists, treat it as the Antigravity saved preference, do not offer a cross-runtime import, and never overwrite it from `.codex/design-arc.yaml` or `.claude/design-arc.yaml`.",
        "Prefer newer-looking Codex preferences over an existing Antigravity file.",
    ),
    "dual-source choice": (
        "If both source preference files exist, show the separately validated portable proposals and require the user to choose exactly one source before asking for import approval; never merge them.",
        "Merge Codex and Claude preferences when both source files exist.",
    ),
    "explicit import approval": (
        "Only after explicit import approval, copy the validated portable values from the chosen source into a new Antigravity preference file; do not move or rename the source file.",
        "Import cross-runtime preferences automatically whenever the Antigravity file is absent.",
    ),
    "source immutability": (
        "Treat every Codex and Claude preference file, active-review record, review artifact, graph, home record, reminder, task identity, and session context as read-only; verify the chosen source remains byte-for-byte unchanged.",
        "Normalize the source preference file after importing it.",
    ),
    "declined import": (
        "If the user declines import or declines to choose a source, leave all Codex and Claude state untouched and continue with a fresh Antigravity setup.",
        "If the user declines import, remove the source preference before fresh setup.",
    ),
    "malformed import": (
        "If either inspected source file is malformed or any portable value is invalid, import nothing from that source, report the invalid fields without exposing unrelated contents, and offer fresh Antigravity setup or the other separately valid source.",
        "Salvage valid-looking fields from malformed cross-runtime preferences.",
    ),
    "runtime provenance": (
        "Every Antigravity-created `.gemini/design-arc-active-review.json` and review artifact under `.gemini/design-arc/reviews/<review_id>/` records `runtime: antigravity` together with its pinned `workflow_version`; reject a `.gemini` record labelled `runtime: codex` and do not reinterpret it.",
        "Infer the active runtime from whichever review file is newest.",
    ),
    "Antigravity review storage": (
        "Google Antigravity stores preferences only at `.gemini/design-arc.yaml`, active-review identity only at `.gemini/design-arc-active-review.json`, and review artifacts only under `.gemini/design-arc/reviews/<review_id>/`.",
        "Google Antigravity stores new review artifacts under .codex for compatibility.",
    ),
    "cross-runtime review isolation": (
        "Never import, merge, migrate, resume, or continue an active review across runtimes; preference import is the only allowed cross-runtime copy.",
        "Merge Codex and Antigravity active reviews when their objectives match.",
    ),
    "no native-image claim": (
        "Never claim native image-generation capability in Google Antigravity.",
        "Google Antigravity can generate images natively.",
    ),
    "lightweight board default": (
        "For the default Google Antigravity route, prepare a lightweight static journey board with HTML/CSS, SVG, or specifications and avoid disposable application logic.",
        "Build a disposable application prototype by default.",
    ),
    "early Stitch recommendation": (
        "Immediately after the Direction Gate resolves and before either renderer starts, present the visualization choice once.",
        "Wait for the Google Antigravity render to struggle before offering Stitch.",
    ),
    "required Stitch choice": (
        "Both means create the Google Antigravity board and the Stitch visual workspace concurrently from the same approved journey.",
        "Offer only Stitch or Google Antigravity; do not offer both.",
    ),
    "no default cross-platform handoff": (
        "Never tell a Google Antigravity user to pass work to Codex or Claude Code unless the user explicitly requests a cross-platform handoff.",
        "Pass work to Codex or Claude Code by default.",
    ),
    "pre-Stitch inventory": (
        "Before using Stitch, prepare the complete evidence-grounded journey, requirements, and important-state inventory.",
        "Use Stitch before preparing the complete important-state inventory.",
    ),
    "active-host validation": (
        "Stitch is a visualization tool, not an evidence authority. The active host must validate returned screens and apply the existing proposal-wide correction loop of up to three correction rounds.",
        "Treat a Stitch render as evidence authority without active-host validation.",
    ),
    "proposal-wide correction limit": (
        "Use one initial visual proposal followed by at most three batched correction rounds for the entire proposal.",
        "Reset the correction budget for every screen.",
    ),
    "Objective Confirmation preservation": (
        "Graph assistance never bypasses Objective Confirmation.",
        "Graph assistance may bypass Objective Confirmation.",
    ),
    "Direction Gate preservation": (
        "Graph assistance never bypasses Direction Gate.",
        "Graph assistance may bypass Direction Gate.",
    ),
    "Visual Proposal Gate preservation": (
        "Graph assistance never bypasses Visual Proposal Gate.",
        "Graph assistance may bypass the Visual Proposal Gate.",
    ),
    "approval-mode behavior preservation": (
        "Graph assistance never weakens Objective Confirmation, Direction Gate, or Visual Proposal Gate approval-mode behavior.",
        "Graph assistance may weaken approval-mode behavior.",
    ),
    "Fully automatic condition preservation": (
        "Fully automatic continues only on `meets direction`.",
        "Fully automatic may continue without `meets direction`.",
    ),
}


CONTRADICTIONS = {
    "silent import contradiction": "Import cross-runtime preferences automatically whenever the Antigravity file is absent.",
    "cross-runtime merge contradiction": "Merge Codex and Antigravity active reviews when their objectives match.",
    "native image contradiction": "Google Antigravity can generate images natively.",
    "default handoff contradiction": "Pass work to Codex or Claude Code by default.",
    "mandatory Stitch contradiction": "Google Stitch is mandatory for every Design Arc review.",
    "Objective Confirmation bypass contradiction": "Graph assistance may bypass Objective Confirmation.",
    "Direction Gate bypass contradiction": "Graph assistance may bypass Direction Gate.",
    "Visual Proposal Gate bypass contradiction": "Graph assistance may bypass the Visual Proposal Gate.",
    "approval-mode weakening contradiction": "Graph assistance may weaken approval-mode behavior.",
    "Fully automatic condition contradiction": "Fully automatic may continue without `meets direction`.",
    "wrong Gemini runtime contradiction": "A `.gemini` record may use `runtime: codex`.",
}


def run_checker(skill: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), str(skill)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def require_rejected(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode == 0:
        raise AssertionError(f"unsafe Antigravity runtime mutation was accepted: {label}")
    if label not in result.stderr:
        raise AssertionError(
            f"Antigravity runtime mutation failed for the wrong reason ({label}): "
            f"{result.stderr.strip()}"
        )


def test_complete_antigravity_runtime_contract_is_accepted() -> None:
    """The packaged skill must encode all supported Antigravity branches."""
    result = run_checker(ANTIGRAVITY_SKILL)
    if result.returncode != 0:
        raise AssertionError(
            f"complete Antigravity runtime contract was rejected: {result.stderr.strip()}"
        )


def test_each_missing_or_unsafe_runtime_branch_is_rejected() -> None:
    """Every state, renderer, and gate branch must fail closed when mutated."""
    source = ANTIGRAVITY_SKILL.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="design-arc-antigravity-runtime-") as temporary:
        mutated = Path(temporary) / "SKILL.md"
        for label, (required, unsafe) in MUTATIONS.items():
            if required not in source:
                raise AssertionError(f"mutation fixture is absent from packaged skill: {label}")
            mutated.write_text(source.replace(required, unsafe, 1), encoding="utf-8")
            require_rejected(run_checker(mutated), label)


def test_explicitly_unsafe_contradictions_are_rejected() -> None:
    """Unsafe additions cannot coexist with otherwise complete instructions."""
    source = ANTIGRAVITY_SKILL.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="design-arc-antigravity-contradiction-") as temporary:
        mutated = Path(temporary) / "SKILL.md"
        for label, contradiction in CONTRADICTIONS.items():
            mutated.write_text(f"{source}\n\n{contradiction}\n", encoding="utf-8")
            require_rejected(run_checker(mutated), label)


def main() -> int:
    test_complete_antigravity_runtime_contract_is_accepted()
    print("PASS: complete Antigravity runtime contract")
    test_each_missing_or_unsafe_runtime_branch_is_rejected()
    print(f"PASS: {len(MUTATIONS)} missing or unsafe Antigravity mutations rejected")
    test_explicitly_unsafe_contradictions_are_rejected()
    print(f"PASS: {len(CONTRADICTIONS)} unsafe Antigravity contradictions rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
