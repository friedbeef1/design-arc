#!/usr/bin/env python3
"""Behavioral contracts for runtime-specific Design Arc visualization advice."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CODEX_SKILL = REPO_ROOT / "plugins/design-arc/skills/design-arc/SKILL.md"
CLAUDE_SKILL = REPO_ROOT / "claude-plugins/design-arc/skills/design-arc/SKILL.md"
ANTIGRAVITY_SKILL = REPO_ROOT / "skills/design-arc/SKILL.md"

ASSET_FIDELITY_CONTRACTS = (
    "The active AI coding platform must create a baseline design and a corresponding platform production asset set before design selection.",
    "When Stitch is invoked, preserve its returned design and exported Stitch production asset set as a separate provenance-bound set; never overwrite either set with the other.",
    "Record the selected design as `platform`, `stitch`, or `hybrid` and bind it to the matching asset set before implementation handoff.",
    "After separate implementation authorization, require the built application to import, reference, and render every required asset from the selected asset set.",
    "A `platform` selection requires platform-generated assets and rejects every Stitch asset.",
    "A `stitch` selection requires exported Stitch assets and rejects platform-generated substitutes.",
    "`Both` creates comparable proposals, not permission to mix their assets; mixing is allowed only after the user explicitly approves a `hybrid` design and identifies which screens, elements, and assets come from each set.",
    "Block implementation completion when any required selected asset is missing, unused, broken, unavailable, substituted, or absent from the running application.",
    "Keep controls, labels, navigation, state, status, focus behavior, and accessibility as semantic HTML or native UI; never flatten them into raster or vector artwork.",
    "When a required asset is raster and the active AI coding platform lacks native image-generation capability, record it as blocked and stop before design completion or implementation handoff; HTML/CSS, SVG, placeholders, and invented substitutes do not satisfy it.",
    "Return `matches approved proposal` only after both source integration and rendered fidelity pass: verify exact selected-asset imports and references, then inspect the running application at desktop and mobile viewports for correct loading and visual fidelity.",
)


def require(source: str, fragment: str, label: str) -> None:
    if fragment not in source:
        raise AssertionError(f"missing {label}: {fragment}")


def reject(source: str, fragment: str, label: str) -> None:
    if fragment in source:
        raise AssertionError(f"forbidden {label}: {fragment}")


def test_codex_visualization_contract() -> None:
    source = CODEX_SKILL.read_text(encoding="utf-8")
    require(source, "Create static screen images and complete journey boards directly in Codex by default.", "Codex default")
    require(source, "canvas-based editing, multiple visual alternatives, and sustained visual refinement", "Stitch benefits")
    require(source, "Recommend Stitch when those benefits materially help the review", "optional recommendation")
    require(source, "Stitch remains optional and separately authorized.", "optional authorization")
    require(source, "1. **Stitch** (recommended)", "recommended Stitch choice")
    require(source, "2. **Stay in Codex**", "Codex-only choice")
    require(source, "3. **Both**", "combined visualization choice")
    require(source, "Reply with `1`, `2`, or `3`.", "numeric visualization reply")
    require(
        source,
        "Both means create the Codex board and the Stitch visual workspace from the same approved journey.",
        "combined visualization behavior",
    )
    reject(source, "Stitch is mandatory", "mandatory Stitch")


def test_claude_visualization_contract() -> None:
    source = CLAUDE_SKILL.read_text(encoding="utf-8")
    require(source, "Never claim native image-generation capability in Claude Code.", "native-image disclaimer")
    require(source, "HTML/CSS, SVG, specifications, and lightweight static journey boards", "Claude outputs")
    require(source, "prepare a lightweight static journey board with HTML/CSS, SVG, or specifications", "Claude default route")
    require(source, "polished screen mockups, visual exploration, editable layouts, or continued visual refinement", "early Stitch triggers")
    require(source, "Do not withhold the Stitch recommendation when polished or editable mockups are requested.", "no withheld Stitch recommendation")
    require(source, "1. **Stitch** (recommended)", "recommended Stitch choice")
    require(source, "2. **Stay in Claude Code**", "Claude-only choice")
    require(source, "3. **Both**", "combined visualization choice")
    require(source, "Reply with `1`, `2`, or `3`.", "numeric visualization reply")
    require(
        source,
        "Both means create the Claude Code board and the Stitch visual workspace from the same approved journey.",
        "combined visualization behavior",
    )
    require(source, "Never tell a Claude Code user to pass work to Codex unless the user explicitly requests a cross-platform handoff.", "no default Codex handoff")
    reject(source, "Generate one complete static journey board in Claude Code by default", "false native default")
    reject(source, "Claude Code can generate images natively", "native image-generation claim")
    reject(source, "Generate static screen images directly in Claude Code", "native screen-generation claim")
    reject(source, "pass work to Codex by default", "default Codex handoff")


def test_shared_stitch_validation_contract() -> None:
    for path in (CODEX_SKILL, CLAUDE_SKILL, ANTIGRAVITY_SKILL):
        source = path.read_text(encoding="utf-8")
        require(source, "Before using Stitch, prepare the complete evidence-grounded journey, requirements, and important-state inventory.", "Stitch preparation")
        require(source, "Stitch is a visualization tool, not an evidence authority.", "Stitch evidence boundary")
        require(source, "up to three correction rounds", "three-round active-host validation")


def test_shared_selected_asset_fidelity_contract() -> None:
    for path in (CODEX_SKILL, CLAUDE_SKILL, ANTIGRAVITY_SKILL):
        source = path.read_text(encoding="utf-8")
        for fragment in ASSET_FIDELITY_CONTRACTS:
            require(source, fragment, f"selected-asset fidelity in {path}")


def main() -> int:
    test_codex_visualization_contract()
    print("PASS: Codex visualization contract")
    test_claude_visualization_contract()
    print("PASS: Claude visualization contract")
    test_shared_stitch_validation_contract()
    print("PASS: shared Stitch preparation and validation contract")
    test_shared_selected_asset_fidelity_contract()
    print("PASS: shared selected-design asset-fidelity contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
