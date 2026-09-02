#!/usr/bin/env python3
"""Validate Google Antigravity runtime and visualization instruction contracts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SKILL = REPO_ROOT / "skills/design-arc/SKILL.md"


REQUIRED_CONTRACTS = {
    "Antigravity invocation": (
        "Use `/design-arc` to begin a Design Arc journey review.",
    ),
    "new setup confirmation": (
        "On new Google Antigravity setup, propose every missing preference and obtain explicit confirmation before creating `.gemini/design-arc.yaml`.",
    ),
    "existing Antigravity preferences": (
        "When `.gemini/design-arc.yaml` already exists, treat it as the Antigravity saved preference, do not offer a cross-runtime import, and never overwrite it from `.codex/design-arc.yaml` or `.claude/design-arc.yaml`.",
    ),
    "dual-source choice": (
        "If both source preference files exist, show the separately validated portable proposals and require the user to choose exactly one source before asking for import approval; never merge them.",
    ),
    "explicit import approval": (
        "Only after explicit import approval, copy the validated portable values from the chosen source into a new Antigravity preference file; do not move or rename the source file.",
    ),
    "source immutability": (
        "Treat every Codex and Claude preference file, active-review record, review artifact, graph, home record, reminder, task identity, and session context as read-only; verify the chosen source remains byte-for-byte unchanged.",
    ),
    "declined import": (
        "If the user declines import or declines to choose a source, leave all Codex and Claude state untouched and continue with a fresh Antigravity setup.",
    ),
    "malformed import": (
        "If either inspected source file is malformed or any portable value is invalid, import nothing from that source, report the invalid fields without exposing unrelated contents, and offer fresh Antigravity setup or the other separately valid source.",
    ),
    "runtime provenance": (
        "Every Antigravity-created `.gemini/design-arc-active-review.json` and review artifact under `.gemini/design-arc/reviews/<review_id>/` records `runtime: antigravity` together with its pinned `workflow_version`; reject a `.gemini` record labelled `runtime: codex` and do not reinterpret it.",
    ),
    "Antigravity review storage": (
        "Google Antigravity stores preferences only at `.gemini/design-arc.yaml`, active-review identity only at `.gemini/design-arc-active-review.json`, and review artifacts only under `.gemini/design-arc/reviews/<review_id>/`.",
    ),
    "cross-runtime review isolation": (
        "Never import, merge, migrate, resume, or continue an active review across runtimes; preference import is the only allowed cross-runtime copy.",
    ),
    "no native-image claim": (
        "Never claim native image-generation capability in Google Antigravity.",
    ),
    "lightweight board default": (
        "For the default Google Antigravity route, prepare a lightweight static journey board with HTML/CSS, SVG, or specifications and avoid disposable application logic.",
    ),
    "early Stitch recommendation": (
        "Immediately after the Direction Gate resolves and before either renderer starts, present the visualization choice once.",
    ),
    "required Stitch choice": (
        "1. **Both Google Antigravity and Stitch — recommended**",
        "2. **Google Antigravity only**",
        "3. **Stitch only**",
        "Reply with `1`, `2`, or `3`.",
        "Both means create the Google Antigravity board and the Stitch visual workspace concurrently from the same approved journey.",
    ),
    "no default cross-platform handoff": (
        "Never tell a Google Antigravity user to pass work to Codex or Claude Code unless the user explicitly requests a cross-platform handoff.",
    ),
    "pre-Stitch inventory": (
        "Before using Stitch, prepare the complete evidence-grounded journey, requirements, and important-state inventory.",
    ),
    "active-host validation": (
        "Stitch is a visualization tool, not an evidence authority. The active host must validate returned screens and apply the existing proposal-wide correction loop of up to three correction rounds.",
    ),
    "proposal-wide correction limit": (
        "Use one initial visual proposal followed by at most three batched correction rounds for the entire proposal.",
    ),
    "Objective Confirmation preservation": (
        "Graph assistance never bypasses Objective Confirmation.",
    ),
    "Direction Gate preservation": (
        "Graph assistance never bypasses Direction Gate.",
    ),
    "Visual Proposal Gate preservation": (
        "Graph assistance never bypasses Visual Proposal Gate.",
    ),
    "approval-mode behavior preservation": (
        "Graph assistance never weakens Objective Confirmation, Direction Gate, or Visual Proposal Gate approval-mode behavior.",
    ),
    "Fully automatic condition preservation": (
        "Fully automatic continues only on `meets direction`.",
    ),
}


FORBIDDEN_CONTRACTS = {
    "silent import contradiction": (
        "Import cross-runtime preferences automatically whenever the Antigravity file is absent.",
    ),
    "cross-runtime merge contradiction": (
        "Merge Codex and Antigravity active reviews when their objectives match.",
    ),
    "native image contradiction": (
        "Google Antigravity can generate images natively.",
    ),
    "default handoff contradiction": (
        "Pass work to Codex or Claude Code by default.",
    ),
    "mandatory Stitch contradiction": (
        "Google Stitch is mandatory for every Design Arc review.",
    ),
    "Objective Confirmation bypass contradiction": (
        "Graph assistance may bypass Objective Confirmation.",
    ),
    "Direction Gate bypass contradiction": (
        "Graph assistance may bypass Direction Gate.",
    ),
    "Visual Proposal Gate bypass contradiction": (
        "Graph assistance may bypass the Visual Proposal Gate.",
    ),
    "approval-mode weakening contradiction": (
        "Graph assistance may weaken approval-mode behavior.",
    ),
    "Fully automatic condition contradiction": (
        "Fully automatic may continue without `meets direction`.",
    ),
    "wrong Gemini runtime contradiction": (
        "A `.gemini` record may use `runtime: codex`.",
    ),
}


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def validate(skill: Path) -> list[str]:
    source = skill.read_text(encoding="utf-8")
    compact = normalized(source)
    failures: list[str] = []

    for label, clauses in REQUIRED_CONTRACTS.items():
        if any(normalized(clause) not in compact for clause in clauses):
            failures.append(label)

    for label, contradictions in FORBIDDEN_CONTRACTS.items():
        if any(normalized(contradiction) in compact for contradiction in contradictions):
            failures.append(label)
    return failures


def parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(description=__doc__)
    argument_parser.add_argument("skill", nargs="?", type=Path, default=DEFAULT_SKILL)
    return argument_parser


def main() -> int:
    args = parser().parse_args()
    try:
        failures = validate(args.skill)
    except OSError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    if failures:
        print(f"FAIL: {', '.join(failures)}", file=sys.stderr)
        return 1
    print("PASS: Antigravity setup, state, visualization, and gate contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
